@echo off
set "APP=%~1"
if exist "%APP%.venv\Scripts\python.exe" (
  set "VENV=%APP%.venv"
  exit /b 0
)
if exist "%APP%..\.venv\Scripts\python.exe" (
  set "VENV=%APP%..\.venv"
  exit /b 0
)
echo No virtual environment found. Run setup.bat first.
exit /b 1
