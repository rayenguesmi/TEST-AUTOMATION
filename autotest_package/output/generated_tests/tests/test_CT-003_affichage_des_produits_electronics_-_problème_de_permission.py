import pytest
from pages.login_page import LoginPage
from pages.error_page import ErrorPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

@pytest.mark.usefixtures("driver")
class TestCT003:
    def test_affichage_produits_electronics_probleme_permission(self, driver):
        # Étape 1 : Se connecter avec un utilisateur non autorisé
        login_page = LoginPage(driver)
        login_page.se_connecter("user@example.com", "password")

        # Étape 2 : Accéder à la page Electronics
        driver.get("https://example.com/electronics")

        # Étape 3 : Visualiser la page
        error_page = ErrorPage(driver)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='error-message']"))
        )

        # Vérification du message d'erreur
        assert error_page.get_message_erreur() == "Vous n'avez pas les permissions nécessaires pour accéder à cette page."

        # Vérification de la présence du message d'erreur dans la page
        assert "erreur d'autorisation" in driver.page_source.lower()

    def test_affichage_produits_electronics_probleme_permission_failure(self, driver):
        try:
            # Étape 1 : Se connecter avec un utilisateur non autorisé
            login_page = LoginPage(driver)
            login_page.se_connecter("user@example.com", "password")

            # Étape 2 : Accéder à la page Electronics
            driver.get("https://example.com/electronics")

            # Étape 3 : Visualiser la page
            error_page = ErrorPage(driver)
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='error-message']"))
            )

            # Vérification du message d'erreur
            assert error_page.get_message_erreur() == "Vous n'avez pas les permissions nécessaires pour accéder à cette page."

            # Vérification de la présence du message d'erreur dans la page
            assert "erreur d'autorisation" in driver.page_source.lower()
        except AssertionError as e:
            # Capture d'un screenshot en cas d'échec
            screenshot_path = os.path.join(os.getcwd(), "screenshots")
            if not os.path.exists(screenshot_path):
                os.makedirs(screenshot_path)
            driver.save_screenshot(os.path.join(screenshot_path, "CT-003_failure.png"))
            raise e