import json
import yaml
import jsonschema
from typing import Dict, Any, List
from utils.llm_client import LLMClient
from utils.logger import setup_logger

logger = setup_logger("TestCaseGenerator")

TEST_CASE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "feature_id": {"type": "string"},
            "titre": {"type": "string"},
            "type": {"enum": ["positif", "négatif", "edge_case"]},
            "préconditions": {"type": "array", "items": {"type": "string"}},
            "étapes": {"type": "array", "items": {"type": "string"}},
            "résultat_attendu": {"type": "string"},
            "données_test": {"type": "object"}
        },
        "required": ["id", "feature_id", "titre", "type", "préconditions", "étapes", "résultat_attendu", "données_test"]
    }
}

class TestCaseGenerator:
    """Generates detailed test cases for each feature in the spec."""

    def __init__(self, config_path: str):
        """Initializes generator with config and prompts."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.system_prompt = self.config['prompts']['test_generation']
        self.llm_client = LLMClient(config_path)

    def generate(self, parsed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates test cases for all features in the spec."""
        all_test_cases = []
        features = parsed_spec.get('features', [])
        
        logger.info(f"Generating test cases for {len(features)} features.")
        
        for feature in features:
            feature_id = feature.get('id', 'F-Unknown')
            logger.debug(f"Generating cases for {feature_id}")
            
            feature_json = json.dumps(feature, indent=2)
            cases = self.llm_client.call_json(self.system_prompt, feature_json)
            
            # Anti-rate limit
            import time
            time.sleep(5)
            
            # Flexible mapping: allow French keys if LLM translates them
            if isinstance(cases, dict) and "test_cases" in cases:
                cases = cases["test_cases"]
            elif isinstance(cases, dict) and "cas_de_test" in cases:
                cases = cases["cas_de_test"]
            
            if not isinstance(cases, list):
                logger.warning(f"LLM did not return a list of cases for {feature_id}. Attempting to extract if it's a dict.")
                if isinstance(cases, dict):
                    cases = [cases]
                else:
                    continue

            # Standardize keys before validation (to keep the rest of the pipeline happy)
            for case in cases:
                if 'cas_de_test_id' in case: case['id'] = case.pop('cas_de_test_id')
                if 'steps' in case: case['étapes'] = case.pop('steps')
                if 'expected_result' in case: case['résultat_attendu'] = case.pop('expected_result')
                # Ensure all required keys exist (with defaults if missing)
                case.setdefault('id', f"TC-{feature_id[2:]}")
                case.setdefault('feature_id', feature_id)
                case.setdefault('titre', 'Generated Test Case')
                case.setdefault('type', 'positif')
                case.setdefault('préconditions', [])
                case.setdefault('étapes', ['Ouvrir le site'])
                case.setdefault('résultat_attendu', 'Action réussie')
                case.setdefault('données_test', {})
                
            all_test_cases.extend(cases)
        
        logger.info(f"Total test cases generated: {len(all_test_cases)}")
        return all_test_cases
