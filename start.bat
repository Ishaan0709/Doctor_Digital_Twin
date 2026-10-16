@echo off
setlocal EnableExtensions
set PYTHONDONTWRITEBYTECODE=1
cd /d "%~dp0"
call "%~dp0scripts\resolve_venv.bat" "%~dp0"
if errorlevel 1 exit /b 1
if not exist "%~dp0web\dist\index.html" (
  echo Frontend build not found. Run setup.bat first.
  exit /b 1
)
echo Opening http://localhost:8000
start "" "http://localhost:8000"
"%VENV%\Scripts\python.exe" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
