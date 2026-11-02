"""BasePage: shared Selenium helpers (all explicit waits) and the page header.

Every page object inherits from this class, so no test or page ever calls
``time.sleep`` or touches WebDriverWait directly.
"""
from typing import List, Tuple
from urllib.parse import urljoin

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from utils.logger import get_logger

Locator = Tuple[str, str]


class BasePage:
    # ---- elements present in the header of every logged-in page
    PAGE_TITLE: Locator = (By.CSS_SELECTOR, "[data-test='title']")
    CART_LINK: Locator = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    CART_BADGE: Locator = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    MENU_BUTTON: Locator = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK: Locator = (By.CSS_SELECTOR, "[data-test='logout-sidebar-link']")

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.log = get_logger()

    # ------------------------------------------------------------ navigation
    def open(self, path: str = "") -> None:
        url = urljoin(settings.BASE_URL, path)
        self.log.info("STEP   | Open URL %s", url)
        self.driver.get(url)

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # ------------------------------------------------------- explicit waits
    def _wait(self, timeout: float = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or settings.EXPLICIT_WAIT)

    def find(self, locator: Locator) -> WebElement:
        """Wait until the element is visible, then return it."""
        return self._wait().until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> List[WebElement]:
        """Wait until at least one matching element is present, then return all."""
        return self._wait().until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: Locator, description: str = "") -> None:
        element = self._wait().until(EC.element_to_be_clickable(locator))
        self.log.info("STEP   | Click %s", description or locator[1])
        element.click()

    def type_text(self, locator: Locator, text: str, description: str = "") -> None:
        """Clear a field and type into it. An empty string just leaves it blank."""
        element = self.find(locator)
        element.clear()
        shown = "(left blank)" if text == "" else text
        self.log.info("STEP   | Enter '%s' in %s", shown, description or locator[1])
        if text:
            element.send_keys(text)

    def get_text(self, locator: Locator) -> str:
        return self.find(locator).text.strip()

    def is_visible(self, locator: Locator, timeout: float = None) -> bool:
        """True if the element becomes visible within ``timeout`` (default SHORT_WAIT)."""
        try:
            self._wait(timeout or settings.SHORT_WAIT).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_for_text(self, locator: Locator, text: str, timeout: float = None) -> bool:
        """True if ``text`` appears inside the element within the timeout."""
        try:
            self._wait(timeout).until(EC.text_to_be_present_in_element(locator, text))
            return True
        except TimeoutException:
            return False

    def wait_for_url_contains(self, fragment: str, timeout: float = None) -> bool:
        try:
            self._wait(timeout).until(EC.url_contains(fragment))
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------- shared header
    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def wait_for_page_title(self, expected: str, timeout: float = None) -> bool:
        return self.wait_for_text(self.PAGE_TITLE, expected, timeout)

    def cart_count(self) -> int:
        """Number shown on the cart badge (0 when the badge is not displayed)."""
        try:
            badges = self.driver.find_elements(*self.CART_BADGE)
            if badges and badges[0].text.strip():
                return int(badges[0].text.strip())
        except StaleElementReferenceException:
            return -1  # page re-rendered mid-read; the caller's wait will retry
        return 0

    def wait_for_cart_count(self, expected: int, timeout: float = None) -> bool:
        """True if the cart badge shows ``expected`` within the timeout."""
        try:
            self._wait(timeout or settings.SHORT_WAIT).until(
                lambda _driver: self.cart_count() == expected
            )
            return True
        except TimeoutException:
            return False

    def open_cart(self) -> None:
        self.click(self.CART_LINK, "cart icon")

    def logout(self) -> None:
        self.click(self.MENU_BUTTON, "menu button")
        self.click(self.LOGOUT_LINK, "Logout link")
