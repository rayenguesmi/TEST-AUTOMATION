from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
import time


class BasePage:
    """Hardened base - WebDriverWait(20), scrollIntoView, JS-click fallback."""

    TIMEOUT = 20

    def __init__(self, driver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, self.TIMEOUT)

    def _scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center',inline:'nearest'});",
            element,
        )
        time.sleep(0.3)

    def wait_for_presence(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def safe_click(self, locator):
        el = self.wait_for_presence(locator)
        self._scroll_to(el)
        el = self.wait_for_clickable(locator)
        try:
            el.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", el)

    def safe_send_keys(self, locator, text: str):
        el = self.wait_for_presence(locator)
        self._scroll_to(el)
        el = self.wait_for_visible(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator) -> str:
        el = self.wait_for_visible(locator)
        self._scroll_to(el)
        return el.text

    def is_visible(self, locator) -> bool:
        try:
            return self.wait_for_visible(locator).is_displayed()
        except TimeoutException:
            return False

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
