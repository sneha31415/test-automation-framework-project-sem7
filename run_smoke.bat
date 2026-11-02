@echo off
REM Runs the smoke suite (core happy-path flows).
cd /d "%~dp0"
call venv\Scripts\activate
pytest -m smoke %*
echo.
echo HTML report: reports\report.html
