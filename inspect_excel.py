import pandas as pd
import openpyxl

file_path = 'Kalki Biochar Validations Sheet.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheet names: {xl.sheet_names}")

    for sheet_name in xl.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
        print("Columns:")
        print(df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Check for data validation (dropdowns) - requires openpyxl directly
        wb = openpyxl.load_workbook(file_path)
        ws = wb[sheet_name]
        print(f"\nData Validations in {sheet_name}:")
        for validation in ws.data_validations.dataValidation:
            print(f"Range: {validation.sqref}, Type: {validation.type}, Formula1: {validation.formula1}")

except Exception as e:
    print(f"Error reading excel: {e}")
