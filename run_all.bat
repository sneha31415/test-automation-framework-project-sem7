@echo off
REM Runs the full suite (smoke + regression).
cd /d "%~dp0"
call venv\Scripts\activate
pytest %*
echo.
echo HTML report: reports\report.html
