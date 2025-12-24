from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import shutil
import os
import uuid

from app.database import init_db, get_db
from app.models import ValidationTask, BatchRow
from app.services import importer, exporter

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
    return templates.TemplateResponse("validation.html", {"request": request, "task": task})

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
    
    # Return simple list of dicts
    data = []
    for b in batches:
        item = {
            "id": b.id,
            "row_index": b.row_index,
            "raw_data": b.raw_data,
            "validation_data": b.validation_data,
            "status": b.status
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
        output_path = f"validated_{task_id}.xlsx"
        exporter.export_task_excel(task_id, db, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=f"Validated_{task_id}.xlsx")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
