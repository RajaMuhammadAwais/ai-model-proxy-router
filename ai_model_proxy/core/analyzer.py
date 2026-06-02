from typing import Dict, Any
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
        full_text = " ".join([m.content for m in request.messages]).lower()
        
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
            
        return {
            "intent": primary_intent,
            "required_capabilities": required_capabilities,
            "token_estimate": len(full_text) // 4
        }
