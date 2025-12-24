# Biochar Validation Studio - Agent README

This document is intended for AI coding assistants (Agents) working on this codebase. It provides internal context, design rationale, and state management details that might not be obvious from the code alone.

## 1. Core Logic & Data Flow
The application follows a strict **Excel -> SQLite -> JSON -> Excel** lifecycle.

- **Importers**: `app/services/importer.py` handles the "hydration" of data. It performs a fuzzy search for image columns because the source spreadsheets (Kalki vs Looker) often change their naming conventions.
- **State Persistence**: Every unit of work is a `BatchRow`. The `validation_data` field within `BatchRow` is a JSON blob storing the nested status of all stages (`moisture`, `start`, `mid`, `90`, `end`).
- **Exporter**: `app/services/exporter.py` is responsible for "flattening" the JSON blobs back into Excel columns. It **must** use stage-prefixed headers (e.g., `Start_Status`) to prevent collisions.

## 2. Front-End Design Patterns (3-Panel UI)
The validation interface (`app/templates/validation.html`) uses a custom layout, not a standard framework component.

- **Split Panels**: Implemented via `resizer` divs and manual JS event listeners (`initResizers`). Avoid replacing these with heavy libraries like Split.js unless a complete UI overhaul is requested.
- **Image Viewer**: Uses manual CSS transforms (`translate`, `scale`, `rotate`). The `Fit to Screen` logic is sensitive to the container dimensions and image aspect ratios.
- **Auto-Save**: The UI uses a debounced (800ms) POST request to `/api/batches/{id}`. The "Saved" indicator is optimistic but robust.

## 3. Critical Naming Conventions
To maintain compatibility between the Python backend and JS frontend, always use these unified keys for stages:
- `moisture`
- `start`
- `mid`
- `90` (Note: In headers, this is often mapped to `90_Percent`)
- `end`

## 4. Current SOP & Schema
The `VALIDATION_SCHEMA` in `app/config.py` is the single source of truth for:
- Rejection reason dropdowns.
- Image column lookup patterns.
- Internal stage labels.

## 5. Known Design Quirks
- **Keyboard Shortcuts**: They are "global" listeners on the `document`. If adding new focusable inputs, ensure they don't trigger validation shortcuts while typing.
- **Navigation Logic**: Moving from the 'End' stage of batch $N$ automatically jumps to the 'Moisture' stage of batch $N+1$. This is a requested workflow optimization.
- **Metadata**: In `validation.html`, the "Date Time Stamp" field is a robust lookup searching for multiple database keys (`production_time_date`, etc.) to ensure a full timestamp is displayed.

## 6. Future Improvements Ideas (Audit Findings)
- Column ordering in the final Excel export is currently "MVP" (appended at the end).
- Image pre-fetching for the "Next" batch could improve perceived speed for users on slow connections.
- Migration to a more structured Alembic setup if more complex database relationships are added.
