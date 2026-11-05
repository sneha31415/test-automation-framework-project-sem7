#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source venv/bin/activate
pytest -m smoke "$@"
echo ""
echo "HTML report generated: reports/report.html"

