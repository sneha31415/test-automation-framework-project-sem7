"""File logging for the framework.

Every line written to ``reports/logs/execution_<timestamp>.log`` contains:
    timestamp | level | test name | STEP/STATUS marker + message
which satisfies the "test name, step, status" logging requirement.
"""
import logging
from datetime import datetime

from config import settings

LOGGER_NAME = "saucedemo"
_current_test = "-"


class _TestNameFilter(logging.Filter):
    """Injects the name of the currently running test into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.test_name = _current_test
        return True


def set_current_test(name: str) -> None:
    global _current_test
    _current_test = name


def get_logger() -> logging.Logger:
    """Return the shared framework logger (configured once per run)."""
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        settings.ensure_dirs()
        logger.setLevel(logging.DEBUG)
        log_file = settings.LOG_DIR / f"execution_{datetime.now():%Y%m%d_%H%M%S}.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(test_name)s | %(message)s")
        )
        handler.addFilter(_TestNameFilter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def log_step(message: str) -> None:
    """Log a human-readable test step."""
    get_logger().info("STEP   | %s", message)


def log_status(status: str, detail: str = "") -> None:
    """Log the outcome of a test (PASSED / FAILED / XFAILED ...)."""
    suffix = f" - {detail}" if detail else ""
    get_logger().info("STATUS | %s%s", status, suffix)
