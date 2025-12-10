@echo off
setlocal

rem Jump to frontend folder
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

echo Starting frontend (Vite) dev server...
npm run dev -- --host

