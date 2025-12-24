
import pandas as pd
import json

def parse_excel(file_path):
    """
    Reads the Excel file.
    Assumes 'Validated Data' schema if present, else tries to map 'Raw Data'.
    Returns:
        dict: {
            "json": [List of Dicts for UI],
            "columns": [List of Column Names],
            "df": pd.DataFrame (The actual dataframe object)
        }
    """
    xl = pd.ExcelFile(file_path)
    
    # Heuristic: Check for "Validated Data" sheet first
    if "Validated Data" in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name="Validated Data")
    elif "18 Dec" in xl.sheet_names:
         # Fallback to Raw Data sheet
        df = pd.read_excel(file_path, sheet_name="18 Dec")
        df = normalize_raw_data(df)
    else:
        # Just take the first sheet and hope for the best, or try to normalize
        df = pd.read_excel(file_path, sheet_name=0)
        df = normalize_raw_data(df) # Attempt normalization on unknown sheets too
    
    # Fill generic NaNs
    df = df.fillna("")
    
    # Convert to Records
    records = df.to_dict(orient="records")
    
    return {
        "json": records,
        "columns": df.columns.tolist(),
        "df": df
    }

def normalize_raw_data(df):
    """
    Maps 'Raw Data' columns to the 'Validated Data' schema.
    Adds missing validation columns.
    """
    # 1. Rename Columns
    column_map = {
        "Batch Kiln ID": "Batch_Kiln_ID", 
        "Wood Moisture (Image)": "Wood Moisture Image Link",
        "Process Start (Image)": "Process Start Image Link",
        "Process Middle (Image)": "Process Middle Image Link",
        "90% Done (Image)": "90% Done Image Link",
        "Process End (Image)": "Process End Image Link"
    }
    df = df.rename(columns=column_map)
    
    # 2. Add Missing Validation Columns (if they don't exist)
    required_cols = [
        "Moisture is within limit", "Moisture Rejected remarks", "Wood Moisture Comments",
        "1.Process Start (Image)_Status", "1.Process Start (Image)_Status Remark", "1.Process Start Comments",
        "2.Process Middle (Image)_Status", "2.Process Middle (Image)_Status Remark", "2.Process Middle Comments",
        "3.90% (Image)_Status", "3.90% (Image)_Status Remark", "3.90% Comments",
        "4.Process End (Image)_Status", "4.Process End (Image)_Status Remark", "4.Process End Comments"
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = "" # Initialize empty
    return df

def update_dataframe(df, update_data):
    """
    Updates the in-memory dataframe based on UI input.
    update_data expected format: { "Batch_Kiln_ID": 123, "updates": { "ColName": "Value" } }
    """
    batch_id = update_data.get("Batch_Kiln_ID")
    updates = update_data.get("updates")
    
    if batch_id is None or updates is None:
        return
        
    # Find the row index. Assuming Batch_Kiln_ID is unique.
    # Note: Column name might vary ('Batch_Kiln_ID' vs 'Batch Kiln ID'). Normalize?
    # For now, simplistic filtering.
    
    # Try different ID column variations
    id_col = "Batch_Kiln_ID"
    if id_col not in df.columns:
        if "Batch Kiln ID" in df.columns:
            id_col = "Batch Kiln ID"
        else:
            # Fallback: Use index if passed? Risk of misalignment.
            pass
            
    # Update logic
    # df.loc[df[id_col] == batch_id, col] = value
    for col, val in updates.items():
        if col in df.columns:
             df.loc[df[id_col] == batch_id, col] = val

def save_excel(df, output_path):
    """
    Writes the dataframe to an Excel file.
    To Do: Re-integrate Data Validation dropdowns using openpyxl.
    """
    # For MVP, just dump the data
    df.to_excel(output_path, index=False, sheet_name="Validated Data")
