# Biochar Validation Studio V2 - Production Ready

The Biochar Validation Studio is now fully audited and optimized for distribution. It supports both **Kalki** and **Looker** formats with a robust, keyboard-driven validation workflow.

## Final Improvements (Audit Phase)
1.  **Cross-Format Robustness**: The importer now uses "Fuzzy Mapping" to find image columns even if naming varies between Looker and Kalki (e.g., `Wood Moisture Image Link` vs `Wood Moisture (Image)`).
2.  **Data Integrity**: Exported Excel files now use strictly prefixed columns (e.g., `Start_Status`, `Start_Geotag`, `Mid_Geotag`). This prevents data from being overwritten when validating multiple stages.
3.  **Unified Schema**: Internal stage names have been unified across Backend and Frontend (`moisture`, `start`, `mid`, `90`, `end`) for 1:1 data consistency.
4.  **UI Refinements**: 
    *   **Date Time Stamp** metadata is now fully robust.
    *   **Status Overview** is pinned to the top of the Left Panel.
    *   **Progress Counter** is visible in the Right Panel.

## Keyboard Shortcuts Summary
- `Shift + Left/Right`: Switch Batches
- `Left/Right`: Switch Stages
- `A`: Approve Stage
- `R`: Smart Rejection (Opens Numeric Modal)
- `1-9`: Select Rejection Reason (within modal)
- `G`: Toggle Geotag Check
- `S`: Toggle Serial Check

## How to Deploy
1.  Zip the project folder (excluding `venv` and `.git`).
2.  Users run `./run_tool.sh` to start and install automatically.
