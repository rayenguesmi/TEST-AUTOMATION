import os
import json
import yaml
import time
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("ReportGenerator")

class ReportGenerator:
    """Generates HTML and JSON reports based on execution results."""

    def __init__(self, config_path: str):
        """Initializes generator with templates and config."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.output_formats = self.config.get('report', {}).get('format', ["html", "json"])
        self.include_screenshots = self.config.get('report', {}).get('include_screenshots', True)

    def generate(self, test_results: Dict[str, Any], parsed_spec: Dict[str, Any], output_reports_dir: str):
        """Generates HTML and JSON reports using template and results."""
        logger.info(f"Generating reports into: {output_reports_dir}")
        os.makedirs(output_reports_dir, exist_ok=True)
        
        # Merge spec information for traceability
        processed_data = self._merge_spec_and_results(test_results, parsed_spec)
        
        # 1. JSON Report
        if "json" in self.output_formats:
            json_report_path = os.path.join(output_reports_dir, "report.json")
            with open(json_report_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
        
        # 2. HTML Report
        if "html" in self.output_formats:
            html_report_path = os.path.join(output_reports_dir, "report.html")
            template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("report_template.html")
            
            html_content = template.render(
                results=test_results,
                spec=parsed_spec,
                summary=processed_data['summary'],
                features=processed_data['features_with_results']
            )
            
            with open(html_report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
        logger.info(f"Report generation completed: {output_reports_dir}")

    def _merge_spec_and_results(self, results: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Merges spec's features with test result metrics."""
        summary = {
            "project_name": spec.get('project_name', 'Unknown'),
            "url_cible": spec.get('url_cible', 'Unknown'),
            "total_tests": results.get('total', 0),
            "passed": results.get('passed', 0),
            "failed": results.get('failed', 0),
            "errors": results.get('errors', 0),
            "duration_seconds": round(results.get('duration_seconds', 0), 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Build a lookup: test classname -> test result
        all_tests = results.get('tests', [])

        features_list = []
        features = spec.get('features', [])
        # Distribute tests across features by template key (F001->F-001, etc.)
        # Template keys: F001, F002, F003, F004, F005, F006
        feature_key_map = {
            f"F-{str(i+1).zfill(3)}": f"F{str(i+1).zfill(3)}"
            for i in range(len(features))
        }

        for feature in features:
            fid = feature.get('id')           # e.g. 'F-001'
            tkey = feature_key_map.get(fid)   # e.g. 'F001'

            # Match tests by classname which contains template key (e.g. 'test_F001_...')
            feature_tests = [
                t for t in all_tests
                if tkey and tkey.lower() in t.get('classname', '').lower()
            ]

            # Fallback: match by test name containing template key
            if not feature_tests:
                feature_tests = [
                    t for t in all_tests
                    if tkey and tkey.lower() in t.get('name', '').lower()
                ]

            all_passed = all(t['statut'] == "PASS" for t in feature_tests) if feature_tests else False
            status = "PASS" if all_passed else "FAIL"

            features_list.append({
                "id": fid,
                "title": feature.get('titre'),
                "description": feature.get('description'),
                "status": status,
                "tests": feature_tests
            })

        return {
            "summary": summary,
            "features_with_results": features_list
        }
