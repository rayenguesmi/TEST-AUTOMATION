import pytest
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Add the pages directory to sys.path to resolve imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages"))

@pytest.fixture(scope="session")
def browser_name(request):
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def headless(request):
    return request.config.getoption("--headless")

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--headless", action="store", default="true")

@pytest.fixture
def driver(browser_name, headless):
    if browser_name == "chrome":
        options = Options()
        if headless == "true":
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        raise ValueError(f"Browser {browser_name} not supported yet.")
    
    yield driver
    
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    
    # set a report attribute for each phase of a test, which can be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    yield
    # Check if test failed
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_id = request.node.name.split('_')[1] # Assumes test_TCXXX_...
        screenshot_name = f"{test_id}_failure.png"
        screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        driver.save_screenshot(os.path.join(screenshots_dir, screenshot_name))