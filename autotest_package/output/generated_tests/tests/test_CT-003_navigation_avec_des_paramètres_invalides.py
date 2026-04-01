import pytest
from pages.login_page import LoginPage
from pages.error_page import ErrorPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestNavigationAvecParametresInvalides:
    def test_navigation_avec_parametres_invalides(self, driver):
        # Étape 1 : Se connecter avec l'email 'test@example.com' et le mot de passe 'password123'
        login_page = LoginPage(driver)
        login_page.se_connecter("test@example.com", "password123")

        # Étape 2 : Saisir l'URL d'une page avec des paramètres invalides (par exemple, '/produits?page=abc')
        url = "http://example.com/produits?page=abc"
        driver.get(url)

        # Étape 3 : Vérifier que l'erreur 'Paramètres invalides' est affichée
        error_page = ErrorPage(driver)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='error-message']"))
        )
        erreur_attendue = "Paramètres invalides"
        erreur_affichee = error_page.get_erreur_message()
        assert erreur_attendue in erreur_affichee, f"Erreur attendue : {erreur_attendue}, Erreur affichée : {erreur_affichee}"

        # Capture d'un screenshot en cas d'échec
        try:
            assert erreur_attendue in erreur_affichee
        except AssertionError as e:
            screenshot_name = f"CT-003_failure_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png"
            driver.save_screenshot(screenshot_name)
            raise e