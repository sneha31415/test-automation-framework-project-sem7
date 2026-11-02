@echo off
REM Runs the regression suite (negative, boundary and secondary tests).
cd /d "%~dp0"
call venv\Scripts\activate
pytest -m regression %*
echo.
echo HTML report: reports\report.html
