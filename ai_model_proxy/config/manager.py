import yaml
import os
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
        
        # Environment variable overrides (simplified example)
        # In production, use pydantic-settings for robust env overrides
        self.config = AppConfig(**raw_config)

    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        for provider in self.config.providers:
            if provider.name == provider_name:
                return provider.dict()
        return None

    def get_routing_policy(self) -> Dict[str, Any]:
        return self.config.routing_policy.dict()
    
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)
