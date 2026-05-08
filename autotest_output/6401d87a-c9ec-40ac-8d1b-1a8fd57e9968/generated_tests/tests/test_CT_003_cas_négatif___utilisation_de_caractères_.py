from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_ct_003(driver: WebDriver):
    # Étape 1 : Ouvrir le site
    driver.get("https://demowebshop.tricentis.com/")

    # Étape 2 : Saisir une URL avec des caractères spéciaux (#, $, etc.)
    url_inexistante = "https://demowebshop.tricentis.com/#$inexistante"
    driver.get(url_inexistante)

    # Étape 3 : Vérifier que l'utilisateur est toujours sur la page d'accueil
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".header-logo")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".header-logo")))
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Étape 4 : Vérifier que l'utilisateur n'a pas accédé à une page inexistante
    assert driver.title == "Demo Web Shop"

    # Étape 5 : Vérifier que l'utilisateur est toujours sur la page d'accueil
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".header-logo")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".header-logo")))
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)

    # Étape 6 : Vérifier que l'utilisateur n'a pas accédé à une page d'erreur
    assert "erreur" not in driver.page_source.lower()
    assert "error" not in driver.page_source.lower()