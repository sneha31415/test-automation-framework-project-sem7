"""Page object for the Products (inventory) page."""
from typing import Dict, List

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


def _xpath_literal(value: str) -> str:
    """Quote a string for use inside an XPath expression."""
    if "'" not in value:
        return f"'{value}'"
    return '"' + value + '"'


class InventoryPage(BasePage):
    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAME_CSS = "[data-test='inventory-item-name']"
    ITEM_PRICE_CSS = "[data-test='inventory-item-price']"

    # ----------------------------------------------------------- page state
    def is_loaded(self) -> bool:
        """True when the page title reads 'Products'."""
        return self.wait_for_page_title("Products")

    @staticmethod
    def _item_xpath(name: str) -> str:
        return (
            "//div[@data-test='inventory-item']"
            f"[.//div[@data-test='inventory-item-name'][normalize-space()={_xpath_literal(name)}]]"
        )

    def _button(self, name: str):
        return (By.XPATH, self._item_xpath(name) + "//button")

    # ------------------------------------------------------------- reading
    def get_products(self) -> List[Dict]:
        """Return name, price (float) and button text for every product shown."""
        products = []
        for item in self.find_all(self.ITEMS):
            price_text = item.find_element(By.CSS_SELECTOR, self.ITEM_PRICE_CSS).text
            products.append(
                {
                    "name": item.find_element(By.CSS_SELECTOR, self.ITEM_NAME_CSS).text.strip(),
                    "price": float(price_text.replace("$", "").strip()),
                    "button_text": item.find_element(By.TAG_NAME, "button").text.strip(),
                }
            )
        return products

    def get_product_names(self) -> List[str]:
        return [p["name"] for p in self.get_products()]

    # ------------------------------------------------------------- actions
    def add_to_cart(self, name: str) -> None:
        self.click(self._button(name), f"'Add to cart' for '{name}'")

    def remove_from_cart(self, name: str) -> None:
        self.click(self._button(name), f"'Remove' for '{name}'")

    def add_to_cart_by_index(self, index: int) -> str:
        """Add the product at position ``index`` and return its name."""
        name = self.get_product_names()[index]
        self.add_to_cart(name)
        return name

    def wait_for_button_text(self, name: str, expected: str) -> bool:
        """True when the product's button reads ``expected`` ('Add to cart' / 'Remove')."""
        return self.wait_for_text(self._button(name), expected)
