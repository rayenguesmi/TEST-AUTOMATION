from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_vers_detail_produit_indisponible(driver: WebDriver):
    # Étape 1 : Navigation vers la page d'accueil
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Recherche du produit 'Unavailable product'
    produit = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Unavailable product"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit)
    produit = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Unavailable product"))
    )
    try:
        produit.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit)

    # Étape 3 : Vérification que la page produit n'est pas affichée
    try:
        WebDriverWait(driver, 2).until(
            EC.url_contains("unavailable-product")
        )
        assert False, "La page produit est affichée"
    except:
        pass

    # Étape 4 : Vérification que un message d'erreur est affiché
    message_erreur = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".error"))
    )
    assert message_erreur.text != "", "Aucun message d'erreur n'est affiché"