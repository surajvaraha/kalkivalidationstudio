# End-to-End System Audit Plan (Production Readiness)

This plan outlines the steps to verify and polish the Biochar Validation Studio for public release, focusing on cross-compatibility between Looker and Kalki formats and export integrity.

## Proposed Audit Areas

### 1. Data Integrity & Schema Support
- **Review**: `app/services/importer.py` and `app/config.py`.
- **Goal**: Ensure that all mandatory columns for both Looker and Kalki are correctly mapped and that the application doesn't crash on slightly malformed inputs.
- **Check**: Key column existence for `wood_moisture`, `Geotag`, `Serial` across both types.

### 2. Export Robustness
- **Review**: `app/services/exporter.py`.
- **Goal**: Verify that the "flattened" validation data correctly writes out unique columns per stage (e.g., `Start_Status`, `Mid_Status`) without overwriting shared fields like `geotag`.
- **Improvement**: Explicitly prefix sub-check columns with the stage name to avoid collision.

### 3. UI/UX Consistency
- **Review**: `app/templates/validation.html` and `app/templates/dashboard.html`.
- **Goal**: Ensure the recent V10 layout changes work for both Looker and Kalki.
- **Check**: Metadata table displays relevant info for Looker (Inventory ID) vs Kalki (Batch ID).
- **Check**: Image fits and zoom levels persist correctly.

### 4. Error Handling
- **Goal**: Prevent the app from hanging if a media link is broken or a database transaction fails.

## Verification Plan
1. **Mock Load**: Import a Looker file and a Kalki file.
2. **Partial Validation**: Validate a few rows, close app, reopen.
3. **Full Export**: Export to Excel and verify column count and data values.
