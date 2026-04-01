from base_page import BasePage

class CartPage(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_cart(self):
        self.navigate_to("https://example.com/cart")

    def assert_cart_contents_visible(self):
        cart_contents = self.wait_for_element_visible("//div[@class='cart-contents']")
        return cart_contents.is_displayed()