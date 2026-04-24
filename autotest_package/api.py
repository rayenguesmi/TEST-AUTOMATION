from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import uuid
import yaml
import shutil
import sys
from typing import Optional

# Ensure relative imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from spec_parser import SpecParser
from test_case_generator import TestCaseGenerator
from spec_to_selenium import SeleniumGenerator
from test_runner import TestRunner
from report_generator import ReportGenerator

app = FastAPI(title="AUTOTEST API Engine")
logger = setup_logger("API", log_level="INFO")

# In-memory storage for task status (for demo purposes)
tasks = {}

class TestRequest(BaseModel):
    spec_content: str
    url: str
    api_key: Optional[str] = None
    provider: Optional[str] = "groq"
    browser: Optional[str] = "chrome"
    headless: Optional[bool] = True

def run_test_pipeline(task_id: str, request: TestRequest):
    try:
        tasks[task_id] = {"status": "running", "progress": "Starting"}
        
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", task_id)
        os.makedirs(output_dir, exist_ok=True)

        # Inject API Key
        if request.api_key:
            env_var_name = f"{request.provider.upper()}_API_KEY"
            os.environ[env_var_name] = request.api_key

        # Save spec content to a temporary file
        spec_path = os.path.join(output_dir, "spec.md")
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(request.spec_content)

        # STEP 1: Parsage
        tasks[task_id]["progress"] = "Parsing Specification"
        parser_engine = SpecParser(config_path)
        parsed_spec = parser_engine.parse(spec_path)
        parsed_spec['url_cible'] = request.url
        
        # STEP 2: Génération des cas de test
        tasks[task_id]["progress"] = "Generating Test Cases"
        case_gen = TestCaseGenerator(config_path)
        test_cases = case_gen.generate(parsed_spec)

        # STEP 3: Génération des scripts Selenium
        tasks[task_id]["progress"] = "Generating Selenium Scripts"
        script_gen = SeleniumGenerator(config_path)
        script_gen.generate_scripts(test_cases, output_dir, url_cible=request.url)
        
        # STEP 4: Exécution des tests
        tasks[task_id]["progress"] = "Running Tests"
        runner = TestRunner(config_path)
        generated_tests_dir = os.path.join(output_dir, "generated_tests")
        test_results = runner.run_tests(
            generated_tests_dir, 
            browser=request.browser, 
            headless=request.headless, 
            timeout_sec=30 * len(test_cases)
        )

        # STEP 5: Génération du rapport
        tasks[task_id]["progress"] = "Generating Report"
        report_gen = ReportGenerator(config_path)
        reports_dir = os.path.join(output_dir, "reports")
        report_gen.generate(test_results, parsed_spec, reports_dir)

        tasks[task_id] = {
            "status": "completed", 
            "progress": "Finished",
            "report_path": f"/reports/{task_id}/report.html",
            "results": test_results
        }
        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        tasks[task_id] = {"status": "failed", "error": str(e)}

@app.post("/run-test")
async def start_test(request: TestRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "progress": "Queued"}
    background_tasks.add_task(run_test_pipeline, task_id, request)
    return {"task_id": task_id, "status": "started"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_id=404, detail="Task not found")
    return tasks[task_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
