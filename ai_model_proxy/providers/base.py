from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..models.llm_metadata import ModelMetadata

class LLMProvider(ABC):
    def __init__(self, name: str, base_url: str, api_key: str):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key

    @abstractmethod
    async def list_models(self) -> List[ModelMetadata]:
        pass

    @abstractmethod
    async def chat_completion(self, model_id: str, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def embeddings(self, model_id: str, input: List[str], **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
