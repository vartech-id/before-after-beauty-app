@echo off
setlocal

rem Launch backend and frontend in separate windows
cd /d "%~dp0"

start "Backend" cmd /k ""%~dp0run_backend.bat""
start "Frontend" cmd /k ""%~dp0run_frontend.bat""

echo Backend and frontend are starting in their own windows.
echo Frontend dev server: http://localhost:5173
echo Close those windows or press Ctrl+C in them to stop the servers.

