from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_recherche_produit_inexistant(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Saisir 'produit_inexistant' dans le champ de recherche
    search_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "small-searchterms")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_input)
    search_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "small-searchterms")))
    search_input.send_keys("produit_inexistant")

    # Étape 3 : Cliquez sur le bouton de recherche
    search_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Search']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
    search_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Search']")))
    try:
        search_button.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", search_button)

    # Vérification du résultat attendu
    result_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='no-result']")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", result_message)
    assert result_message.text == "No products were found that matched your criteria."