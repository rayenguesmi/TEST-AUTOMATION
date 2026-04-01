import os
import json
import yaml
from typing import Dict, Any, List
from utils.llm_client import LLMClient
from utils.logger import setup_logger

logger = setup_logger("SeleniumGenerator")

class SeleniumGenerator:
    """Generates Selenium Python scripts (POM pattern) from test cases."""

    def __init__(self, config_path: str):
        """Initializes generator with config and prompts."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.system_prompt = self.config['prompts']['selenium_generation']
        self.llm_client = LLMClient(config_path)

    def generate_scripts(self, test_cases: List[Dict[str, Any]], output_dir: str, url_cible: str = None):
        """Generates POM structure and pytest scripts into output directory."""
        self.url_cible = url_cible
        logger.info(f"Generating Selenium scripts into: {output_dir}")
        
        # Structure creation
        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        pages_dir = os.path.join(generated_tests_dir, "pages")
        tests_dir = os.path.join(generated_tests_dir, "tests")

        for d in [generated_tests_dir, pages_dir, tests_dir]:
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "__init__.py"), 'a').close()
        
        # Generation: Step-by-step
        # 1. Base Page
        self._write_base_page(pages_dir)
        
        # 2. Conftest & Pytest Config
        self._write_conftest(generated_tests_dir)
        self._write_pytest_ini(generated_tests_dir)
        
        # 3. For each unique page name identified by LLM, we should save it.
        # To simplify, we'll ask the LLM to provide the Page Objects for the entire spec once.
        self._generate_page_objects(test_cases, pages_dir)
        
        # Collect generated page files and classes to feed to the LLM context
        page_files_context = ""
        for p_file in os.listdir(pages_dir):
            if p_file.endswith(".py") and p_file not in ("__init__.py", "base_page.py"):
                with open(os.path.join(pages_dir, p_file), "r", encoding="utf-8") as pf:
                    content = pf.read()
                    import re
                    class_names = re.findall(r'class\s+([A-Za-z0-9_]+)', content)
                    page_files_context += f"- Fichier: {p_file} | Classes: {', '.join(class_names)}\n"

        # 4. Generate the test scripts
        for case in test_cases:
            test_id = case.get('id', 'TC-Unknown')
            logger.info(f"Generating Selenium script for {test_id}")
            
            import re
            case_json = json.dumps(case, indent=2)
            url_cible = getattr(self, 'url_cible', 'https://demowebshop.tricentis.com/electronics') # Fallback if not set
            prompt_addition = f"\n\nURL du site : {url_cible}"
            prompt_addition += f"\n\nIMPORTANT: Tu DOIS utiliser UNIQUEMENT les classes Page déja créées dans le dossier pages/ et les importer correctement (ex: from pages.login_page import LoginPage). Voici les pages disponibles:\n{page_files_context}"
            prompt_addition += "\n\nRègle d'importation critique : NE FAIS PAS 'from selenium.webdriver import WebDriver'. Utilise 'from selenium.webdriver.remote.webdriver import WebDriver' à la place."
            code = self.llm_client.call(self.system_prompt + prompt_addition, case_json)
            
            # Extract code
            code_match = re.search(r'```(?:python)?\s*\n(.*?)\n\s*```', code, re.DOTALL)
            if code_match:
                code = code_match.group(1)
            
            test_file_path = os.path.join(tests_dir, f"test_{test_id}_{case.get('titre', 'unnamed').lower().replace(' ', '_')}.py")
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(code.strip())
            
            # Anti rate-limit
            import time
            time.sleep(5)

    def _generate_page_objects(self, test_cases: List[Dict[str, Any]], pages_dir: str):
        """Asks LLM to generate all necessary Page Object files for the spec."""
        logger.info("Generating Page Object files...")
        url_cible = getattr(self, 'url_cible', 'https://demowebshop.tricentis.com/electronics')
        system_prompt = f"""
        Tu es un expert QA Selenium. Pour le projet fourni, génère UNIQUEMENT le contenu des classes Page Object nécessaires en Python 3.12.
        
        Règles d'or :
        1. CHAQUE fichier Page Object doit commencer par : from selenium.webdriver.remote.webdriver import WebDriver.
        2. CHAQUE constructeur __init__ doit utiliser l'annotation de type : def __init__(self, driver: WebDriver):.
        3. Importe 'base_page' si nécessaire : from .base_page import BasePage (ou from base_page import BasePage selon la structure).
        4. Utilise la vraie URL du site : {url_cible}
        
        Structure de réponse attendue :
        FILE: login_page.py
        ```python
        (code de la page)
        ```
        FILE: dashboard_page.py
        ...
        """
        cases_json = json.dumps(test_cases[:5], indent=2) # Take first 5 cases to avoid token overflow
        response = self.llm_client.call(system_prompt, f"Génère les pages pour ces cas de test : {cases_json}")
        
        import re
        # Look for FILE: filename and then its content between ``` (any flavor)
        files = re.findall(r'FILE:\s*(.*?\.py)\s*```(?:python)?\s*\n(.*?)\n\s*```', response, re.DOTALL)
        
        if not files:
            logger.warning("No Page Objects found with 'FILE:' header. Trying fallback search.")
            # Fallback: look for any python blocks and use their title if found before them
            files = re.findall(r'([a-zA-Z0-9_]+\.py)\s*```(?:python)?\s*\n(.*?)\n\s*```', response, re.DOTALL)

        for filename, content in files:
            with open(os.path.join(pages_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content.strip())
            logger.info(f"Page file created: {filename}")

    def _write_base_page(self, pages_dir: str):
        """Creates the base_page.py file with common Selenium utilities."""
        base_page_code = """
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    \"\"\"Base Page class containing generic Selenium methods.\"\"\"
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def send_keys(self, locator, text):
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.find_element(locator).text

    def is_visible(self, locator):
        try:
            return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()
        except TimeoutException:
            return False
"""
        with open(os.path.join(pages_dir, "base_page.py"), 'w', encoding='utf-8') as f:
            f.write(base_page_code.strip())

    def _write_conftest(self, output_dir: str):
        """Creates conftest.py for pytest fixtures."""
        conftest_code = """
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
"""
        with open(os.path.join(output_dir, "conftest.py"), 'w', encoding='utf-8') as f:
            f.write(conftest_code.strip())

    def _write_pytest_ini(self, output_dir: str):
        """Creates pytest.ini configuration."""
        pytest_ini = """
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --junitxml=results.xml
"""
        with open(os.path.join(output_dir, "pytest.ini"), 'w', encoding='utf-8') as f:
            f.write(pytest_ini.strip())

    def _extract_and_save_pages(self, code: str, pages_dir: str):
        """Extracts page classes from LLM code block and saves them as separate files."""
        # Simple heuristic to extract class definitions and put them in pages/ folder
        # In actual practice, we'd want the LLM to separate these explicitly.
        # For now, I'll keep the generated code as is (merged) unless I see clear Page class definitions.
        # But to respect POM, it's better to have separate files.
        # Let's assume the LLM generates a monolithic file for simplicity in this specific task
        # unless we want to do more advanced parsing.
        pass
