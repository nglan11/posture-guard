@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found. Run scripts\setup.ps1 first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m posture_guard.main
if errorlevel 1 pause
