import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import json
import yaml
import time
from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from utils.logger import setup_logger

logger = setup_logger("LLMClient")

class LLMClient:
    """Abstraction for interacting with Anthropic or OpenAI."""

    def __init__(self, config_path: str):
        """Initializes the LLM based on config."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.llm_config = config.get('llm', {})
        self.provider = self.llm_config.get('provider', 'anthropic')
        self.model = self.llm_config.get('model', 'claude-3-5-sonnet-20241022')
        self.temperature = self.llm_config.get('temperature', 0.2)
        self.max_tokens = self.llm_config.get('max_tokens', 4096)

        import os
        api_key = os.getenv("GOOGLE_API_KEY") if self.provider == "google" else \
                  os.getenv("MISTRAL_API_KEY") if self.provider == "mistral" else \
                  os.getenv("GROQ_API_KEY") if self.provider == "groq" else \
                  os.getenv("OPENAI_API_KEY") if self.provider == "openai" else \
                  os.getenv("ANTHROPIC_API_KEY") if self.provider == "anthropic" else None

        if self.provider == "anthropic":
            self.llm = ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096,
                api_key=api_key
            )
        elif self.provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096,
                api_key=api_key
            )
        elif self.provider == "groq":
            self.llm = ChatGroq(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096,
                api_key=api_key
            )
        elif self.provider == "google":
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens or 4096,
                google_api_key=api_key
            )
        elif self.provider == "mistral":
            self.llm = ChatMistralAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens or 4096,
                api_key=api_key
            )
        elif self.provider == "ollama":
            self.llm = ChatOllama(
                model=self.model,
                temperature=self.temperature,
                base_url=self.llm_config.get('base_url', 'http://localhost:11434')
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def call(self, system_prompt: str, user_content: str, retries: int = 5) -> str:
        """Call LLM with retries."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        for attempt in range(retries):
            try:
                logger.debug(f"Calling LLM: {self.provider}/{self.model} - Attempt {attempt+1}")
                response = self.llm.invoke(messages)
                content = response.content
                if isinstance(content, list):
                    # Join logic for multi-modal responses if they appear
                    content = "".join([c["text"] if isinstance(c, dict) and "text" in c else str(c) for c in content])
                
                logger.debug(f"LLM Response received.")
                return content

            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt == retries - 1:
                    raise e
                time.sleep(2 ** attempt)

    def call_json(self, system_prompt: str, user_content: str, retries: int = 5) -> Dict[str, Any]:
        """Call LLM and parse JSON output with retries on decode error."""
        for attempt in range(retries):
            try:
                content = self.call(system_prompt, user_content, retries=1) # One call at a time
                
                # Robust extraction using regex
                import re
                content = content.strip()
                json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                
                return json.loads(content)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"JSON attempt {attempt+1} failed: {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to get valid JSON after {retries} attempts.")
                    raise e
                time.sleep(2 ** attempt)
