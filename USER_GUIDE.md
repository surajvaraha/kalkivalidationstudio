# Biochar Validation Studio - User Guide

Welcome to the Biochar Validation Studio! This tool is designed to make your validation workflow faster, more accurate, and entirely keyboard-driven.

## 1. Getting Started
To start the application, simply double-click the `run_tool.sh` file or run it from your terminal:
```bash
./run_tool.sh
```
This will automatically set up the environment and open the Dashboard in your default web browser.

## 2. The Dashboard
The Dashboard is your control center for validation tasks.
- **Upload**: Click "**+ New Validation Task**" to import a Kalki or Looker Excel sheet.
- **Resume**: The system saves your progress automatically. You can close the app and click "**Validate**" on any existing task to pick up where you left off.
- **Export**: Once finished, click "**Export .xlsx**" to download the final validated file.

## 3. The Validation Interface (3 Panels)
- **Left Panel**: Current Batch metadata (ID, Time, Partner) and a pinned **Status Table** showing which stages you've already completed for this batch.
- **Center Panel**: The high-resolution Image Viewer. You can zoom with your mouse wheel and drag to pan.
- **Right Panel**: Your decision center. Select Status, Reasons, and toggle Geotag/Serial checks.

## 4. Keyboard Shortcuts (Pro Workflow)
For maximum speed, we recommend using the keyboard:

### Navigation
- **Shift + &larr; / &rarr;**: Switch between different **Batches**.
- **&larr; / &rarr;**: Switch between different **Stages** (Moist, Start, Mid, 90%, End).
- Moving "Next" from the **End** stage will automatically jump you to the next batch.

### Decisions
- **A**: Approve the current stage.
- **G**: Toggle **Geotag** present.
- **S**: Toggle **Serial #** valid.
- **Q**: Mark as **Under Query**.

### Smart Rejection (Fastest)
1. Press **R** to open the Rejection Modal.
2. Press a **Number Key (1-9)** to select your reason.
3. The modal will close, and your choice will be saved instantly.

## 5. Tips for Success
- **Fit to Screen**: If an image looks too small, click the "Expand" icon in the bottom center toolbar or press `F`.
- **Auto-Save**: You don't need to look for a save button! Every change is saved to the database within 800ms of your action.
- **Export Cleanup**: The final exported file will have clear columns like `Start_Status`, `Mid_Status`, etc., making it easy for the final reporting team to read.
