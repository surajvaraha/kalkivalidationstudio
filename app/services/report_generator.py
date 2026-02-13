"""
Rejection Report Generator — integrated into Validation Studio.

Reads validated batch data from the database, identifies rejected stages,
downloads validation images, and generates per-partner PDF rejection reports
bundled into a ZIP file.

Adapted from biocharrejectionreportgenerator/automation.py to work with the
studio's data model (BatchRow.raw_data + BatchRow.validation_data).
"""

import os
import re
import time
import zipfile
import concurrent.futures
import threading
from io import BytesIO

import requests as http_requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Image as RLImage, Spacer, PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from sqlalchemy.orm import Session

from app.models import ValidationTask, BatchRow, TaskType
from app.config import VALIDATION_SCHEMA, get_stages_for_task_type

# ──────────────────────────────────────────────────────────────────────────────
# Directories
# ──────────────────────────────────────────────────────────────────────────────
REPORTS_DIR = "generated_reports"
ZIPS_DIR = "report_zips"

# ──────────────────────────────────────────────────────────────────────────────
# In-memory job tracker (lightweight; no external deps required)
# ──────────────────────────────────────────────────────────────────────────────
_jobs: dict = {}
_jobs_lock = threading.Lock()


def _update_job(job_id: str, **kwargs):
    with _jobs_lock:
        if job_id not in _jobs:
            _jobs[job_id] = {}
        _jobs[job_id].update(kwargs)


def get_job_status(job_id: str) -> dict | None:
    with _jobs_lock:
        return _jobs.get(job_id, {}).copy() if job_id in _jobs else None


def cancel_job(job_id: str):
    """Mark a job as cancelled. The background worker checks this flag."""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["_cancel"] = True


def _is_cancelled(job_id: str) -> bool:
    with _jobs_lock:
        return _jobs.get(job_id, {}).get("_cancel", False)


# ──────────────────────────────────────────────────────────────────────────────
# Metadata extraction helpers
# ──────────────────────────────────────────────────────────────────────────────

# Maps (task_type) → dict of metadata keys → list of raw_data column candidates
META_COLUMNS = {
    TaskType.KALKI: {
        "partner":      ["Partner Name", "Partner_Name"],
        "inventoryId":  ["Batch Kiln ID", "Batch_Kiln_ID"],
        "date":         ["production_start_date", "Production_Start_Date"],
        "time":         ["production_time_date", "Production_Time_Date"],
        "submission":   ["submission_datetime", "Submission_Datetime"],
        "kilnId":       ["Kiln ID", "Kiln_ID"],
        "artisan":      ["Kiln Name", "Kiln_Name"],
        "slot":         ["Facility Name", "Facility_Name"],
    },
}

# Stage key → list of raw_data columns where the image URL might live
# (includes both original column names and the normalised *_image key from the importer)
STAGE_IMAGE_COLUMNS = {
    "moisture_1": ["moisture_1_image", "Wood Moisture Image 1"],
    "moisture_2": ["moisture_2_image", "Wood Moisture Image 2"],
    "moisture_3": ["moisture_3_image", "Wood Moisture Image 3"],
    "moisture_4": ["moisture_4_image", "Wood Moisture Image 4"],
    "moisture_5": ["moisture_5_image", "Wood Moisture Image 5"],
    "start":      ["start_image", "Process Start (Image)", "Process Start Image Link"],
    "mid":        ["mid_image", "Process Middle (Image)", "Process Middle Image Link"],
    "90":         ["90_image", "90% Done (Image)", "90% Done Image Link"],
    "end":        ["end_image", "Process End (Image)", "Process End Image Link"],
}

# Stage key → human-readable label for the PDF
STAGE_LABELS = {
    "moisture_1": "Wood Moisture 1",
    "moisture_2": "Wood Moisture 2",
    "moisture_3": "Wood Moisture 3",
    "moisture_4": "Wood Moisture 4",
    "moisture_5": "Wood Moisture 5",
    "start":      "Process Start",
    "mid":        "Process Middle",
    "90":         "90% Done",
    "end":        "Process End",
}


def _get_raw(raw: dict, *keys) -> str:
    """Return the first non-empty value from raw_data for any of the given keys."""
    for k in keys:
        v = raw.get(k)
        if v is not None and str(v).strip() not in ("", "nan", "None"):
            return str(v).strip()
    return ""


def _is_rejected(status: str, stage_key: str) -> bool:
    """Check if a validation status indicates rejection (unified for all stages)."""
    s = str(status).strip().lower()
    return s == "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# Image downloader (same as original)
# ──────────────────────────────────────────────────────────────────────────────

def _download_image(url: str) -> BytesIO | None:
    try:
        if not isinstance(url, str) or not url.startswith("http"):
            return None
        resp = http_requests.get(url, timeout=15)
        if resp.status_code == 200:
            return BytesIO(resp.content)
    except Exception as e:
        print(f"[ReportGen] Image download failed {url}: {e}")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# PDF builder (same layout as standalone tool)
# ──────────────────────────────────────────────────────────────────────────────

def _build_partner_pdf(partner_name: str, batches: list[dict], output_path: str) -> str | None:
    """Generate a single PDF for one partner containing all rejected batches."""

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30,
    )
    elements = []
    styles = getSampleStyleSheet()

    style_header_text = ParagraphStyle("HeaderVal", parent=styles["Normal"], fontSize=9, leading=11)
    style_header_lbl  = ParagraphStyle("HeaderLbl", parent=styles["Normal"], fontSize=9, leading=11, fontName="Helvetica-Bold")
    style_reason      = ParagraphStyle("Reason", parent=styles["Normal"], textColor=colors.red, fontSize=10, leading=12)
    style_stage       = ParagraphStyle("Stage", parent=styles["Normal"], textColor=colors.white, backColor=colors.darkgrey, fontSize=8, alignment=1, spaceBefore=4)

    # 1. Pre-download all images in parallel
    all_urls: set[str] = set()
    for batch in batches:
        for item in batch["images"]:
            url = item.get("image", "")
            if isinstance(url, str) and url.startswith("http"):
                all_urls.add(url)

    image_map: dict[str, BytesIO] = {}
    if all_urls:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            future_to_url = {pool.submit(_download_image, u): u for u in all_urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        image_map[url] = data
                except Exception:
                    pass

    # 2. Build PDF pages
    first_page = True
    for batch in batches:
        if not first_page:
            elements.append(PageBreak())
        first_page = False

        meta = batch["meta"]

        # Build production date/time from separate columns
        prod_date = meta.get("date", "")
        prod_time = meta.get("time", "")
        prod_str = f"{prod_date} {prod_time}".strip() or "--"

        # Build submission date/time — may be a single combined column (e.g. "2026-02-10 14:30:00")
        sub_raw = meta.get("submission", "")
        if sub_raw:
            parts = str(sub_raw).split("T") if "T" in str(sub_raw) else str(sub_raw).split(" ", 1)
            sub_date = parts[0] if parts else ""
            sub_time = parts[1].split(".")[0] if len(parts) > 1 else ""  # strip microseconds
            sub_str = f"{sub_date} {sub_time}".strip()
        else:
            sub_str = "--"

        header_data = [
            [
                Paragraph("Partner Name:", style_header_lbl),
                Paragraph(str(meta.get("partner", "")), style_header_text),
                Paragraph("Inventory/Batch ID:", style_header_lbl),
                Paragraph(str(meta.get("inventoryId", "")), style_header_text),
            ],
            [
                Paragraph("Production:", style_header_lbl),
                Paragraph(prod_str, style_header_text),
                Paragraph("Submitted:", style_header_lbl),
                Paragraph(sub_str, style_header_text),
            ],
            [
                Paragraph("Kiln ID:", style_header_lbl),
                Paragraph(str(meta.get("kilnId", "")), style_header_text),
                Paragraph("Artisan/Name:", style_header_lbl),
                Paragraph(str(meta.get("artisan", "")), style_header_text),
            ],
            [
                Paragraph("Slot/Facility:", style_header_lbl),
                Paragraph(str(meta.get("slot", "")), style_header_text),
                Paragraph("", style_header_lbl),
                Paragraph("", style_header_text),
            ],
        ]

        t_header = Table(header_data, colWidths=[1.2 * inch, 2.5 * inch, 1.2 * inch, 2.0 * inch])
        t_header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(Paragraph("Rejection Report", styles["Heading2"]))
        elements.append(t_header)
        elements.append(Spacer(1, 0.2 * inch))

        # Rejection image grid (2 columns)
        rejection_items = batch["images"]
        rejection_rows = []
        for i in range(0, len(rejection_items), 2):
            row_items = rejection_items[i:i + 2]
            row_cells = []

            for item in row_items:
                img_url = item.get("image", "")
                if img_url in image_map:
                    img_data = BytesIO(image_map[img_url].getvalue())
                    img_flowable = RLImage(img_data, width=3 * inch, height=2.2 * inch)
                    img_flowable.hAlign = "CENTER"
                elif not img_url:
                    img_flowable = Paragraph("[No Image Link]", styles["Normal"])
                else:
                    img_flowable = Paragraph("[Image Download Failed]", styles["Normal"])

                stage_para  = Paragraph(f"STAGE: {item['stage']}", style_stage)
                reason_para = Paragraph(f"Reason: {item['reason']}", style_reason)

                cell_table = Table(
                    [[img_flowable], [stage_para], [reason_para]],
                    colWidths=[3.1 * inch],
                )
                cell_table.setStyle(TableStyle([
                    ("BOX", (0, 0), (-1, -1), 1, colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]))
                row_cells.append(cell_table)

            if len(row_cells) < 2:
                row_cells.append(Spacer(1, 1))

            rejection_rows.append(row_cells)

        if rejection_rows:
            t_grid = Table(rejection_rows, colWidths=[3.4 * inch, 3.4 * inch])
            t_grid.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ]))
            elements.append(t_grid)
        else:
            elements.append(Paragraph(
                "This batch has rejections marked but no images were found.",
                styles["Normal"],
            ))

    try:
        doc.build(elements)
        return output_path
    except Exception as e:
        print(f"[ReportGen] PDF build failed for {partner_name}: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point — called from FastAPI background task
# ──────────────────────────────────────────────────────────────────────────────

def generate_rejection_report(task_id: str, job_id: str, db_factory):
    """
    Background worker that:
    1. Reads all batches for the task from the DB
    2. Collects rejected stages per partner
    3. Generates PDFs (one per partner)
    4. Zips them and updates the job status

    Parameters
    ----------
    task_id : str
        The ValidationTask UUID.
    job_id : str
        A unique job identifier for status tracking.
    db_factory : callable
        A callable that yields a new DB session (since background threads
        must not share the request-scoped session).
    """
    _update_job(job_id, status="processing", message="Starting report generation...", percent=0)

    try:
        # Get a fresh DB session for this background thread
        db: Session = next(db_factory())

        task = db.query(ValidationTask).filter(ValidationTask.id == task_id).first()
        if not task:
            _update_job(job_id, status="error", message="Task not found")
            return

        task_type = task.task_type
        stages = get_stages_for_task_type(task_type)
        meta_cols = META_COLUMNS.get(task_type, META_COLUMNS[TaskType.KALKI])

        batches = db.query(BatchRow).filter(BatchRow.task_id == task_id).all()
        _update_job(job_id, message=f"Processing {len(batches)} batches...", percent=2)

        if _is_cancelled(job_id):
            _update_job(job_id, status="cancelled", message="Cancelled by user.", percent=0)
            return

        # ── Collect rejections grouped by partner ────────────────────────
        partners: dict[str, list[dict]] = {}
        for batch in batches:
            raw = batch.raw_data or {}
            val = batch.validation_data or {}

            # Find rejected stages
            rejected_images = []
            for stage_key in stages:
                stage_val = val.get(stage_key, {})
                status = stage_val.get("status", "")
                if not _is_rejected(status, stage_key):
                    continue

                # Get image URL
                img_cols = STAGE_IMAGE_COLUMNS.get(stage_key, [])
                image_url = _get_raw(raw, *img_cols)

                # Get reason from validation_data
                reason = stage_val.get("reason", "") or "No Reason Provided"

                stage_label = STAGE_LABELS.get(stage_key, stage_key)
                rejected_images.append({
                    "stage": stage_label,
                    "image": image_url,
                    "reason": reason,
                })

            if not rejected_images:
                continue

            # Extract metadata
            partner_name = _get_raw(raw, *meta_cols["partner"]) or "Unknown Partner"

            batch_meta = {}
            for meta_key, col_candidates in meta_cols.items():
                batch_meta[meta_key] = _get_raw(raw, *col_candidates)

            if partner_name not in partners:
                partners[partner_name] = []
            partners[partner_name].append({"meta": batch_meta, "images": rejected_images})

        if not partners:
            _update_job(
                job_id, status="done", message="No rejections found — nothing to generate.",
                percent=100, file=None,
            )
            return

        _update_job(
            job_id,
            message=f"Found {len(partners)} partner(s) with rejections. Generating PDFs...",
            percent=5,
        )

        # ── Generate PDFs (parallel) ────────────────────────────────────
        if _is_cancelled(job_id):
            _update_job(job_id, status="cancelled", message="Cancelled by user.", percent=0)
            return

        os.makedirs(REPORTS_DIR, exist_ok=True)
        os.makedirs(ZIPS_DIR, exist_ok=True)

        total = len(partners)
        completed = 0
        start_time = time.time()
        generated_files: list[str] = []

        def _process_partner(item):
            p_name, p_batches = item
            safe_name = re.sub(r"[^a-zA-Z0-9]", "_", p_name)
            path = os.path.join(REPORTS_DIR, f"Report_{safe_name}.pdf")
            return _build_partner_pdf(p_name, p_batches, path)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            future_map = {pool.submit(_process_partner, item): item for item in partners.items()}
            for future in concurrent.futures.as_completed(future_map):
                # Check for cancellation between partner PDFs
                if _is_cancelled(job_id):
                    # Cancel remaining futures
                    for f in future_map:
                        f.cancel()
                    _update_job(job_id, status="cancelled",
                                message=f"Stopped. {completed}/{total} report(s) were generated before cancellation.",
                                percent=0)
                    return

                completed += 1
                result = future.result()
                if result:
                    generated_files.append(result)

                pct = 5 + int((completed / total) * 90)
                elapsed = time.time() - start_time
                eta = (elapsed / completed) * (total - completed) if completed else 0
                eta_str = f"{int(eta)}s" if eta < 60 else f"{int(eta // 60)}m {int(eta % 60)}s"
                _update_job(
                    job_id,
                    message=f"Generated {completed}/{total} reports (ETA: {eta_str})",
                    percent=pct,
                )

        if not generated_files:
            _update_job(job_id, status="done", message="Rejections found but PDF generation failed.", percent=100, file=None)
            return

        # ── ZIP all reports ─────────────────────────────────────────────
        _update_job(job_id, message="Packaging reports into ZIP...", percent=96)
        zip_name = f"RejectionReports_{task_id[:8]}.zip"
        zip_path = os.path.join(ZIPS_DIR, zip_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fpath in generated_files:
                zf.write(fpath, os.path.basename(fpath))

        _update_job(
            job_id, status="done",
            message=f"Done! {len(generated_files)} report(s) generated.",
            percent=100, file=zip_path, filename=zip_name,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        _update_job(job_id, status="error", message=f"Report generation failed: {str(e)}")
