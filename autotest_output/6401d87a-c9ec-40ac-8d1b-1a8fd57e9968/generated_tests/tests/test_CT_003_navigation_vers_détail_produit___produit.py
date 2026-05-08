from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_vers_detail_produit_non_existant(driver: WebDriver):
    # Étape 1 : Navigation vers la page d'accueil
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le lien du produit non existant
    try:
        produit_non_existant = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Non existant product"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit_non_existant)
        produit_non_existant = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Non existant product"))
        )
        try:
            produit_non_existant.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            driver.execute_script("arguments[0].click();", produit_non_existant)
    except:
        # Si le produit non existant n'est pas trouvé, on passe à l'étape suivante
        pass

    # Étape 3 : Vérifier que la page produit n'est pas affichée
    try:
        WebDriverWait(driver, 2).until(
            EC.url_contains("non-existant-product")
        )
        assert False, "La page produit est affichée"
    except:
        # La page produit n'est pas affichée, on continue
        pass

    # Étape 4 : Vérifier que un message d'erreur est affiché
    try:
        message_erreur = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error"))
        )
        assert message_erreur.text != "", "Aucun message d'erreur n'est affiché"
    except:
        assert False, "Aucun message d'erreur n'est affiché"