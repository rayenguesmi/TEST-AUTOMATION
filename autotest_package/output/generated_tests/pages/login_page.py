from selenium.webdriver.remote.webdriver import WebDriver
from base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.url = "https://demowebshop.tricentis.com/login"

    def login(self, email: str, password: str):
        self.driver.find_element("name", "Email").send_keys(email)
        self.driver.find_element("name", "Password").send_keys(password)
        self.driver.find_element("xpath", "//input[@value='Log in']").click()