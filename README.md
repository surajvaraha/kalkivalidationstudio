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
├── run_tool.sh            # Automated setup and launch script
└── biochar.db             # Local SQLite database
```

## Key Services

### Importer (`app/services/importer.py`)
- Automatically detects if an uploaded file is **Kalki** or **Looker** format.
- Uses **Fuzzy Image Mapping** to find image URLs even if column names vary.
- Reconstructs nested validation states from flattened Excel columns for existing/partially validated sheets.

### Exporter (`app/services/exporter.py`)
- Flattens the nested validation database into a flat Excel format.
- Uses **Stage Prefixing** (e.g., `Start_Status`, `Mid_Geotag`) to prevent column collisions across different validation stages.

## Development Setup

1. **Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn sqlalchemy pandas openpyxl jinja2 python-multipart
   ```

2. **Run Dev Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Database Migration**:
   Models are automatically created on startup via `Base.metadata.create_all(engine)`.

## Validation Schema (`app/config.py`)
Central configuration for all validation logic. To add a new stage or modify rejection reasons, update the `VALIDATION_SCHEMA` and `GENERAL_REJECTION_REASONS` lists in this file.
