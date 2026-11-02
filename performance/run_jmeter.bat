@echo off
REM ---------------------------------------------------------------------------
REM  Runs the SauceDemo load test in JMeter non-GUI mode, then builds
REM  aggregate.csv and Findings.md from the results.
REM
REM  Prerequisites: Java 8+ and Apache JMeter 5.6+ with its \bin folder on PATH
REM  Usage (from the project root or this folder):  performance\run_jmeter.bat
REM  Takes about 3 minutes.
REM ---------------------------------------------------------------------------
setlocal
cd /d "%~dp0"

where jmeter >nul 2>nul
if errorlevel 1 (
    echo [ERROR] jmeter was not found on PATH. Add JMeter's bin folder to PATH and retry.
    exit /b 1
)

REM JMeter refuses to write a dashboard into a non-empty folder, so clear old output first
if exist results\results.jtl del /q results\results.jtl
if exist results\jmeter.log del /q results\jmeter.log
if exist html_report rmdir /s /q html_report

echo Running load test: 20 users, 60s ramp-up, 180s duration ...
jmeter -n -t jmx\saucedemo_weekend_lab.jmx -l results\results.jtl -j results\jmeter.log -e -o html_report
if errorlevel 1 (
    echo [ERROR] JMeter run failed - see results\jmeter.log
    exit /b 1
)

echo Creating aggregate.csv and Findings.md ...
python analyze_results.py
echo.
echo Done. Open performance\html_report\index.html for the dashboard.
endlocal
