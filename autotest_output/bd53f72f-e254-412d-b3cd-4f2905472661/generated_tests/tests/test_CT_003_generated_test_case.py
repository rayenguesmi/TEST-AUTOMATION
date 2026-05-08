from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

def test_consulter_detalles_produit_url_invalide(driver: WebDriver):
    # Étape 1 : Se rendre sur la page https://demowebshop.tricentis.com/product/123456
    url = "https://demowebshop.tricentis.com/product/123456"
    driver.get(url)

    # Étape 2 : Vérifier que la page d'erreur s'affiche
    error_message_locator = By.XPATH, "//div[@class='error-page']"
    error_message = WebDriverWait(driver, 20).until(EC.presence_of_element_located(error_message_locator))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", error_message)
    assert error_message.is_displayed(), "La page d'erreur ne s'affiche pas"