from selenium.webdriver.remote.webdriver import WebDriver
import pytest
from pages.pagination_page import PaginationPage

@pytest.mark.usefixtures("driver")
class TestPagination:

    @pytest.mark.id("T-005-01")
    def test_pagination_next(self, driver):
        pagination_page = PaginationPage(driver)
        pagination_page.open_products_page()
        pagination_page.click_next_button()
        assert pagination_page.products_have_changed(), "Les nouveaux produits ne sont pas affichés"

    @pytest.mark.id("T-005-02")
    def test_pagination_next_invalid(self, driver):
        pagination_page = PaginationPage(driver)
        pagination_page.open_products_page()
        while True:
            try:
                pagination_page.click_next_button()
            except Exception as e:
                break
        assert pagination_page.is_on_last_page(), "L'utilisateur n'est pas redirigé vers la dernière page disponible"

    @pytest.mark.id("T-005-03")
    def test_pagination_previous_invalid(self, driver):
        pagination_page = PaginationPage(driver)
        pagination_page.open_products_page()
        assert pagination_page.is_on_first_page(), "L'utilisateur n'est pas sur la première page"

    @pytest.mark.id("T-005-04")
    def test_pagination_single_page(self, driver):
        pagination_page = PaginationPage(driver)
        pagination_page.open_category_with_single_page()
        assert not pagination_page.are_next_and_previous_buttons_visible(), "Les boutons de pagination sont affichés"