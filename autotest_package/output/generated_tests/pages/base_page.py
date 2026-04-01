from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def navigate_to(self, url):
        self.driver.get(url)

    def wait_for_element_visible(self, element_locator):
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, element_locator)))

    def click_on(self, element_locator):
        self.driver.find_element_by_xpath(element_locator).click()

    def assert_error_message(self, element_locator):
        error_message = self.driver.find_element_by_xpath(element_locator).text
        assert "Error" in error_message

    def verify_text(self, expected_text):
        actual_text = self.driver.find_element_by_tag_name("body").text
        assert expected_text in actual_text