# Biochar Validation Studio - Developer README

Biochar Validation Studio is a specialized desktop-style web application designed for high-efficiency validation of Biochar production batches. It streamlines the process of auditing production images (Start, Mid, End, etc.) and capturing SOP-compliant validation decisions.

## Tech Stack
- **Backend**: Python 3.9+, FastAPI, SQLAlchemy (SQLite)
- **Data Processing**: Pandas, OpenPyXL
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS (CDN)
- **Layout**: Custom 3-panel resizable layout with split handles.

## Project Structure
```bash
.
├── app/
│   ├── main.py            # FastAPI entry point & API routes
│   ├── models.py          # SQLAlchemy Database Models (Task, Batch)
│   ├── database.py        # SQLite configuration
│   ├── config.py          # Validation schemas, SOP reasons, and stage definitions
│   ├── services/
│   │   ├── importer.py    # Excel parsing and data "hydration"
│   │   └── exporter.py    # Validation data flattening and Excel generation
│   └── templates/
│       ├── dashboard.html  # Task management UI
│       └── validation.html # High-efficiency 3-panel validation UI
├── run_tool.command       # Automated setup & launch script (macOS/Linux)
├── run_tool.bat           # Automated setup & launch script (Windows)
└── biochar.db             # Local SQLite database
```

## Key Services

### Importer (`app/services/importer.py`)
- Automatically detects **Kalki** vs **Looker** from column names (`batch_kiln_id` / `inventory id`).
- **Fuzzy image mapping**: Maps image columns (e.g. `Wood Moisture Image 1`, `Process Start (Image)`) to normalised keys so all stage images load in the validation UI.
- Handles **datetime and numpy types** so Excel dates/times and numeric columns are stored safely in JSON.
- **Supported input**: Aligned with Kalki input sheets (e.g. `Kalki Input Sheet for 11 Feb 2026.xlsx`): `Batch Kiln ID`, `production_start_date`, `production_time_date`, `wood_moisture`, `moisture_reading_1`–`5`, `Wood Moisture Image 1`–`5`, `Process Start (Image)`, `Process Middle (Image)`, `90% Done (Image)`, `Process End (Image)`, `calculated_volume`, `Model Processed (Image)`, `submission_datetime`, etc.

### Exporter (`app/services/exporter.py`)
- **Output = input columns + validation columns.** All original columns are preserved; then Status, Remark, Comment, Geotag, Serial per stage are appended so the sheet clearly shows user responses.
- For **Kalki** tasks, column order matches the official input sheet; validation columns use clear names (e.g. `Moisture 1 Status`, `Process Start Remark`, `Process End Geotag`).

## Development Setup

1. **Environment**:
   ```bash
    - **macOS/Linux**: `source venv/bin/activate`
    - **Windows**: `venv\Scripts\activate`
    pip install -r requirements.txt
   ```

2. **Run Dev Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Database Migration**:
   Models are automatically created on startup via `Base.metadata.create_all(engine)`.

## Validation Schema (`app/config.py`)
Central configuration for all validation logic. To add a new stage or modify rejection reasons, update the `VALIDATION_SCHEMA` and `GENERAL_REJECTION_REASONS` lists in this file.

## Troubleshooting

### macOS Security Warning
If you see an error like "Apple could not verify 'run_tool.sh' is free of malware" when running the script:

1. **Via Terminal (Recommended)**:
   Run this command in the project directory:
   ```bash
   xattr -d com.apple.quarantine run_tool.sh
   ```

2. **Via Finder**:
   - Right-click (or Control-click) `run_tool.sh` in Finder.
   - Select **Open**.
   - In the dialog that appears, click **Open**.

### Windows Security Warning (SmartScreen)
If you see "Windows protected your PC" when running `run_tool.bat`:
1. Click **More info**.
2. Click **Run anyway**.
