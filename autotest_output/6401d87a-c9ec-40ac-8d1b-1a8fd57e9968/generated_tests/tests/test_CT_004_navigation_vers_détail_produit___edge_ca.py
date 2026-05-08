from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_vers_detail_produit(driver: WebDriver):
    # Étape 1 : Navigation vers la page d'accueil
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Recherche du produit avec un nom très long
    produit = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Produit avec un nom très très très long"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit)
    produit = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Produit avec un nom très très très long"))
    )
    try:
        produit.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit)

    # Étape 3 : Vérification de la page produit
    WebDriverWait(driver, 20).until(
        EC.url_contains("produit-avec-un-nom-tres-tres-tres-long")
    )
    description = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-description"))
    )
    prix = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-price"))
    )
    bouton_ajouter_au_panier = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[value='Add to cart']"))
    )

    # Vérification des éléments de la page produit
    assert description.is_displayed()
    assert prix.is_displayed()
    assert bouton_ajouter_au_panier.is_displayed()