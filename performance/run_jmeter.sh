#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if ! command -v jmeter &>/dev/null; then
    echo "[ERROR] jmeter was not found on PATH. Please install JMeter and ensure Java is installed."
    exit 1
fi

rm -f results/results.jtl results/jmeter.log
rm -rf html_report

echo "Running load test: 20 users, 60s ramp-up, 180s duration..."
jmeter -n -t jmx/saucedemo_weekend_lab.jmx -l results/results.jtl -j results/jmeter.log -e -o html_report

echo "Creating aggregate.csv and Findings.md..."
python3 analyze_results.py

echo ""
echo "Done. Open performance/html_report/index.html to view the dashboard."

