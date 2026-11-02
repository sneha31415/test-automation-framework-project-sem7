"""Session / access control - FR-10."""
import pytest

from pages.login_page import LoginPage
from utils.logger import log_step


@pytest.mark.regression
@pytest.mark.fr("FR-10")
def test_logout_returns_to_login_page(inventory, driver):
    """FR-10 (supporting): logging out lands on the Login page."""
    inventory.logout()
    assert LoginPage(driver).is_on_login_page(), "Login page was not displayed after logout"


@pytest.mark.regression
@pytest.mark.fr("FR-10")
@pytest.mark.parametrize("protected_page", ["inventory.html", "cart.html"])
def test_protected_pages_redirect_to_login_after_logout(inventory, driver, protected_page):
    """FR-10: opening inventory/cart directly after logout redirects to Login."""
    inventory.logout()
    login = LoginPage(driver)
    assert login.is_on_login_page(), "Precondition failed: not logged out"

    log_step(f"Navigate directly to /{protected_page} while logged out")
    login.open(protected_page)

    assert login.is_on_login_page(), f"Login page was not shown when opening /{protected_page}"
    assert not login.current_url.rstrip("/").endswith(protected_page.rstrip("/")), (
        f"Still on /{protected_page} - user was not redirected"
    )
    log_step(f"Banner shown after redirect: '{login.get_error_message()}'")
