@echo off
SETLOCAL EnableDelayedExpansion

echo Starting Biochar Validation Studio for Windows...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python could not be found. Please install Python 3.
    pause
    exit /b
)

:: Create venv if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    
    echo Installing dependencies...
    pip install fastapi uvicorn sqlalchemy pandas openpyxl jinja2 python-multipart
) else (
    call venv\Scripts\activate
)

:: Open Browser (Wait a bit for server to start)
start "" http://localhost:8000

:: Run App
echo Server running at http://localhost:8000
python -m app.main

pause
