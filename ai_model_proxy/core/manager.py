import time
import logging
from typing import List, Dict, Any
from .analyzer import RequestAnalyzer
from .router import RouterEngine
from ..providers.openai_adapter import OpenAICompatibleProvider
from ..models.llm_metadata import ModelMetadata, ChatCompletionRequest
from ..services.reliability import ReliabilityManager

logger = logging.getLogger(__name__)

class ProviderManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.providers = {}
        self.models: List[ModelMetadata] = []
        self.analyzer = RequestAnalyzer()
        self.router = RouterEngine(config_manager.get_routing_policy())
        self.reliability = ReliabilityManager()
        self._initialize_providers()

    def _initialize_providers(self):
        for p_conf in self.config_manager.config.providers:
            # In a real system, use a factory to create specific provider types
            provider = OpenAICompatibleProvider(
                name=p_conf.name,
                base_url=p_conf.base_url,
                api_key=p_conf.api_key
            )
            self.providers[p_conf.name] = provider

    async def refresh_models(self):
        all_models = []
        for name, provider in self.providers.items():
            try:
                models = await provider.list_models()
                all_models.extend(models)
            except Exception as e:
                logger.error(f"Failed to fetch models from {name}: {e}")
        self.models = all_models

    async def handle_chat_completion(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        # 1. Analyze Request
        analysis = await self.analyzer.analyze_request(request)
        
        # 2. Ensure models are loaded
        if not self.models:
            await self.refresh_models()
            
        # 3. Route Request
        best_model = await self.router.route_request(analysis, self.models)
        provider = self.providers[best_model.provider]
        
        # 4. Execute with Reliability
        start_time = time.time()
        success = False
        try:
            circuit = self.reliability.get_circuit(best_model.provider)
            
            async def call_provider():
                return await provider.chat_completion(
                    model_id=best_model.id,
                    messages=[m.dict() for m in request.messages]
                )

            response = await circuit.call(self.reliability.with_retry, call_provider)
            success = True
            return response
        finally:
            latency = time.time() - start_time
            self.router.update_metrics(best_model.id, best_model.provider, latency, success)
