from typing import Any, Dict, Iterable

from ..models.llm_metadata import ChatCompletionRequest

class RequestAnalyzer:
    def __init__(self):
        # In a real system, we might load a small model or use embeddings
        # For this implementation, we'll use keyword-based intent detection
        # as a placeholder for a more complex ML-based classifier.
        self.intents = {
            "coding": ["python", "code", "function", "bug", "debug", "programming", "script"],
            "reasoning": ["solve", "math", "logic", "explain", "why", "complex", "step-by-step"],
            "summarization": ["summarize", "tl;dr", "extract", "shorten", "concise"],
            "chat": ["hello", "hi", "how are you", "chat", "talk"]
        }

    async def analyze_request(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        full_text = " ".join(self._message_text(request)).lower()
        
        scores = {intent: 0 for intent in self.intents}
        for intent, keywords in self.intents.items():
            for kw in keywords:
                if kw in full_text:
                    scores[intent] += 1
        
        # Determine primary intent
        primary_intent = max(scores, key=scores.get) if any(scores.values()) else "general"
        
        # Estimate required capabilities
        required_capabilities = {
            "reasoning_strength": 0.3,
            "coding_strength": 0.3,
            "context_length": len(full_text) // 4 + (request.max_tokens or 500)
        }
        
        if primary_intent == "coding":
            required_capabilities["coding_strength"] = 0.8
        elif primary_intent == "reasoning":
            required_capabilities["reasoning_strength"] = 0.8

        required_capabilities["tool_calling"] = bool(request.tools or request.tool_choice)
        required_capabilities["multimodal"] = any(self._is_multimodal_content(message.content) for message in request.messages)
            
        return {
            "intent": primary_intent,
            "required_capabilities": required_capabilities,
            "token_estimate": len(full_text) // 4,
            "requested_model": request.model,
            "analysis_method": "keyword_signals_and_request_shape"
        }

    def _message_text(self, request: ChatCompletionRequest) -> Iterable[str]:
        for message in request.messages:
            content = message.content
            if isinstance(content, str):
                yield content
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        yield part["text"]
            elif content is not None:
                yield str(content)

    def _is_multimodal_content(self, content: Any) -> bool:
        if not isinstance(content, list):
            return False
        return any(isinstance(part, dict) and part.get("type") not in {"text", None} for part in content)
