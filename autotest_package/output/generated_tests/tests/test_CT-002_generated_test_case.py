import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.electronics_page import ElectronicsPage
from pages.error_page import ErrorPage
from pages.product_page import ProductPage
import time

@pytest.mark.usefixtures("driver")
class TestCT002:
    def test_ct002(self, driver: WebDriver):
        # Étape 1 : Se connecter au site web avec l'email 'user@example.com' et le mot de passe 'password123'
        login_page = LoginPage(driver)
        login_page.go_to()
        login_page.email_input.send_keys("user@example.com")
        login_page.password_input.send_keys("password123")
        login_page.login_button.click()

        # Étape 2 : Cliquer sur le produit 'Produit 2' indisponible
        electronics_page = ElectronicsPage(driver)
        electronics_page.go_to()
        electronics_page.product_2_link.click()

        # Étape 3 : Vérifier que la page produit n'est pas affichée et qu'un message d'erreur est affiché
        error_page = ErrorPage(driver)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, error_page.error_message_css))
            )
            assert error_page.error_message.text != ""
        except AssertionError:
            driver.save_screenshot(f"CT-002_failure.png")
            pytest.fail("La page produit est affichée ou le message d'erreur n'est pas affiché")