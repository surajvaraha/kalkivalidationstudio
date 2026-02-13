from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import shutil
import os
import uuid

from app.database import init_db, get_db
from app.models import ValidationTask, BatchRow, RejectionReasonMaster, StageReasonLink
from app.services import importer, exporter
from app.services import report_generator
from app.config import get_stages_for_task_type

# Initialize Database
init_db()

app = FastAPI()

# Mounts
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(ValidationTask).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tasks": tasks})

@app.get("/validate/{task_id}")
async def read_validation_ui(task_id: str, request: Request, db: Session = Depends(get_db)):
    task = db.query(ValidationTask).filter(ValidationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    stages = get_stages_for_task_type(task.task_type)
    return templates.TemplateResponse("validation.html", {"request": request, "task": task, "stages": stages})

# --- API ---

@app.post("/api/tasks")
async def create_task(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        temp_file = f"temp_{uuid.uuid4()}_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        task = importer.import_excel_task(temp_file, file.filename, db)
        os.remove(temp_file) # Cleanup
        
        return {"id": task.id, "filename": task.filename, "status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks/{task_id}/batches")
async def get_batches(task_id: str, page: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offset = page * limit
    batches = db.query(BatchRow).filter(BatchRow.task_id == task_id).offset(offset).limit(limit).all()
    
    # Return simple list of dicts (ensure no null for JSON fields so frontend doesn't throw)
    data = []
    for b in batches:
        status_val = b.status.value if hasattr(b.status, "value") else str(b.status)
        item = {
            "id": b.id,
            "row_index": b.row_index,
            "raw_data": b.raw_data if b.raw_data is not None else {},
            "validation_data": b.validation_data if b.validation_data is not None else {},
            "status": status_val
        }
        data.append(item)
        
    return {"data": data}

@app.put("/api/batches/{batch_id}")
async def update_batch(batch_id: int, payload: dict, db: Session = Depends(get_db)):
    batch = db.query(BatchRow).filter(BatchRow.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    # Payload expects: { "validation_data": {...}, "status": "VALIDATED" }
    if "validation_data" in payload:
        # Deep merge or replace? For simplicity, we merge top-level keys
        current_data = batch.validation_data or {}
        current_data.update(payload["validation_data"])
        batch.validation_data = current_data
        
        # Force SQLAlchemy to detect change in JSON field if needed (sometimes required)
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(batch, "validation_data")

    if "status" in payload:
        batch.status = payload["status"]
        
    db.commit()
    return {"status": "success"}

@app.get("/api/tasks/{task_id}/download")
async def download_task(task_id: str, db: Session = Depends(get_db)):
    try:
        # Ensure exports directory exists
        os.makedirs("exports", exist_ok=True)
        output_path = f"exports/validated_{task_id}.xlsx"
        exporter.export_task_excel(task_id, db, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=f"Validated_{task_id}.xlsx")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(ValidationTask).filter(ValidationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # ValidationTask cascade delete will handle batches if configured in models.py
    # checking models.py: batches = relationship("BatchRow", back_populates="task", cascade="all, delete-orphan")
    # So deleting task is enough.
    
    db.delete(task)
    db.commit()
    
    return {"status": "success", "id": task_id}

# --- Rejection Report API ---

@app.post("/api/tasks/{task_id}/rejection-report")
async def start_rejection_report(task_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Kick off background PDF generation for all rejected batches in this task."""
    task = db.query(ValidationTask).filter(ValidationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    job_id = str(uuid.uuid4())
    # Pass the DB session factory so the background thread creates its own session
    background_tasks.add_task(report_generator.generate_rejection_report, task_id, job_id, get_db)
    return {"job_id": job_id, "status": "started"}


@app.get("/api/tasks/{task_id}/rejection-report/status/{job_id}")
async def rejection_report_status(task_id: str, job_id: str):
    """Poll the progress of a rejection report generation job."""
    status = report_generator.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


@app.post("/api/tasks/{task_id}/rejection-report/cancel/{job_id}")
async def cancel_rejection_report(task_id: str, job_id: str):
    """Cancel a running rejection report generation job."""
    status = report_generator.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    report_generator.cancel_job(job_id)
    return {"status": "cancelling", "message": "Cancel signal sent"}


@app.get("/api/tasks/{task_id}/rejection-report/download/{job_id}")
async def download_rejection_report(task_id: str, job_id: str):
    """Download the generated ZIP once the job is done."""
    status = report_generator.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if status.get("status") != "done":
        raise HTTPException(status_code=400, detail="Report is not ready yet")

    file_path = status.get("file")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    filename = status.get("filename", "RejectionReports.zip")
    return FileResponse(file_path, media_type="application/zip", filename=filename)


# --- Rejection Reasons CRUD API ---

_STAGES = ["moisture", "start", "mid", "90", "end"]


@app.get("/api/rejection-reasons")
async def get_rejection_reasons(view: str | None = None, db: Session = Depends(get_db)):
    """Return rejection reasons. Default: grouped by stage for validation UI. ?view=master: full master list with stage assignments."""
    if view == "master":
        masters = db.query(RejectionReasonMaster).order_by(RejectionReasonMaster.id).all()
        return [
            {
                "id": m.id,
                "reason_text": m.reason_text,
                "stages": [link.stage for link in sorted(m.stage_links, key=lambda l: (_STAGES.index(l.stage) if l.stage in _STAGES else 999, l.display_order))],
            }
            for m in masters
        ]
    # Default: grouped by stage (for validation UI), ordered by display_order then master id (added order)
    links = (
        db.query(StageReasonLink, RejectionReasonMaster)
        .join(RejectionReasonMaster, StageReasonLink.master_id == RejectionReasonMaster.id)
        .order_by(StageReasonLink.stage, StageReasonLink.display_order, RejectionReasonMaster.id)
        .all()
    )
    grouped = {}
    for link, master in links:
        grouped.setdefault(link.stage, []).append({
            "id": master.id,
            "reason": master.reason_text,
            "display_order": link.display_order,
        })
    return grouped


@app.post("/api/rejection-reasons")
async def add_rejection_reason(payload: dict, db: Session = Depends(get_db)):
    """Create a new master reason, optionally assign to stages. stages: list of stage keys."""
    reason_text = payload.get("reason_text", payload.get("reason", "")).strip()
    if not reason_text:
        raise HTTPException(status_code=400, detail="reason_text is required")

    existing = db.query(RejectionReasonMaster).filter(RejectionReasonMaster.reason_text == reason_text).first()
    if existing:
        raise HTTPException(status_code=400, detail="Reason already exists")

    stages = payload.get("stages") or []
    master = RejectionReasonMaster(reason_text=reason_text)
    db.add(master)
    db.flush()
    for idx, stage in enumerate(stages):
        if stage in _STAGES:
            db.add(StageReasonLink(master_id=master.id, stage=stage, display_order=idx))
    db.commit()
    db.refresh(master)
    return {"id": master.id, "reason_text": master.reason_text, "stages": stages}


@app.put("/api/rejection-reasons/{reason_id}")
async def update_rejection_reason(reason_id: int, payload: dict, db: Session = Depends(get_db)):
    """Update reason text. Changes propagate to all stages."""
    master = db.query(RejectionReasonMaster).filter(RejectionReasonMaster.id == reason_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Reason not found")

    new_text = payload.get("reason_text", payload.get("reason", "")).strip()
    if not new_text:
        raise HTTPException(status_code=400, detail="reason_text is required")

    other = db.query(RejectionReasonMaster).filter(RejectionReasonMaster.reason_text == new_text, RejectionReasonMaster.id != reason_id).first()
    if other:
        raise HTTPException(status_code=400, detail="Another reason with this text already exists")

    master.reason_text = new_text
    db.commit()
    return {"id": master.id, "reason_text": master.reason_text}


@app.delete("/api/rejection-reasons/{reason_id}")
async def delete_rejection_reason(reason_id: int, db: Session = Depends(get_db)):
    """Delete a master reason and all stage links. Existing batch validation_data unchanged."""
    master = db.query(RejectionReasonMaster).filter(RejectionReasonMaster.id == reason_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Reason not found")
    db.delete(master)
    db.commit()
    return {"status": "success", "id": reason_id}


@app.put("/api/rejection-reasons/{reason_id}/stages")
async def toggle_stage_assignment(reason_id: int, payload: dict, db: Session = Depends(get_db)):
    """Toggle stage assignment. payload: { stage: string, enabled: boolean }."""
    stage = payload.get("stage", "").strip()
    enabled = payload.get("enabled", True)
    if stage not in _STAGES:
        raise HTTPException(status_code=400, detail="Invalid stage")

    master = db.query(RejectionReasonMaster).filter(RejectionReasonMaster.id == reason_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Reason not found")

    link = db.query(StageReasonLink).filter(StageReasonLink.master_id == reason_id, StageReasonLink.stage == stage).first()
    if enabled and not link:
        max_order = db.query(StageReasonLink).filter(StageReasonLink.stage == stage).count()
        db.add(StageReasonLink(master_id=reason_id, stage=stage, display_order=max_order))
        db.commit()
        return {"stage": stage, "enabled": True}
    if not enabled and link:
        db.delete(link)
        db.commit()
        return {"stage": stage, "enabled": False}
    return {"stage": stage, "enabled": enabled}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
