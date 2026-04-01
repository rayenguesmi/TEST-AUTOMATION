from base_page import BasePage

class ProductPage(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_product(self, product_url):
        self.navigate_to(product_url)

    def assert_product_detail_visible(self):
        product_detail = self.wait_for_element_visible("//div[@class='product-detail']")
        return product_detail.is_displayed()

    def click_on_add_to_cart(self):
        add_to_cart_locator = "//button[@data-test='add-to-cart']"
        self.click_on(add_to_cart_locator)