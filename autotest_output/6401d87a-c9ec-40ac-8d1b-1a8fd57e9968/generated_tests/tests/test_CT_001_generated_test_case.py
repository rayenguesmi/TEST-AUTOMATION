from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_affichage_produits_electroniques(driver: WebDriver):
    # Étape 1 : Accéder à la page https://demowebshop.tricentis.com/electronics
    driver.get("https://demowebshop.tricentis.com/electronics")

    # Étape 2 : Vérifier que la page affiche une liste de produits électroniques
    produits = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-grid"))
    )
    assert len(produits) > 0, "La page ne contient pas de produits électroniques"

    # Étape 3 : Vérifier que chaque produit contient un nom, un prix et une image
    for produit in produits:
        nom_produit = WebDriverWait(produit, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-title"))
        )
        prix_produit = WebDriverWait(produit, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".price"))
        )
        image_produit = WebDriverWait(produit, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img"))
        )
        assert nom_produit.text != "", "Le produit ne contient pas de nom"
        assert prix_produit.text != "", "Le produit ne contient pas de prix"
        assert image_produit.get_attribute("src") != "", "Le produit ne contient pas d'image"

    # Étape 4 : Cliquez sur un produit pour vérifier que les produits sont cliquables
    premier_produit = produits[0]
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".item-grid:first-child"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".item-grid:first-child"))
    )
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Vérifier que la page de détails du produit est affichée
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-details"))
    )