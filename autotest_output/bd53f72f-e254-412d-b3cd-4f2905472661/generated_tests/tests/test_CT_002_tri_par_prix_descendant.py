from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_tri_prix_descendant(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Sélectionner l'option de tri 'Prix: Élevé à bas'
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

    # Sélectionner l'option 'Prix: Élevé à bas'
    option_prix_elevé_bas = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//option[text()='Prix: Élevé à bas']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_prix_elevé_bas)
    option_prix_elevé_bas = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//option[text()='Prix: Élevé à bas']"))
    )
    try:
        option_prix_elevé_bas.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", option_prix_elevé_bas)

    # Étape 3 : Vérifier que les produits sont triés par prix descendant
    produits = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-grid .product"))
    )
    prix_produits = []
    for produit in produits:
        prix_produit = WebDriverWait(produit, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".price"))
        )
        prix_produit = prix_produit.text.replace("$", "").replace(",", "")
        prix_produit = float(prix_produit)
        prix_produits.append(prix_produit)

    # Vérifier que les prix sont triés par ordre descendant
    prix_produits_tries = sorted(prix_produits, reverse=True)
    assert prix_produits == prix_produits_tries