from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_tri_prix_ascendant(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner l'option de tri 'Prix: Bas à élevé'
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_sort_by)
    select_sort_by = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "products-orderby"))
    )
    try:
        select_sort_by.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", select_sort_by)

    # Sélectionner l'option 'Prix: Bas à élevé'
    option_tri = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//option[text()='Price: Low to High']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri)
    option_tri = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//option[text()='Price: Low to High']"))
    )
    try:
        option_tri.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri)

    # Étape 3 : Vérifier que les produits sont triés par prix ascendant
    produits = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product-price"))
    )
    prix_produits = [float(produit.text.replace("$", "")) for produit in produits]
    assert prix_produits == sorted(prix_produits), "Les produits ne sont pas triés par prix ascendant"