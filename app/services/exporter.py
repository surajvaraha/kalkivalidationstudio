from app.config import VALIDATION_SCHEMA, STAGES
import pandas as pd
from sqlalchemy.orm import Session
from app.models import ValidationTask, TaskType

def export_task_excel(task_id: str, db: Session, output_path: str):
    """
    Reconstructs the Excel file from stored raw_data and validation_data.
    Adds necessary output columns based on STAGES from config.
    """
    task = db.query(ValidationTask).filter(ValidationTask.id == task_id).first()
    if not task:
        raise ValueError("Task not found")
        
    # Gather Data
    rows = []
    for batch in task.batches:
        # Start with raw data
        row_data = batch.raw_data.copy()
        
        # Merge validation data
        val_data = batch.validation_data or {}
        
        # Explicitly map validation data to columns using VALIDATION_SCHEMA
        for schema in VALIDATION_SCHEMA:
            stage_key = schema["key"]
            info = val_data.get(stage_key, {})
            
            status_col = schema["status_col"]
            reason_col = schema["reason_col"]
            comment_col = schema["comment_col"]

            # Map validation fields to exact Excel columns
            row_data[status_col] = info.get("status", "")
            row_data[reason_col] = info.get("reason", "")
            row_data[comment_col] = info.get("comment", "")
            
            # Normalize prefix for sub-check headers (e.g. 'start' -> 'Start')
            prefix = stage_key.capitalize()
            if stage_key == '90': prefix = '90_Percent' 

            # Sub-checks: Prefixed to avoid collision (these stay as helper columns)
            sub = info.get("sub_checks", {})
            row_data[f"{prefix}_Geotag"] = "Yes" if sub.get("geotag") else "No"
            row_data[f"{prefix}_Serial"] = "Yes" if sub.get("serial") else "No"

        rows.append(row_data)
        
    df = pd.DataFrame(rows)
    
    # MVP: Just write it out.
    df.to_excel(output_path, index=False)
    
    return output_path
