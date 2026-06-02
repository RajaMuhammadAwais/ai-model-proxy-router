import yaml
import os
import re
from typing import Any, Dict, Optional
from .schema import AppConfig
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self.config_path = config_path
        self.config: Optional[AppConfig] = None
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        self.config = AppConfig(**self._expand_env(raw_config))

    def _expand_env(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {k: self._expand_env(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._expand_env(item) for item in value]
        if isinstance(value, str):
            match = re.fullmatch(r"\$\{([A-Z0-9_]+)\}", value)
            if match:
                return os.getenv(match.group(1), "")
        return value

    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        for provider in self.config.providers:
            if provider.name == provider_name:
                return provider.model_dump()
        return None

    def get_routing_policy(self) -> Dict[str, Any]:
        return self.config.routing_policy.dict()
    
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)
