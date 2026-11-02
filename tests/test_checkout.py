"""Checkout module - FR-11 to FR-16."""
import pytest

from pages.checkout_page import CheckoutCompletePage, CheckoutOverviewPage
from utils.data_reader import read_csv, read_json
from utils.logger import log_step

CUSTOMER = read_json("customer.json")


def _checkout_negative_params():
    return [
        pytest.param(
            row,
            id=f"{row['tc_id']}-{row['title']}",
            marks=[pytest.mark.regression, pytest.mark.fr(row["fr_id"])],
        )
        for row in read_csv("checkout_negative.csv")
    ]


def _postal_code_params():
    params = []
    for case in read_json("postal_codes.json")["cases"]:
        marks = [pytest.mark.regression, pytest.mark.fr("FR-14")]
        if case["known_defect"]:
            marks += [
                pytest.mark.known_defect,
                pytest.mark.xfail(
                    reason=(
                        "DEF-01: FR-14 says this postal code must be rejected, but the "
                        "application accepts it (no numeric / length validation)."
                    ),
                    strict=False,  # if the site is ever fixed this shows as XPASS, not a failure
                ),
            ]
        label = case["description"].replace(" ", "_")
        params.append(pytest.param(case, id=f"{case['tc_id']}-{label}", marks=marks))
    return params


@pytest.mark.smoke
@pytest.mark.fr("FR-11")
def test_checkout_button_opens_your_information_page(cart_page, driver):
    """FR-11: Checkout on the Cart page opens 'Checkout: Your Information'."""
    cart_page.click_checkout()

    assert cart_page.wait_for_page_title("Checkout: Your Information"), "Checkout page title not shown"
    assert "checkout-step-one" in cart_page.current_url


@pytest.mark.parametrize("row", _checkout_negative_params())
def test_mandatory_name_fields(checkout_info, row):
    """FR-12/13: a blank First or Last Name shows an error and keeps the user on the form."""
    log_step(f"Submit: first='{row['first_name']}' last='{row['last_name']}' postal='{row['postal_code']}'")
    checkout_info.fill_information(row["first_name"], row["last_name"], row["postal_code"])
    checkout_info.click_continue()

    assert checkout_info.is_error_displayed(), "Error message was not displayed"
    message = checkout_info.get_error_message()
    log_step(f"Error message: {message}")
    assert row["expected_error"].lower() in message.lower(), (
        f"Expected error containing '{row['expected_error']}' but got '{message}'"
    )
    assert checkout_info.is_still_on_this_page(), "User must stay on 'Your Information'"


@pytest.mark.parametrize("case", _postal_code_params())
def test_postal_code_validation(checkout_info, driver, case):
    """FR-14: postal code boundaries (4 invalid / 5 valid / 6 valid) and non-numeric values."""
    log_step(f"Postal code '{case['value']}' ({case['description']}) -> expected {case['expected']}")
    checkout_info.fill_information(CUSTOMER["first_name"], CUSTOMER["last_name"], case["value"])
    checkout_info.click_continue()

    if case["expected"] == "valid":
        overview = CheckoutOverviewPage(driver)
        assert overview.is_loaded(), f"Valid postal code '{case['value']}' did not reach the Overview page"
    else:
        assert checkout_info.is_error_displayed(), (
            f"Invalid postal code '{case['value']}' was accepted - no error message shown"
        )
        assert checkout_info.is_still_on_this_page(), "User must stay on 'Your Information'"


@pytest.mark.regression
@pytest.mark.fr("FR-15")
def test_valid_information_leads_to_overview(checkout_info, driver):
    """FR-15: valid first name, last name and postal code open 'Checkout: Overview'."""
    checkout_info.fill_information(CUSTOMER["first_name"], CUSTOMER["last_name"], CUSTOMER["postal_code"])
    checkout_info.click_continue()

    overview = CheckoutOverviewPage(driver)
    assert overview.is_loaded(), "Checkout: Overview page was not displayed"
    assert checkout_info.selected_item in overview.get_item_names(), "Selected item missing on Overview"


@pytest.mark.smoke
@pytest.mark.fr("FR-16")
def test_finish_order_shows_success_message(checkout_info, driver):
    """FR-16: Finish on the Overview page shows the 'Thank you for your order' message."""
    checkout_info.fill_information(CUSTOMER["first_name"], CUSTOMER["last_name"], CUSTOMER["postal_code"])
    checkout_info.click_continue()
    overview = CheckoutOverviewPage(driver)
    assert overview.is_loaded(), "Precondition failed: Overview page not displayed"

    overview.click_finish()
    complete = CheckoutCompletePage(driver)
    assert complete.is_loaded(), "Checkout: Complete page was not displayed"
    message = complete.get_success_message()
    log_step(f"Success message: {message}")
    assert "thank you for your order" in message.lower(), f"Unexpected success message: '{message}'"
    assert complete.wait_for_cart_count(0), "Cart badge should be empty after the order is placed"
