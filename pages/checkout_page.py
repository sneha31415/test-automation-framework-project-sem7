"""Page objects for the three checkout screens:
Your Information -> Overview -> Complete.
"""
from typing import List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    """Checkout: Your Information."""

    FIRST_NAME = (By.CSS_SELECTOR, "[data-test='firstName']")
    LAST_NAME = (By.CSS_SELECTOR, "[data-test='lastName']")
    POSTAL_CODE = (By.CSS_SELECTOR, "[data-test='postalCode']")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "[data-test='continue']")
    ERROR_BANNER = (By.CSS_SELECTOR, "[data-test='error']")

    def is_loaded(self) -> bool:
        return self.wait_for_page_title("Checkout: Your Information")

    def fill_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Type the three fields (any may be blank)."""
        self.type_text(self.FIRST_NAME, first_name, "First Name")
        self.type_text(self.LAST_NAME, last_name, "Last Name")
        self.type_text(self.POSTAL_CODE, postal_code, "Postal Code")

    def click_continue(self) -> None:
        self.click(self.CONTINUE_BUTTON, "Continue button")

    def is_error_displayed(self) -> bool:
        return self.is_visible(self.ERROR_BANNER)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_BANNER) if self.is_error_displayed() else ""

    def is_still_on_this_page(self) -> bool:
        """True when the information form is still displayed."""
        return "checkout-step-one" in self.current_url and self.is_visible(self.FIRST_NAME)


class CheckoutOverviewPage(BasePage):
    """Checkout: Overview."""

    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    FINISH_BUTTON = (By.CSS_SELECTOR, "[data-test='finish']")

    def is_loaded(self, timeout: float = None) -> bool:
        return self.wait_for_page_title("Checkout: Overview", timeout)

    def get_item_names(self) -> List[str]:
        return [el.text.strip() for el in self.find_all(self.ITEM_NAMES)]

    def click_finish(self) -> None:
        self.click(self.FINISH_BUTTON, "Finish button")


class CheckoutCompletePage(BasePage):
    """Checkout: Complete."""

    COMPLETE_HEADER = (By.CSS_SELECTOR, "[data-test='complete-header']")

    def is_loaded(self) -> bool:
        return self.wait_for_page_title("Checkout: Complete!")

    def get_success_message(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)
