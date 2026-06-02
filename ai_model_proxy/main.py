from fastapi import FastAPI, Depends, HTTPException
from .api.v1.endpoints import router as v1_router
from .config.manager import ConfigManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Model Proxy & Intelligent Router",
    description="Universal OpenAI-compatible gateway with intelligent routing.",
    version="1.0.0"
)

# Initialize Components
config_manager = ConfigManager()
from .core.manager import ProviderManager
from .services.observability import ObservabilityManager
from .services.cache import CacheManager

observability = ObservabilityManager()
provider_manager = ProviderManager(config_manager, observability=observability)
cache = CacheManager(enabled=config_manager.config.cache_enabled, redis_url=config_manager.config.redis_url)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Model Proxy...")
    observability.instrument_app(app)
    await provider_manager.refresh_models()

# Dependency Injection for routes
def get_provider_manager():
    return provider_manager

app.include_router(v1_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
