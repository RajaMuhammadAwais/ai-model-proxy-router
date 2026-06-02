import httpx
from typing import List, Dict, Any
from .base import LLMProvider
from ..models.llm_metadata import ModelMetadata, ModelCapabilities

class OpenAICompatibleProvider(LLMProvider):
    async def list_models(self) -> List[ModelMetadata]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            data = response.json()
            
            models = []
            for m in data.get("data", []):
                # In a real system, we'd fetch or infer capabilities
                # For now, using placeholder values
                models.append(ModelMetadata(
                    id=m["id"],
                    provider=self.name,
                    capabilities=ModelCapabilities(
                        context_length=4096,
                        reasoning_strength=0.5,
                        coding_strength=0.5
                    ),
                    cost_per_1k_tokens=0.01
                ))
            return models

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
