import pytest
from pages.login_page import LoginPage
from pages.electronics_page import ElectronicsPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestNavigationPremierePage:
    def test_navigation_premiere_page(self, driver):
        # Étape 1 : Se connecter avec l'email 'test@example.com' et le mot de passe 'password123'
        login_page = LoginPage(driver)
        login_page.se_connecter("test@example.com", "password123")

        # Étape 2 : Cliquer sur le bouton 'Previous' sur la première page
        electronics_page = ElectronicsPage(driver)
        electronics_page.clique_bouton_previous()

        # Étape 3 : Vérifier que la page ne change pas
        WebDriverWait(driver, 10).until(
            EC.url_to_be(driver.current_url)
        )
        assert driver.current_url == electronics_page.url

        # Vérification de la page
        assert electronics_page.titre_page.text == "Electronics"

    def test_navigation_premiere_page_failure(self, driver):
        try:
            # Étape 1 : Se connecter avec l'email 'test@example.com' et le mot de passe 'password123'
            login_page = LoginPage(driver)
            login_page.se_connecter("test@example.com", "password123")

            # Étape 2 : Cliquer sur le bouton 'Previous' sur la première page
            electronics_page = ElectronicsPage(driver)
            electronics_page.clique_bouton_previous()

            # Étape 3 : Vérifier que la page ne change pas
            WebDriverWait(driver, 10).until(
                EC.url_to_be(driver.current_url)
            )
            assert driver.current_url == electronics_page.url

            # Vérification de la page
            assert electronics_page.titre_page.text == "Electronics"
        except AssertionError as e:
            # Capture d'un screenshot en cas d'échec
            driver.save_screenshot("CT-004_failure.png")
            raise AssertionError(e)