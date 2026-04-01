from base_page import BasePage

class PaginationPage(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_pagination(self):
        self.navigate_to("https://example.com/pagination")

    def click_next_button(self):
        next_button_locator = "//button[@data-test='next']"
        self.click_on(next_button_locator)