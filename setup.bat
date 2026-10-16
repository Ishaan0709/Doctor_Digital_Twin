@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where node >nul 2>&1
if errorlevel 1 (
  echo Node.js is required. Install it from https://nodejs.org and run setup.bat again.
  exit /b 1
)

set "VENV=%~dp0.venv"
if exist "%~dp0.venv\Scripts\python.exe" goto venv_ready
if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "VENV=%~dp0..\.venv"
  goto venv_ready
)

echo Creating .venv ...
py -3 -m venv "%~dp0.venv"
if errorlevel 1 python -m venv "%~dp0.venv"
if errorlevel 1 (
  echo Could not create a Python virtual environment.
  exit /b 1
)
set "VENV=%~dp0.venv"

:venv_ready
echo Using %VENV%
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1
"%VENV%\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 exit /b 1

pushd "%~dp0web"
call npm install
if errorlevel 1 (
  popd
  exit /b 1
)
call npm run build
if errorlevel 1 (
  popd
  exit /b 1
)
popd

if not exist "%~dp0.env" (
  copy /Y "%~dp0.env.example" "%~dp0.env" >nul
  echo Created .env from .env.example. Add your OPENAI_API_KEY.
) else (
  echo .env already exists and was left unchanged.
)

echo Setup complete. Next, run start.bat
exit /b 0
