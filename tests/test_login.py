"""Login module - FR-01 to FR-05."""
import pytest

from config import settings
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.data_reader import read_csv, read_json
from utils.logger import log_step


def _login_negative_params():
    return [
        pytest.param(
            row,
            id=f"{row['tc_id']}-{row['title']}",
            marks=[pytest.mark.regression, pytest.mark.fr(row["fr_id"])],
        )
        for row in read_csv("login_negative.csv")
    ]


def _username_boundary_params():
    data = read_json("username_boundary.json")["cases"]
    return [
        pytest.param(
            case,
            id=f"{case['tc_id']}-{case['length']}_chars",
            marks=[pytest.mark.regression, pytest.mark.fr("FR-05")],
        )
        for case in data
    ]


@pytest.mark.smoke
@pytest.mark.fr("FR-01")
def test_login_success(login_page, driver):
    """FR-01: valid credentials open the Products page."""
    log_step("Log in with the valid credentials")
    login_page.login(settings.VALID_USERNAME, settings.VALID_PASSWORD)

    inventory = InventoryPage(driver)
    assert inventory.is_loaded(), "Products page title was not displayed after login"
    assert inventory.get_page_title() == "Products"
    assert "inventory.html" in inventory.current_url


@pytest.mark.parametrize("row", _login_negative_params())
def test_login_failure(login_page, row):
    """FR-02/03/04: invalid, blank or locked-out credentials show an error and stay on Login."""
    log_step(f"Attempt login: user='{row['username']}' password='{row['password']}'")
    login_page.login(row["username"], row["password"])

    assert login_page.is_error_displayed(), "Error banner was not displayed"
    message = login_page.get_error_message()
    log_step(f"Error banner text: {message}")
    assert row["expected_error"].lower() in message.lower(), (
        f"Expected error containing '{row['expected_error']}' but got '{message}'"
    )
    assert "inventory.html" not in login_page.current_url, "User must stay on the Login page"
    assert login_page.is_on_login_page()


@pytest.mark.parametrize("case", _username_boundary_params())
def test_username_length_boundary(login_page, case):
    """FR-05: usernames around/over 30 characters never log in and show an error banner."""
    username = "a" * case["length"]
    log_step(f"Boundary test: username length = {len(username)} ({case['note']})")
    login_page.login(username, settings.VALID_PASSWORD)

    assert login_page.is_error_displayed(), "Error banner was not displayed"
    assert "inventory.html" not in login_page.current_url
    assert login_page.is_on_login_page()
