from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

class ProductPage:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def get_product_details(self):
        product_name = self.driver.find_element(By.CSS_SELECTOR, ".product-name").text
        product_description = self.driver.find_element(By.CSS_SELECTOR, ".product-description").text
        product_price = self.driver.find_element(By.CSS_SELECTOR, ".product-price").text
        return {
            "name": product_name,
            "description": product_description,
            "price": product_price
        }

    def add_to_cart(self):
        add_to_cart_button = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart")
        add_to_cart_button.click()