import re
import math
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, date, time as dt_time
from sqlalchemy.orm import Session
from app.config import VALIDATION_SCHEMA, STAGES
from app.models import TaskType, TaskStatus, ValidationTask, BatchRow


# ─── JSON Safety ────────────────────────────────────────────────────────────

def _make_json_safe(obj):
    """
    Recursively convert any non-JSON-serializable Python/Pandas/NumPy value
    so the dict can be stored in an SQLite JSON column without errors.
    """
    if obj is None:
        return ""

    # float NaN / Inf
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return ""
        return obj

    # Python stdlib date/time types
    if isinstance(obj, (datetime, date, dt_time)):
        return str(obj)

    # Pandas Timestamp / Timedelta / NaT
    if isinstance(obj, pd.Timestamp):
        return str(obj) if not pd.isna(obj) else ""
    if isinstance(obj, pd.Timedelta):
        return str(obj)
    if obj is pd.NaT:
        return ""

    # NumPy scalars (np.int64, np.float64, np.bool_, etc.)
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        val = obj.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return ""
        return val

    # Containers
    if isinstance(obj, dict):
        return {str(k): _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(v) for v in obj]

    return obj


# ─── Task Type Detection ───────────────────────────────────────────────────

def determine_task_type(columns):
    """Detect Kalki vs Looker from column names."""
    col_str = " ".join(str(c) for c in columns).lower()
    if "batch_kiln_id" in col_str or "batch kiln id" in col_str:
        return TaskType.KALKI
    if "inventory id" in col_str or "artisan pro" in col_str:
        return TaskType.LOOKER
    return TaskType.UNKNOWN


# ─── Main Import ───────────────────────────────────────────────────────────

def import_excel_task(file_path: str, filename: str, db: Session):
    """Read an Excel file, create a ValidationTask, and populate BatchRows."""
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read Excel: {e}")

    # Normalize column whitespace (e.g. "3.90%  (Image)_Status" → "3.90% (Image)_Status")
    df.columns = [re.sub(r"\s+", " ", str(c).strip()) for c in df.columns]

    # Determine type
    columns = df.columns.tolist()
    task_type = determine_task_type(columns)

    # Create task
    task_id = str(uuid.uuid4())
    new_task = ValidationTask(
        id=task_id,
        filename=filename,
        task_type=task_type,
        status=TaskStatus.PENDING,
    )
    db.add(new_task)
    db.flush()

    # Build schema lookup for image normalisation
    schema_map = {s["key"]: s for s in VALIDATION_SCHEMA}

    batch_rows = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()

        # Fuzzy image mapping: for each schema stage, copy the first matching
        # image column to a normalised key like "moisture_1_image"
        for schema in VALIDATION_SCHEMA:
            target_key = f"{schema['key']}_image"
            if target_key not in row_dict or not row_dict.get(target_key):
                for pattern in schema["image_patterns"]:
                    val = row_dict.get(pattern)
                    if val is not None and val != "" and not (isinstance(val, float) and math.isnan(val)):
                        row_dict[target_key] = val
                        break

        # Make everything JSON-safe (datetime.time, numpy int64, NaN, etc.)
        raw_data = _make_json_safe(row_dict)

        # Reconstruct any existing validation data from flat columns
        validation_data = _make_json_safe(_reconstruct_validation(row_dict))

        batch_row = BatchRow(
            task_id=task_id,
            row_index=idx,
            raw_data=raw_data,
            validation_data=validation_data,
            status="IN_PROGRESS" if _has_validation_cols(row_dict) else "PENDING",
        )
        batch_rows.append(batch_row)

    db.add_all(batch_rows)
    db.commit()
    return new_task


# ─── Helpers ────────────────────────────────────────────────────────────────

def _has_validation_cols(row):
    """True if the row already has any *_status-ish column with a value."""
    for k, v in row.items():
        if v and ("status" in str(k).lower()):
            return True
    return False


def _reconstruct_validation(row):
    """
    Reverse-engineer flat Excel validation columns back into nested
    validation_data dict.  Handles both old template columns and new ones.
    """
    val_data = {}
    schema_map = {s["key"]: s for s in VALIDATION_SCHEMA}

    for stage in STAGES:
        schema = schema_map.get(stage)
        if not schema:
            continue

        # Try schema column names
        status = _first_val(row, schema["status_col"])
        reason = _first_val(row, schema["reason_col"]) or ""
        comment = _first_val(row, schema["comment_col"]) or ""

        if not status:
            continue

        entry = {"status": status, "reason": reason, "comment": comment}
        val_data[stage] = entry

    return val_data


def _first_val(row, *keys):
    """Return the first non-empty value from row for any of the given keys."""
    for k in keys:
        v = row.get(k)
        if v is not None and v != "":
            try:
                if isinstance(v, float) and math.isnan(v):
                    continue
            except (TypeError, ValueError):
                pass
            return v
    return None
