from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_tri_prix_ascendant(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner l'option de tri 'Prix: Bas à élevé'
    select_sort = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "products-orderby"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_sort)
    select_sort = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "products-orderby"))
    )
    try:
        select_sort.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", select_sort)

    # Sélectionner l'option 'Prix: Bas à élevé'
    option_tri = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//option[text()='Prix: Bas à élevé']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_tri)
    option_tri = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//option[text()='Prix: Bas à élevé']"))
    )
    try:
        option_tri.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_tri)

    # Étape 3 : Vérifier que les produits sont triés par prix ascendant
    produits = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product-price"))
    )
    prix = [float(p.text.replace("$", "")) for p in produits]
    assert prix == sorted(prix), "Les produits ne sont pas triés par prix ascendant"