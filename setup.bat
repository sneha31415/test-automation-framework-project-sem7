@echo off
REM One-time setup: creates a virtual environment and installs dependencies.
cd /d "%~dp0"
python --version >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found. Install Python 3.11+ and tick "Add python.exe to PATH".
    exit /b 1
)
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete. Run run_smoke.bat or run_all.bat next.
