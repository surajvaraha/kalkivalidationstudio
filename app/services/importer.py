import pandas as pd
import uuid
from sqlalchemy.orm import Session
from app.config import VALIDATION_SCHEMA, STAGES
from app.models import TaskType, TaskStatus, ValidationTask, BatchRow
import json

def determine_task_type(columns):
    """
    Heuristic to determine if the sheet is Kalki or Looker based on columns.
    """
    col_str = " ".join(columns).lower()
    
    if "batch_kiln_id" in col_str or "batch kiln id" in col_str:
        return TaskType.KALKI
    elif "inventory id" in col_str or "artisan pro" in col_str:
        return TaskType.LOOKER
    return TaskType.UNKNOWN

def import_excel_task(file_path: str, filename: str, db: Session):
    """
    Reads an Excel file, creates a ValidationTask, and populates BatchRows.
    """
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read Excel: {e}")
        
    # Nano-fix for NaNs
    df = df.fillna("")
    
    # Determine Type
    columns = df.columns.tolist()
    task_type = determine_task_type(columns)
    
    # Create Task
    task_id = str(uuid.uuid4())
    new_task = ValidationTask(
        id=task_id,
        filename=filename,
        task_type=task_type,
        status=TaskStatus.PENDING
    )
    db.add(new_task)
    db.flush()
    
    # Create Batch Rows
    batch_rows = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        
        # Normalize row_dict: Fuzzy Image Search based on Schema
        for schema in VALIDATION_SCHEMA:
            target_key = f"{schema['key']}_image"
            # If the target image key isn't there, search for it
            if target_key not in row_dict or not row_dict[target_key]:
                for pattern in schema['image_patterns']:
                    if pattern in row_dict and row_dict[pattern]:
                        row_dict[target_key] = row_dict[pattern]
                        break

        # Serialize specific types
        for k, v in row_dict.items():
            if pd.isna(v):
                row_dict[k] = ""
            elif isinstance(v, (pd.Timestamp, pd.Timedelta)):
                row_dict[k] = str(v)

        batch_row = BatchRow(
            task_id=task_id,
            row_index=idx,
            raw_data=row_dict,
            validation_data=reconstruct_validation_data(row_dict),
            status="IN_PROGRESS" if has_validation_data(row_dict) else "PENDING"
        )
        batch_rows.append(batch_row)
        
    db.add_all(batch_rows)
    db.commit()
    return new_task

def has_validation_data(row):
    return any("_status" in k.lower() for k in row.keys() if row[k])

def reconstruct_validation_data(row):
    """
    Reverse engineering the flat excel columns back to nested validation_data.
    Supports both global keys and stage-prefixed keys.
    """
    val_data = {}
    
    for stage in STAGES:
        # Check for {stage}_status or {prefix}_Status
        # We try capitalized and lower case because users/exporters might vary
        prefix = stage.capitalize()
        if stage == '90': prefix = '90_Percent'

        status = row.get(f"{stage}_status") or row.get(f"{prefix}_Status")
        if status:
            if stage not in val_data: val_data[stage] = {}
            val_data[stage]['status'] = status
            val_data[stage]['reason'] = row.get(f"{stage}_reason") or row.get(f"{prefix}_Reason", "")
            val_data[stage]['comment'] = row.get(f"{stage}_comment") or row.get(f"{prefix}_Comment", "")
            
            # Sub checks (Geotag, Serial) - Prefer prefixed keys for robustness
            sub_checks = {}
            
            geo = row.get(f"{stage}_geotag") or row.get(f"{prefix}_Geotag") or row.get("geotag")
            ser = row.get(f"{stage}_serial") or row.get(f"{prefix}_Serial") or row.get("serial")
            
            if geo is not None:
                sub_checks['geotag'] = str(geo).lower() in ['true', 'yes', '1']
            if ser is not None:
                sub_checks['serial'] = str(ser).lower() in ['true', 'yes', '1']
            
            if sub_checks:
                val_data[stage]['sub_checks'] = sub_checks

    return val_data
