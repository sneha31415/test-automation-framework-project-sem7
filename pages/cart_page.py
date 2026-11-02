"""Page object for the Cart page."""
from typing import Dict, List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "[data-test='checkout']")
    CONTINUE_SHOPPING = (By.CSS_SELECTOR, "[data-test='continue-shopping']")

    def is_loaded(self) -> bool:
        return self.wait_for_page_title("Your Cart")

    def get_items(self) -> List[Dict]:
        """Return name and price (float) of every item listed in the cart."""
        items = []
        for row in self.find_all(self.ITEMS):
            price_text = row.find_element(
                By.CSS_SELECTOR, "[data-test='inventory-item-price']"
            ).text
            items.append(
                {
                    "name": row.find_element(
                        By.CSS_SELECTOR, "[data-test='inventory-item-name']"
                    ).text.strip(),
                    "price": float(price_text.replace("$", "").strip()),
                }
            )
        return items

    def click_checkout(self) -> None:
        self.click(self.CHECKOUT_BUTTON, "Checkout button")
