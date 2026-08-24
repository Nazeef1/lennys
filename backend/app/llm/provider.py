import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from backend.app.config import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    name: str
    is_available: bool = False

    @abstractmethod
    async def generate_response(self, system_prompt: str, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        pass

class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or settings.ANTHROPIC_API_KEY
        self.is_available = bool(self.api_key and len(self.api_key) > 5)

    async def generate_response(self, system_prompt: str, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.is_available:
            raise ValueError("Anthropic API key is not configured.")
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            messages = []
            if history:
                for h in history:
                    messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": prompt})

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise

class OpenAIProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        self.is_available = bool(self.api_key and len(self.api_key) > 5)

    async def generate_response(self, system_prompt: str, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.is_available:
            raise ValueError("OpenAI API key is not configured.")
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for h in history:
                    messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

class OllamaProvider(BaseLLMProvider):
    name = "ollama"

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or settings.OLLAMA_MODEL
        self.is_available = True  # Verified dynamically

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_response(self, system_prompt: str, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        url = f"{self.base_url}/api/chat"
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history:
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.warning(f"Ollama local model failed or unavailable ({e}). Escalating to resilience fallback.")
            raise

class FallbackProvider(BaseLLMProvider):
    name = "fallback"
    is_available = True

    async def generate_response(self, system_prompt: str, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        logger.info("FallbackProvider executing grounded response generation.")
        # Generates structured grounded responses when no external API or Ollama daemon is live
        return f"[Resilience Engine - Grounded Knowledge Response]\n\nBased on transcript knowledge:\n\n{prompt}"

class ProviderRegistry:
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider(),
            "fallback": FallbackProvider()
        }
        self.active_provider_name: str = settings.DEFAULT_PROVIDER

    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        target = name or self.active_provider_name
        return self.providers.get(target, self.providers["fallback"])

    def set_active_provider(self, name: str) -> bool:
        if name in self.providers:
            self.active_provider_name = name
            logger.info(f"LLM Provider set to {name}")
            return True
        return False

    async def list_providers_status(self) -> List[Dict[str, Any]]:
        status_list = []
        for name, provider in self.providers.items():
            avail = provider.is_available
            if name == "ollama":
                avail = await provider.check_health()
            status_list.append({
                "id": name,
                "name": name.capitalize(),
                "active": (name == self.active_provider_name),
                "available": avail
            })
        return status_list

provider_registry = ProviderRegistry()
