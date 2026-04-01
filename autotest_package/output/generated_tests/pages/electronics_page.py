from selenium.webdriver.remote.webdriver import WebDriver
from .base_page import BasePage

class ElectronicsPage(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_electronics(self):
        self.navigate_to("https://example.com/electronics")

    def assert_product_list_visible(self):
        product_list = self.wait_for_element_visible("//div[@class='product-list']")
        return product_list.is_displayed()

    def click_on_product(self, product_name):
        product_link_locator = f"//a[@href='#'][contains(text(), '{product_name}')]"
        self.click_on(product_link_locator)