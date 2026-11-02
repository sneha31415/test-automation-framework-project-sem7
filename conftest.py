"""Shared fixtures and pytest hooks.

Provides:
  * ``driver``            - a Chrome instance per test, always closed afterwards
  * page / flow fixtures  - ``login_page``, ``inventory``, ``cart_page``, ``checkout_info``
  * screenshot on failure - saved to reports/screenshots/ and embedded in the HTML report
  * file logging          - test name, steps and final status in reports/logs/
  * report enrichment     - an "FR ID" column for requirement traceability
"""
import base64
import html
import os
import re
from datetime import datetime

import pytest

from config import settings
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutInfoPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.driver_factory import create_driver
from utils.logger import get_logger, log_status, set_current_test


# --------------------------------------------------------------------- CLI
def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False,
                     help="Run Chrome without a visible window")
    parser.addoption("--base-url", action="store", default=None,
                     help="Override the application URL (default: https://www.saucedemo.com/)")


def pytest_configure(config):
    settings.ensure_dirs()
    base_url = config.getoption("--base-url")
    if base_url:
        settings.BASE_URL = base_url if base_url.endswith("/") else base_url + "/"
    if config.getoption("--headless") or os.getenv("HEADLESS") == "1":
        settings.HEADLESS = True
    # Show the AUT in the "Environment" table of the HTML report
    try:
        from pytest_metadata.plugin import metadata_key

        config.stash[metadata_key]["Application URL"] = settings.BASE_URL
        config.stash[metadata_key]["Headless"] = str(settings.HEADLESS)
    except Exception:  # noqa: BLE001 - metadata is cosmetic only
        pass


# ------------------------------------------------------------- HTML report
def pytest_html_report_title(report):
    report.title = "SauceDemo Automation - Test Execution Report"


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>FR ID</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{html.escape(getattr(report, 'fr_id', ''))}</td>")


# ------------------------------------------------- failure evidence + logging
def _save_screenshot(driver, test_name: str, prefix: str):
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_name)[:120]
    path = settings.SCREENSHOT_DIR / f"{prefix}_{safe_name}_{datetime.now():%Y%m%d_%H%M%S}.png"
    driver.save_screenshot(str(path))
    return path


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # traceability: expose the FR ID(s) from @pytest.mark.fr(...) on the report
    report.fr_id = ", ".join(arg for mark in item.iter_markers("fr") for arg in mark.args)

    if report.when not in ("setup", "call"):
        return
    if report.when == "setup" and report.passed:
        return

    is_xfail = hasattr(report, "wasxfail")
    if report.passed:
        status = "XPASSED" if is_xfail else "PASSED"
    elif report.failed:
        status = "FAILED"
    else:
        status = "XFAILED" if is_xfail else "SKIPPED"

    detail = ""
    if call.excinfo is not None:
        detail = str(call.excinfo.value).strip().splitlines()[0][:200] if str(call.excinfo.value).strip() else ""
    log_status(status, detail)

    # Evidence: screenshot for real failures AND for expected failures (defect proof)
    if status in ("FAILED", "XFAILED"):
        driver = getattr(item, "driver_instance", None)
        if driver is not None:
            try:
                from pytest_html import extras

                prefix = "FAIL" if status == "FAILED" else "XFAIL"
                path = _save_screenshot(driver, item.name, prefix)
                get_logger().info("STATUS | Screenshot saved: %s", path)
                encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
                report.extras = getattr(report, "extras", []) + [
                    extras.png(encoded, name="Screenshot"),
                    extras.url(driver.current_url, name="Page URL"),
                ]
            except Exception as exc:  # noqa: BLE001 - never let evidence capture break a run
                get_logger().warning("Could not capture screenshot: %s", exc)


@pytest.fixture(autouse=True)
def _log_test_context(request):
    """Tag every log line with the test name and log START / END markers."""
    set_current_test(request.node.name)
    get_logger().info("START  | %s", request.node.nodeid)
    yield
    get_logger().info("END    | %s", request.node.nodeid)
    set_current_test("-")


# ---------------------------------------------------------------- fixtures
@pytest.fixture
def driver(request):
    """A fresh Chrome browser for each test; quit even when the test fails."""
    browser = create_driver(headless=settings.HEADLESS)
    request.node.driver_instance = browser  # lets the report hook take screenshots
    yield browser
    browser.quit()


@pytest.fixture
def login_page(driver):
    """The login page, already opened."""
    return LoginPage(driver).open()


@pytest.fixture
def inventory(login_page, driver):
    """Logged in as standard_user and sitting on the Products page."""
    login_page.login(settings.VALID_USERNAME, settings.VALID_PASSWORD)
    page = InventoryPage(driver)
    assert page.is_loaded(), "Precondition failed: could not log in to reach the Products page"
    return page


@pytest.fixture
def cart_page(inventory, driver):
    """Cart page containing exactly one item (``cart_page.selected_item`` = its name)."""
    name = inventory.add_to_cart_by_index(0)
    inventory.open_cart()
    page = CartPage(driver)
    assert page.is_loaded(), "Precondition failed: Cart page did not open"
    page.selected_item = name
    return page


@pytest.fixture
def checkout_info(cart_page, driver):
    """Checkout: Your Information page (``checkout_info.selected_item`` = item in cart)."""
    cart_page.click_checkout()
    page = CheckoutInfoPage(driver)
    assert page.is_loaded(), "Precondition failed: Checkout page did not open"
    page.selected_item = cart_page.selected_item
    return page
