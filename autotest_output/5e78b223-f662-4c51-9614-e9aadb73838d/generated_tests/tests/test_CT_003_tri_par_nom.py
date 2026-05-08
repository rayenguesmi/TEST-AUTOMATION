from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_tri_par_nom(driver: WebDriver):
    # Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Sélectionner l'option de tri 'Nom: A à Z'
    option_tri = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[value='Name: A to Z']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri)
    option_tri = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[value='Name: A to Z']")))
    try:
        option_tri.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri)

    # Vérifier que les produits sont triés par nom
    produits = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product-title")))
    noms_produits = [produit.text for produit in produits]
    assert noms_produits == sorted(noms_produits)