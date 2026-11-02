"""Helpers for data-driven tests: read CSV / JSON files from ``testdata/``."""
import csv
import json
from typing import Any, Dict, List

from config import settings


def read_csv(filename: str) -> List[Dict[str, str]]:
    """Return the rows of ``testdata/<filename>`` as a list of dicts."""
    path = settings.TESTDATA_DIR / filename
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(filename: str) -> Any:
    """Return the parsed content of ``testdata/<filename>``."""
    path = settings.TESTDATA_DIR / filename
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)
