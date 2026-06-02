import asyncio
import logging
import time
from typing import Callable, Any, Dict
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

class CircuitBreakerOpen(Exception):
    pass

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info(f"Circuit {self.name} is HALF-OPEN")
            else:
                raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit {self.name} is now OPEN")

class ReliabilityManager:
    def __init__(self):
        self.circuits: Dict[str, CircuitBreaker] = {}

    def get_circuit(self, name: str) -> CircuitBreaker:
        if name not in self.circuits:
            self.circuits[name] = CircuitBreaker(name)
        return self.circuits[name]

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def with_retry(self, func: Callable, *args, **kwargs) -> Any:
        return await func(*args, **kwargs)
