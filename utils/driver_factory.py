"""Creates configured Chrome WebDriver instances.

Driver resolution order:
  1. CHROMEDRIVER_PATH environment variable (explicit path), if set
  2. webdriver-manager (downloads a matching driver automatically)
  3. Selenium Manager (built into Selenium 4.6+) as the final fallback
"""
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.logger import get_logger


def _build_service() -> Service:
    log = get_logger()
    explicit_path = os.getenv("CHROMEDRIVER_PATH")
    if explicit_path:
        return Service(explicit_path)

    if os.getenv("USE_WEBDRIVER_MANAGER", "1") == "1":
        try:
            from webdriver_manager.chrome import ChromeDriverManager

            return Service(ChromeDriverManager().install())
        except Exception as exc:  # noqa: BLE001 - any failure -> fall back
            log.warning("webdriver-manager failed (%s); falling back to Selenium Manager", exc)
    return Service()  # Selenium Manager resolves the driver itself


def create_driver(headless: bool = False) -> webdriver.Chrome:
    """Return a ready-to-use Chrome driver."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    # Chrome shows a "Change your password" breach popup after logging in with
    # SauceDemo's well-known credentials; it blocks clicks, so switch it off.
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-features=PasswordLeakDetection,PasswordCheck")

    # Needed only on Linux/CI containers; harmless to leave unset on Windows.
    if os.getenv("CHROME_NO_SANDBOX") == "1":
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=_build_service(), options=options)
    driver.implicitly_wait(0)  # explicit waits only - never mix with implicit waits
    return driver
