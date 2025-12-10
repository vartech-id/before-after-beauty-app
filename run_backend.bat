@echo off
setlocal

rem Jump to repository root (this file's folder)
cd /d "%~dp0"

set "PYTHON=backend\venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    set "PYTHON=python"
)

echo Starting backend with %PYTHON% ...
"%PYTHON%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

