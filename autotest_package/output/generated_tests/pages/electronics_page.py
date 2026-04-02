from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

class ElectronicsPage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.url = "https://example.com/electronics"

    def get_product_list(self):
        self.driver.get(self.url)
        product_list = self.driver.find_elements(By.CSS_SELECTOR, ".product-list > li")
        return product_list

    def select_product(self, product_name):
        product_list = self.get_product_list()
        for product in product_list:
            if product.text == product_name:
                product.click()
                break