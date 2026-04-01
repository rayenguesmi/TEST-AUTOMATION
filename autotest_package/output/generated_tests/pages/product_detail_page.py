from base_page import BasePage
from selenium.webdriver.common.by import By

class ProductDetailPage(BasePage):
    PRODUCT_NAME_LOCATOR = (By.CSS_SELECTOR, ".product-name")
    PRODUCT_DESCRIPTION_LOCATOR = (By.CSS_SELECTOR, ".product-description")
    PRODUCT_PRICE_LOCATOR = (By.CSS_SELECTOR, ".product-price")
    ADD_TO_CART_BUTTON_LOCATOR = (By.CSS_SELECTOR, ".add-to-cart-button")

    def get_product_name(self):
        return self.get_element_text(self.PRODUCT_NAME_LOCATOR)

    def get_product_description(self):
        return self.get_element_text(self.PRODUCT_DESCRIPTION_LOCATOR)

    def get_product_price(self):
        return self.get_element_text(self.PRODUCT_PRICE_LOCATOR)

    def click_add_to_cart(self):
        self.click_element(self.ADD_TO_CART_BUTTON_LOCATOR)