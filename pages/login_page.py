"""Page object for the SauceDemo login page."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-test='login-button']")
    ERROR_BANNER = (By.CSS_SELECTOR, "[data-test='error']")

    def open(self, path: str = "") -> "LoginPage":
        super().open(path)
        return self

    def login(self, username: str, password: str) -> None:
        """Fill in the credentials and click Login (either field may be blank)."""
        self.type_text(self.USERNAME_INPUT, username, "Username")
        self.type_text(self.PASSWORD_INPUT, password, "Password")
        self.click(self.LOGIN_BUTTON, "Login button")

    def is_error_displayed(self) -> bool:
        return self.is_visible(self.ERROR_BANNER)

    def get_error_message(self) -> str:
        """Text of the error banner, or '' if no banner is shown."""
        return self.get_text(self.ERROR_BANNER) if self.is_error_displayed() else ""

    def is_on_login_page(self) -> bool:
        """True when the login form is displayed (i.e. we are NOT logged in)."""
        return self.is_visible(self.LOGIN_BUTTON)
