from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_CT_005(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner une option de tri qui ne correspond à aucun produit
    # Ici, nous allons sélectionner l'option de tri "Z - A" pour les prix
    # car cela ne correspond à aucun produit
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name='products-orderby']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[name='products-orderby']")))
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Sélectionner l'option "Z - A" pour les prix
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[value='6']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[value='6']")))
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Étape 3 : Vérifier que la liste des produits est vide
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-grid")))
    produits = element.find_elements(By.CSS_SELECTOR, ".product-item")
    assert len(produits) == 0, "La liste des produits n'est pas vide"