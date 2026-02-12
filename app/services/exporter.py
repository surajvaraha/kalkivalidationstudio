"""
Export validated task to Excel. Output = all input columns (preserved) + validation
columns (Status, Remark, Comment per stage). Column order matches the Kalki input
sheet when task type is KALKI. Geotag/Serial are not exported.
"""

from app.config import (
    VALIDATION_SCHEMA,
    get_stages_for_task_type,
)
import pandas as pd
from sqlalchemy.orm import Session
from app.models import ValidationTask, TaskType

# Exact column order from "Kalki Input Sheet for 11 Feb 2026.xlsx"
KALKI_INPUT_COLUMN_ORDER = [
    "Batch Kiln ID",
    "production_start_date",
    "production_time_date",
    "organization_id",
    "Partner Name",
    "Facility Name",
    "Kiln ID",
    "Kiln Name",
    "wood_moisture",
    "moisture_reading_1",
    "Wood Moisture Image 1",
    "moisture_reading_2",
    "Wood Moisture Image 2",
    "moisture_reading_3",
    "Wood Moisture Image 3",
    "moisture_reading_4",
    "Wood Moisture Image 4",
    "moisture_reading_5",
    "Wood Moisture Image 5",
    "Process Start (Image)",
    "90% Done (Image)",
    "calculated_volume",
    "Model Processed (Image)",
    "Process End (Image)",
    "Process Middle (Image)",
    "submission_datetime",
]


def export_task_excel(task_id: str, db: Session, output_path: str) -> str:
    """
    Reconstruct Excel from raw_data + validation_data.
    - All input columns are preserved.
    - Validation columns (Status, Remark, Comment per stage) are appended.
    """
    task = db.query(ValidationTask).filter(ValidationTask.id == task_id).first()
    if not task:
        raise ValueError("Task not found")

    stages_to_export = get_stages_for_task_type(task.task_type)
    schema_by_key = {s["key"]: s for s in VALIDATION_SCHEMA}
    is_kalki = task.task_type == TaskType.KALKI

    # Validation columns: Status, Reason, Comment only (no Geotag/Serial)
    validation_col_list = []
    for stage_key in stages_to_export:
        schema = schema_by_key.get(stage_key)
        if not schema:
            continue
        validation_col_list.append(schema["status_col"])
        validation_col_list.append(schema["reason_col"])
        validation_col_list.append(schema["comment_col"])

    rows = []
    for batch in task.batches:
        row_data = dict(batch.raw_data) if batch.raw_data else {}
        val_data = batch.validation_data or {}

        for stage_key in stages_to_export:
            schema = schema_by_key.get(stage_key)
            if not schema:
                continue
            info = val_data.get(stage_key, {})

            row_data[schema["status_col"]] = info.get("status", "")
            row_data[schema["reason_col"]] = info.get("reason", "")
            row_data[schema["comment_col"]] = info.get("comment", "")

        rows.append(row_data)

    df = pd.DataFrame(rows)

    if is_kalki and KALKI_INPUT_COLUMN_ORDER:
        # Output = input columns (exact order) + validation columns; exclude internal *_image keys
        input_cols = [c for c in KALKI_INPUT_COLUMN_ORDER if c in df.columns]
        val_cols = [c for c in validation_col_list if c in df.columns]
        df = df[input_cols + val_cols]
    elif is_kalki:
        # No template: input-like cols first, then validation; drop *_image
        drop = [c for c in df.columns if c.endswith("_image")]
        df = df[[c for c in df.columns if c not in drop]]

    df.to_excel(output_path, index=False)
    return output_path
