import pytest
from pages.electronics_page import ElectronicsPage
from pages.login_page import LoginPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestCT003:
    def test_ct003(self, driver):
        # Étape 1 : Ouvrir le site et se connecter
        login_page = LoginPage(driver)
        login_page.se_connecter("username", "password")

        # Étape 2 : Accéder à la page des produits électroniques
        electronics_page = ElectronicsPage(driver)
        electronics_page.acceder_a_la_page()

        # Étape 3 : Sélectionner l'option de tri 'Nom'
        electronics_page.selectionner_option_tri("Nom")

        # Étape 4 : Entrer des caractères spéciaux dans le champ de recherche
        caracteres_speciaux = "!@#$%"
        electronics_page.entrer_caracteres_speciaux(caracteres_speciaux)

        # Étape 5 : Vérifier que la liste des produits est mise à jour avec les noms contenant les caractères spéciaux
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#produits"))
            )
            produits = driver.find_elements(By.CSS_SELECTOR, "#produits li")
            for produit in produits:
                assert caracteres_speciaux in produit.text
        except AssertionError:
            driver.save_screenshot("CT-003_failure.png")
            pytest.fail("La liste des produits n'est pas triée par nom avec les caractères spéciaux")

        # Vérification finale
        assert electronics_page.est_tri_par_nom(caracteres_speciaux)

        # Capture d'écran en cas de succès
        driver.save_screenshot("CT-003_success.png")