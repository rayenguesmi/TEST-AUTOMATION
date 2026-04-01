import json
import yaml
import jsonschema
from typing import Dict, Any, List
from utils.file_loader import FileLoader
from utils.llm_client import LLMClient
from utils.logger import setup_logger

logger = setup_logger("SpecParser")

SPEC_SCHEMA = {
    "type": "object",
    "properties": {
        "project_name": {"type": "string"},
        "url_cible": {"type": "string"},
        "features": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "titre": {"type": "string"},
                    "description": {"type": "string"},
                    "criteres_acceptance": {"type": "array", "items": {"type": "string"}},
                    "flux_positif": {"type": "string"},
                    "flux_negatif": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["id", "titre", "description", "criteres_acceptance", "flux_positif", "flux_negatif"]
            }
        }
    },
    "required": ["project_name", "url_cible", "features"]
}

class SpecParser:
    """Parses functional spec files into structured JSON."""

    def __init__(self, config_path: str):
        """Initializes parser with config and prompts."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.system_prompt = self.config['prompts']['spec_parsing']
        self.llm_client = LLMClient(config_path)

    def parse(self, spec_file_path: str) -> Dict[str, Any]:
        """Loads spec file, extracts content with LLM, and validates."""
        logger.info(f"Parsing spec file: {spec_file_path}")
        raw_text = FileLoader.load_file(spec_file_path)
        
        logger.debug(f"Raw spec content length: {len(raw_text)}")
        structured_data = self.llm_client.call_json(self.system_prompt, raw_text)
        
        logger.debug(f"LLM Response structured data: {json.dumps(structured_data, indent=2)}")
        
        # Normalize data (some LLMs return lists for string fields or vice versa)
        if 'features' in structured_data and isinstance(structured_data['features'], list):
            for feat in structured_data['features']:
                # Ensure flux_positif is a string
                if isinstance(feat.get('flux_positif'), list):
                    feat['flux_positif'] = " ".join([str(x) for x in feat['flux_positif']])
                elif feat.get('flux_positif') is None:
                    feat['flux_positif'] = ""
                
                # Ensure lists are lists
                for list_field in ['criteres_acceptance', 'flux_negatif']:
                    if isinstance(feat.get(list_field), str):
                        feat[list_field] = [feat[list_field]]
                    elif feat.get(list_field) is None:
                        feat[list_field] = []

        # Validate schema
        try:
            jsonschema.validate(instance=structured_data, schema=SPEC_SCHEMA)
            logger.info("Spec parsed and validated successfully.")
        except jsonschema.ValidationError as e:
            logger.error(f"Spec validation failed at {e.path}: {e.message}")
            logger.debug(f"Offending instance: {e.instance}")
            raise e

        return structured_data
