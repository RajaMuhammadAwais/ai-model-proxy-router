from fastapi import APIRouter, HTTPException, Request
from ...models.llm_metadata import ChatCompletionRequest
from typing import Any, Dict

router = APIRouter()

from fastapi import Depends
from ...core.manager import ProviderManager
from ...security.auth import get_api_key
from ...security.guardrails import RequestGuardrails

def get_pm():
    from ...main import provider_manager
    return provider_manager

@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest, 
    pm: ProviderManager = Depends(get_pm),
    api_key: str = Depends(get_api_key)
):
    security = pm.config_manager.config.security
    RequestGuardrails(
        max_prompt_chars=security.max_prompt_chars,
        block_prompt_injection_signals=security.block_prompt_injection_signals,
    ).validate(request)
    return await pm.handle_chat_completion(request)

@router.get("/models")
async def list_models(pm: ProviderManager = Depends(get_pm), api_key: str = Depends(get_api_key)):
    if not pm.models:
        await pm.refresh_models()
    return {"data": [m.model_dump() for m in pm.models]}

@router.post("/embeddings")
async def embeddings(request: Dict[str, Any], api_key: str = Depends(get_api_key)):
    return {"message": "Embeddings logic not yet implemented"}
