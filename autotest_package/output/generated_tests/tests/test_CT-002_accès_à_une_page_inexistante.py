import pytest
from pages.login_page import LoginPage
from pages.error_page import ErrorPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

@pytest.mark.usefixtures("driver")
class TestCT002:
    def test_access_inexistent_page(self, driver):
        # Étape 1 : Se connecter avec l'email 'test@example.com' et le mot de passe 'password123'
        login_page = LoginPage(driver)
        login_page.open()
        login_page.set_email("test@example.com")
        login_page.set_password("password123")
        login_page.click_submit()

        # Étape 2 : Saisir l'URL d'une page inexistante (par exemple, '/produits?page=1000')
        driver.get("http://example.com/produits?page=1000")

        # Étape 3 : Vérifier que l'erreur 'Page non trouvée' est affichée
        error_page = ErrorPage(driver)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h1[text()='Page non trouvée']"))
        )
        assert error_page.get_error_message() == "Page non trouvée"

        # Vérification de l'erreur
        try:
            assert error_page.get_error_message() == "Page non trouvée"
        except AssertionError:
            # Capture d'un screenshot en cas d'échec
            screenshot_path = os.path.join(os.getcwd(), "screenshots")
            if not os.path.exists(screenshot_path):
                os.makedirs(screenshot_path)
            driver.save_screenshot(os.path.join(screenshot_path, "CT-002_failure.png"))
            raise