from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_recherche_produit_avec_caracteres_speciaux(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Saisir 'phone@' dans le champ de recherche
    search_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "small-searchterms")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
    search_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "small-searchterms")))
    search_input.send_keys("phone@")

    # Étape 3 : Cliquez sur le bouton de recherche
    search_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Search']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
    search_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Search']")))
    try:
        search_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", search_button)

    # Vérification des résultats de recherche
    search_results = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-grid")))
    assert "phone" in search_results.text, "Les résultats de recherche ne contiennent pas le mot-clé 'phone'"