#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 was not found. Please install Python 3.11+."
    exit 1
fi

echo "Creating virtual environment 'venv'..."
python3 -m venv venv
source venv/bin/activate
echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete! Run ./run_smoke.sh or ./run_all.sh next."

