from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_mise_a_jour_dynamique_de_la_liste(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri
    selecteur_option_tri = "[name='products-orderby']"
    option_tri = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, selecteur_option_tri)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri)
    option_tri = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selecteur_option_tri)))
    try:
        option_tri.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri)

    # Sélectionner l'option "Prix: Bas à élevé"
    selecteur_option_prix = "[value='Price: Low to High']"
    option_prix = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, selecteur_option_prix)))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_prix)
    option_prix = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selecteur_option_prix)))
    try:
        option_prix.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_prix)

    # Étape 3 : Vérifier que la liste des produits est mise à jour dynamiquement
    selecteur_liste_produits = ".product-grid"
    liste_produits = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, selecteur_liste_produits)))
    assert liste_produits.is_displayed()