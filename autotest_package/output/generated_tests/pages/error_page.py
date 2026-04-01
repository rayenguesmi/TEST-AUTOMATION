from base_page import BasePage
from selenium.webdriver.common.by import By

class ErrorPage(BasePage):
    ERROR_MESSAGE_LOCATOR = (By.CSS_SELECTOR, ".error-message")

    def get_error_message(self):
        return self.get_element_text(self.ERROR_MESSAGE_LOCATOR)