from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

class HomePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.url = "https://example.com"

    def navigate_to_electronics(self):
        self.driver.get(self.url)
        electronics_link = self.driver.find_element(By.LINK_TEXT, "Electronics")
        electronics_link.click()

    def navigate_to_product(self, product_name):
        self.driver.get(self.url)
        product_link = self.driver.find_element(By.LINK_TEXT, product_name)
        product_link.click()