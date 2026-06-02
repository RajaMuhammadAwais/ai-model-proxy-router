import re
from typing import Iterable

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_413_CONTENT_TOO_LARGE

from ..models.llm_metadata import ChatCompletionRequest


class RequestGuardrails:
    prompt_injection_signals = (
        re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
        re.compile(r"reveal\s+(the\s+)?(system|developer)\s+prompt", re.IGNORECASE),
        re.compile(r"(steal|dump|exfiltrate)\s+(secrets|credentials|api\s*keys)", re.IGNORECASE),
    )

    def __init__(self, max_prompt_chars: int, block_prompt_injection_signals: bool = True):
        self.max_prompt_chars = max_prompt_chars
        self.block_prompt_injection_signals = block_prompt_injection_signals

    def validate(self, request: ChatCompletionRequest) -> None:
        prompt = "\n".join(self._message_text(request))
        if len(prompt) > self.max_prompt_chars:
            raise HTTPException(
                status_code=HTTP_413_CONTENT_TOO_LARGE,
                detail="Prompt exceeds configured size limit",
            )
        if self.block_prompt_injection_signals and any(pattern.search(prompt) for pattern in self.prompt_injection_signals):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Request blocked by prompt-injection guardrail",
            )

    def _message_text(self, request: ChatCompletionRequest) -> Iterable[str]:
        for message in request.messages:
            yield message.content
