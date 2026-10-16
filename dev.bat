@echo off
setlocal EnableExtensions
set PYTHONDONTWRITEBYTECODE=1
cd /d "%~dp0"
call "%~dp0scripts\resolve_venv.bat" "%~dp0"
if errorlevel 1 exit /b 1
if not exist "%~dp0web\node_modules" (
  echo Frontend packages are missing. Run setup.bat first.
  exit /b 1
)
"%VENV%\Scripts\python.exe" "%~dp0scripts\dev_server.py"
