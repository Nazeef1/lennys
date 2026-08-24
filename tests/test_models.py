import pytest
from backend.app.llm.provider import provider_registry, FallbackProvider, AnthropicProvider, OpenAIProvider, OllamaProvider

@pytest.mark.asyncio
async def test_provider_registry():
    # Check fallback provider
    fallback = provider_registry.get_provider("fallback")
    assert isinstance(fallback, FallbackProvider)
    assert fallback.is_available is True

    response = await fallback.generate_response("System Prompt", "Test prompt question?")
    assert "[Resilience Engine" in response
    assert "Test prompt question?" in response

@pytest.mark.asyncio
async def test_provider_switching():
    assert provider_registry.set_active_provider("fallback") is True
    assert provider_registry.active_provider_name == "fallback"

    statuses = await provider_registry.list_providers_status()
    assert any(s["id"] == "fallback" and s["active"] for s in statuses)
