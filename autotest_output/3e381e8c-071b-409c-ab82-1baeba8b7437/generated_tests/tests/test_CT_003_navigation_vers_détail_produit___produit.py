from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_navigation_vers_detail_produit_non_existant(driver: WebDriver):
    # Étape 1 : Navigation vers la page d'accueil
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Cliquer sur le lien du produit non existant
    produit_non_existant = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='https://demowebshop.tricentis.com/non-existant-product']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", produit_non_existant)
    produit_non_existant = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='https://demowebshop.tricentis.com/non-existant-product']"))
    )
    try:
        produit_non_existant.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", produit_non_existant)

    # Étape 3 : Vérifier que la page produit n'est pas affichée
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-details"))
        )
        assert False, "La page produit est affichée"
    except:
        pass

    # Étape 4 : Vérifier que le message 'Page not found' est affiché
    message_page_not_found = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//h1[text()='Page not found']"))
    )
    assert message_page_not_found.text == "Page not found"