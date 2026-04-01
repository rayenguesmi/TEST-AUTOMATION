import pytest
from selenium.webdriver.common.by import By

def test_CT006_search_product_exists(driver):
    driver.get("https://demowebshop.tricentis.com/")
    search_input = driver.find_element(By.ID, "small-searchterms")
    search_input.send_keys("Phone")
    driver.find_element(By.CSS_SELECTOR, ".search-box-button").click()
    assert "Search" in driver.title
    assert len(driver.find_elements(By.CSS_SELECTOR, ".product-item")) > 0
