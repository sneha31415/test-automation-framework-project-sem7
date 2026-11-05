#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source venv/bin/activate
pytest -m regression "$@"
echo ""
echo "HTML report generated: reports/report.html"

