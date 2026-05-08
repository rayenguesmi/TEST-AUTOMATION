from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_acces_page_produit(driver: WebDriver):
    # Étape 1 : Accéder à la page https://demowebshop.tricentis.com/electronics
    url = "https://demowebshop.tricentis.com/electronics"
    driver.get(url)

    # Étape 2 : Rechercher un produit spécifique (par exemple, 'HTC One M9')
    produit = "HTC One M9"
    search_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "small-searchterms")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
    search_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "small-searchterms")))
    try:
        search_input.send_keys(produit)
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].value = '" + produit + "';", search_input)

    search_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Search']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
    search_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Search']")))
    try:
        search_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", search_button)

    # Étape 3 : Vérifier que la page affiche les détails du produit spécifique
    produit_title = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//h2[text()='" + produit + "']")))
    assert produit_title.text == produit