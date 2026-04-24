import os
import re
import subprocess
import yaml
import time
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("TestRunner")

class TestRunner:
    """Executes generated tests using pytest and parses results."""

    def __init__(self, config_path: str):
        """Initializes runner with config."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.selenium_config = self.config.get('selenium', {})

    def run_tests(self, test_dir: str, browser: str = "chrome", headless: bool = True, timeout_sec: int = 600) -> Dict[str, Any]:
        """Runs pytest on the test directory and returns structured results."""
        logger.info(f"Running tests in: {test_dir} with browser: {browser}, headless: {headless}")
        
        import sys
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            f"--junitxml={os.path.join(test_dir, 'results.xml')}",
            f"--browser={browser}",
            f"--headless={'true' if headless else 'false'}"
        ]
        
        # Execute tests via subprocess
        start_time = time.time()
        try:
            logger.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            logger.info("Tests execution completed.")
        except subprocess.TimeoutExpired:
            logger.error(f"Tests execution timed out after {timeout_sec} seconds.")
            # Maybe some results were already written? 
        
        duration = time.time() - start_time
        
        # Parse result XML to get detailed report
        report_data = self._parse_junit_xml(os.path.join(test_dir, 'results.xml'), duration)
        
        return report_data

    def _parse_junit_xml(self, xml_path: str, duration: float) -> Dict[str, Any]:
        """Parses JUnit XML and extracts pass/fail metrics and messages."""
        if not os.path.exists(xml_path):
            logger.error(f"Results file not found: {xml_path}")
            return {"total": 0, "passed": 0, "failed": 0, "errors": 0, "duration_seconds": duration, "tests": []}

        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        testsuite = root.find('.//testsuite')
        if testsuite is None:
            # Maybe some older/different format?
            testsuite = root
        
        total = int(testsuite.get('tests', 0))
        failures = int(testsuite.get('failures', 0))
        errors = int(testsuite.get('errors', 0))
        skipped = int(testsuite.get('skipped', 0))
        passed = total - failures - errors - skipped
        
        tests_list = []
        for testcase in testsuite.findall('testcase'):
            full_name = testcase.get('name', '')
            class_name = testcase.get('classname', '')
            
            # Extract Feature ID (e.g., F_001 -> F-001)
            test_id = "TC-Unknown"
            match = re.search(r'F_(\d+)', full_name + class_name)
            if match:
                test_id = f"F-{match.group(1)}"
            else:
                # Fallback to old logic if no F-number found
                test_id = full_name.split('_')[1] if '_' in full_name else full_name
            
            name = full_name
            dur = float(testcase.get('time', 0))
            status = "PASS"
            msg = None
            
            failure = testcase.find('failure')
            if failure is not None:
                status = "FAIL"
                msg = failure.text
            
            error = testcase.find('error')
            if error is not None:
                status = "ERROR"
                msg = error.text
            
            # Simple heuristic for screenshot path (assuming same name as conftest.py logic)
            screenshot_path = f"../screenshots/{test_id}_failure.png" if status in ["FAIL", "ERROR"] else None
            
            classname = testcase.get('classname', '')

            tests_list.append({
                "id": test_id,
                "name": name,
                "classname": classname,
                "statut": status,
                "durée_secondes": dur,
                "message_erreur": msg,
                "screenshot_path": screenshot_path
            })

        return {
            "total": total,
            "passed": passed,
            "failed": failures,
            "errors": errors,
            "duration_seconds": duration,
            "tests": tests_list
        }
