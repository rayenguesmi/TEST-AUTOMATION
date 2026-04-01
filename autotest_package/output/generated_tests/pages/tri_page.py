from base_page import BasePage

class TriPage(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_tri(self):
        self.navigate_to("https://example.com/tri")

    def select_tri_option(self, tri_option):
        tri_option_locator = f"//select[@name='tri-option']/{tri_option}"
        self.driver.find_element_by_xpath(tri_option_locator).click()

    def assert_tri_result_visible(self):
        tri_result = self.wait_for_element_visible("//div[@class='tri-result']")
        return tri_result.is_displayed()