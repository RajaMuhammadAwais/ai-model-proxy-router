import httpx
import logging
from typing import List, Dict, Any, Optional

from .base import LLMProvider
from ..models.llm_metadata import ModelMetadata

logger = logging.getLogger(__name__)

class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        configured_models: Optional[List[ModelMetadata]] = None,
    ):
        super().__init__(name, base_url, api_key)
        self.configured_models = configured_models or []

    async def list_models(self) -> List[ModelMetadata]:
        if self.configured_models:
            return self.configured_models

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            discovered_ids = [model.get("id") for model in data.get("data", []) if model.get("id")]
            logger.warning(
                "Provider %s returned %d model ids but no configured metadata; routing will not infer capabilities",
                self.name,
                len(discovered_ids),
            )
            return []

    async def chat_completion(self, model_id: str, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model_id,
                    "messages": messages,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()

    async def embeddings(self, model_id: str, input: List[str], **kwargs) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model_id,
                    "input": input,
                    **kwargs
                }
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
                return response.status_code == 200
        except Exception:
            return False
