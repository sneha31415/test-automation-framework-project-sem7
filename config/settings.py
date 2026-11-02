"""Central configuration for the SauceDemo automation framework.

Everything that might change between machines or runs lives here, so that
tests and page objects never contain hard-coded URLs, credentials or timeouts.
Values can be overridden with environment variables or pytest CLI options
(see conftest.py).
"""
import os
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"
LOG_DIR = REPORTS_DIR / "logs"
TESTDATA_DIR = ROOT_DIR / "testdata"

# ---------------------------------------------------- application under test
BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com/")

# Credentials supplied in the case study (override via env vars if ever needed)
VALID_USERNAME = os.getenv("SAUCE_USER", "standard_user")
VALID_PASSWORD = os.getenv("SAUCE_PASS", "secret_sauce")

# ------------------------------------------------------------------ browser
HEADLESS = os.getenv("HEADLESS", "0") == "1"

# ------------------------------------------------------------ explicit waits
# EXPLICIT_WAIT : max seconds to wait for an element/condition that MUST appear.
# SHORT_WAIT    : max seconds when we are checking something that may legitimately
#                 NOT appear (e.g. "is an error banner shown?") so negative checks
#                 stay fast. Both are used with WebDriverWait - never time.sleep.
EXPLICIT_WAIT = 10
SHORT_WAIT = 3


def ensure_dirs() -> None:
    """Create the report folders if they do not exist yet."""
    for folder in (REPORTS_DIR, SCREENSHOT_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)
