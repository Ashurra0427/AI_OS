"""LLM abstraction — cloud preferred, local fallback."""

from __future__ import annotations

import logging
from typing import Any

from src.config.settings import settings

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model: str | None = None, local: bool = False) -> None:
        if model:
            self.model = model
        elif local:
            self.model = settings.llm_local_model
        else:
            self.model = settings.llm_cloud_provider
        self._local = local

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        if self._local or not settings.llm_cloud_api_key:
            return await self._local_generate(prompt, **kwargs)
        try:
            return await self._cloud_generate(prompt, **kwargs)
        except Exception as exc:
            logger.warning("cloud_llm_failed", error=str(exc))
            return await self._local_generate(prompt, **kwargs)

    async def _cloud_generate(self, prompt: str, **kwargs: Any) -> str:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.llm_cloud_api_key)
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return resp.choices[0].message.content or ""

    async def _local_generate(self, prompt: str, **kwargs: Any) -> str:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(settings.llm_local_model)
            model = AutoModelForCausalLM.from_pretrained(settings.llm_local_model)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=512)
            return tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as exc:
            logger.error("local_llm_failed", error=str(exc))
            return "[LLM unavailable]"
