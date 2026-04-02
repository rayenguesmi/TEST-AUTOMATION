from pages.search_page import SearchPage
from selenium.webdriver.remote.webdriver import WebDriver

def test_search_existing_product(driver: WebDriver):
    search_page = SearchPage(driver)
    search_page.open()
    
    search_page.enter_search_term("phone")
    search_page.submit_search()
    
    assert search_page.is_element_visible(".search-results"), "Search results are not visible"
    assert search_page.get_elements_count(".product-item") > 0, "No products found"

def test_search_non_existing_product(driver: WebDriver):
    search_page = SearchPage(driver)
    search_page.open()
    
    search_page.enter_search_term("xyz123")
    search_page.submit_search()
    
    assert search_page.is_element_visible(".search-results"), "Search results are not visible"
    assert search_page.is_element_visible(".no-results-message"), "No results message is not visible"

def test_search_empty_product(driver: WebDriver):
    search_page = SearchPage(driver)
    search_page.open()
    
    search_page.enter_search_term("")
    search_page.submit_search()
    
    assert search_page.is_element_visible(".search-results"), "Search results are not visible"
    assert search_page.is_element_visible(".no-results-message"), "No results message is not visible"