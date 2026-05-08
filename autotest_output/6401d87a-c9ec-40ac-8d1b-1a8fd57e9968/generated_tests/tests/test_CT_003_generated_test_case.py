from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_CT_003(driver: WebDriver):
    # Étape 1 : Accéder à la page https://demowebshop.tricentis.com/electronics sans être connecté
    url = "https://demowebshop.tricentis.com/electronics"
    driver.get(url)

    # Étape 2 : Vérifier que la page affiche une liste de produits électroniques sans possibilité d'achat
    produits = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product")))
    assert len(produits) > 0, "La page ne contient pas de produits électroniques"

    # Vérifier que les boutons d'achat sont présents mais non cliquables
    boutons_achat = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product .add-to-cart-button")))
    for bouton in boutons_achat:
        bouton = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".product-grid .product .add-to-cart-button")))
        try:
            bouton.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            # Le bouton d'achat ne devrait pas être cliquable sans être connecté
            pass
        else:
            assert False, "Le bouton d'achat est cliquable sans être connecté"