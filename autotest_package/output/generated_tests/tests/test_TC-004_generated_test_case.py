import pytest
from pages.tri_page import TriPage
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.fixture
def driver():
    return WebDriver()

class TestTriPage:
    @pytest.mark.parametrize("tri_option", ["prixAscendant", "nomInvaild", "prixDescendant", "nom"])
    def test_tri(self, driver, tri_option):
        tri_page = TriPage(driver)
        tri_page.open()
        tri_page.select_tri_option(tri_option)

        if tri_option in ["prixAscendant", "nom"]:
            assert tri_page.is_sorted_by_price_or_name()
        elif tri_option == "nomInvaild":
            assert tri_page.is_error_message_displayed("Erreur: Option de tri invalide")
        elif tri_option == "prixDescendant" and not tri_page.are_products_present():
            assert True  # No assertion needed, as expected result is empty list
        else:
            pytest.fail(f"Unexpected tri option '{tri_option}'")

        if driver.session_status == 'failed':
            driver.get_screenshot_as_file(f"{tri_option}_failure.png")