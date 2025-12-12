"""AI provider configurations and model definitions."""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from pydantic import BaseModel


def get_ai_client() -> Optional[Any]:
    """
    Get an OpenAI-compatible client for the configured AI provider.
    
    Returns an OpenAI client configured for the selected provider,
    or None if no provider is configured.
    
    All providers use the OpenAI SDK format for compatibility.
    """
    from config.settings import get_settings
    
    settings = get_settings()
    
    # Determine which provider to use based on available API keys
    provider = settings.ai.default_provider
    api_key = settings.get_api_key(provider)
    
    # If default provider has no key, try others
    if not api_key:
        for p in ["openrouter", "openai", "anthropic", "google"]:
            key = settings.get_api_key(p)
            if key:
                provider = p
                api_key = key
                break
    
    if not api_key:
        return None
    
    # Import OpenAI SDK
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai package is required. Install with: pip install openai"
        )
    
    # Configure client based on provider
    provider_config = AI_PROVIDERS.get(provider)
    if not provider_config:
        return None
    
    base_url = provider_config.base_url
    
    # Special handling for different providers
    if provider == "openrouter":
        return OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://semantic-seo-platform.streamlit.app",
                "X-Title": "Semantic SEO Platform"
            }
        )
    elif provider == "anthropic":
        # Anthropic uses their own SDK, but we can use OpenAI format
        # via their OpenAI-compatible endpoint
        return OpenAI(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
        )
    elif provider == "google":
        # Google requires special handling
        # For now, recommend using OpenRouter for Google models
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Return a wrapper that mimics OpenAI interface
            return GoogleAIWrapper(api_key)
        except ImportError:
            return None
    else:
        # OpenAI or other OpenAI-compatible providers
        return OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None,
        )


class GoogleAIWrapper:
    """Wrapper to make Google AI API compatible with OpenAI interface."""
    
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.genai = genai
    
    @property
    def chat(self):
        return self
    
    @property
    def completions(self):
        return self
    
    def create(self, model: str, messages: list, **kwargs):
        """Create a chat completion using Google AI."""
        # Convert OpenAI message format to Google format
        model_instance = self.genai.GenerativeModel(model)
        
        # Build conversation
        chat = model_instance.start_chat(history=[])
        
        # Get the last user message
        last_message = ""
        for msg in messages:
            if msg["role"] == "user":
                last_message = msg["content"]
            elif msg["role"] == "system":
                # Prepend system message to user message
                last_message = msg["content"] + "\n\n" + last_message
        
        response = chat.send_message(last_message)
        
        # Return OpenAI-compatible response format
        class Choice:
            def __init__(self, text):
                self.message = type('obj', (object,), {'content': text})()
        
        class Response:
            def __init__(self, text):
                self.choices = [Choice(text)]
        
        return Response(response.text)


class ModelConfig(BaseModel):
    """Configuration for a specific AI model."""
    
    id: str
    name: str
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    best_for: List[str]
    supports_json: bool = True
    supports_streaming: bool = True


class ProviderConfig(BaseModel):
    """Configuration for an AI provider."""
    
    name: str
    display_name: str
    base_url: str
    models: Dict[str, ModelConfig]
    requires_api_key: bool = True


# AI Provider Configurations
AI_PROVIDERS: Dict[str, ProviderConfig] = {
    "openrouter": ProviderConfig(
        name="openrouter",
        display_name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        models={
            "claude-3-5-sonnet": ModelConfig(
                id="anthropic/claude-3.5-sonnet",
                name="Claude 3.5 Sonnet",
                context_window=200000,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                best_for=[
                    "content_generation",
                    "analysis",
                    "long_form"
                ],
            ),
            "claude-3-sonnet": ModelConfig(
                id="anthropic/claude-3-sonnet",
                name="Claude 3 Sonnet",
                context_window=200000,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                best_for=[
                    "content_generation",
                    "analysis"
                ],
            ),
            "gpt-4-turbo": ModelConfig(
                id="openai/gpt-4-turbo",
                name="GPT-4 Turbo",
                context_window=128000,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                best_for=[
                    "complex_reasoning",
                    "long_content"
                ],
            ),
            "gpt-4o": ModelConfig(
                id="openai/gpt-4o",
                name="GPT-4o",
                context_window=128000,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
                best_for=[
                    "general_purpose",
                    "fast"
                ],
            ),
            "gpt-4o-mini": ModelConfig(
                id="openai/gpt-4o-mini",
                name="GPT-4o Mini",
                context_window=128000,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                best_for=[
                    "quick_tasks",
                    "cost_effective"
                ],
            ),
            "gemini-pro": ModelConfig(
                id="google/gemini-pro",
                name="Gemini Pro",
                context_window=32000,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.0005,
                best_for=[
                    "quick_tasks",
                    "cost_effective"
                ],
            ),
            "gemini-1.5-pro": ModelConfig(
                id="google/gemini-pro-1.5",
                name="Gemini 1.5 Pro",
                context_window=1000000,
                cost_per_1k_input=0.00125,
                cost_per_1k_output=0.005,
                best_for=[
                    "very_long_context",
                    "analysis"
                ],
            ),
        },
    ),
    "openai": ProviderConfig(
        name="openai",
        display_name="OpenAI Direct",
        base_url="https://api.openai.com/v1",
        models={
            "gpt-4-turbo": ModelConfig(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                context_window=128000,
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                best_for=[
                    "complex_reasoning",
                    "long_content"
                ],
            ),
            "gpt-4o": ModelConfig(
                id="gpt-4o",
                name="GPT-4o",
                context_window=128000,
                cost_per_1k_input=0.005,
                cost_per_1k_output=0.015,
                best_for=[
                    "general_purpose"
                ],
            ),
            "gpt-4o-mini": ModelConfig(
                id="gpt-4o-mini",
                name="GPT-4o Mini",
                context_window=128000,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                best_for=[
                    "quick_tasks",
                    "cost_effective"
                ],
            ),
        },
    ),
    "anthropic": ProviderConfig(
        name="anthropic",
        display_name="Anthropic Direct",
        base_url="https://api.anthropic.com/v1",
        models={
            "claude-3-5-sonnet": ModelConfig(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                context_window=200000,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                best_for=[
                    "detailed_analysis",
                    "long_form",
                    "content_generation"
                ],
            ),
            "claude-3-haiku": ModelConfig(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                context_window=200000,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                best_for=[
                    "quick_tasks",
                    "cost_effective"
                ],
            ),
        },
    ),
    "google": ProviderConfig(
        name="google",
        display_name="Google AI (Gemini)",
        base_url="https://generativelanguage.googleapis.com/v1",
        models={
            "gemini-pro": ModelConfig(
                id="gemini-pro",
                name="Gemini Pro",
                context_window=32000,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.0005,
                best_for=[
                    "quick_tasks"
                ],
            ),
            "gemini-1.5-pro": ModelConfig(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                context_window=1000000,
                cost_per_1k_input=0.00125,
                cost_per_1k_output=0.005,
                best_for=[
                    "very_long_context"
                ],
            ),
        },
    ),
}


def get_provider_config(provider: str) -> Optional[ProviderConfig]:
    """Get configuration for a specific provider."""
    return AI_PROVIDERS.get(provider)


def get_model_config(
    provider: str,
    model: str
) -> Optional[ModelConfig]:
    """Get configuration for a specific model."""
    provider_config = get_provider_config(provider)
    if provider_config:
        return provider_config.models.get(model)
    return None


def get_available_models(provider: str) -> Dict[str, ModelConfig]:
    """Get all available models for a provider."""
    provider_config = get_provider_config(provider)
    if provider_config:
        return provider_config.models
    return {}


def get_best_model_for_task(
    task: str,
    available_providers: List[str]
) -> Optional[tuple]:
    """
    Find the best model for a specific task from available providers.
    
    Args:
        task: Task type (e.g., 'content_generation', 'analysis')
        available_providers: List of providers with valid API keys
    
    Returns:
        Tuple of (provider, model_key, model_config) or None
    """
    for provider in available_providers:
        provider_config = get_provider_config(provider)
        if not provider_config:
            continue
        
        for model_key, model_config in provider_config.models.items():
            if task in model_config.best_for:
                return (provider, model_key, model_config)
    
    return None


# Default model recommendations by use case
RECOMMENDED_MODELS = {
    "entity_discovery": {
        "provider": "openrouter",
        "model": "claude-3-5-sonnet",
        "temperature": 0.3,
        "reason": "Best for factual entity extraction"
    },
    "content_brief": {
        "provider": "openrouter",
        "model": "gpt-4-turbo",
        "temperature": 0.5,
        "reason": "Good balance of creativity and structure"
    },
    "query_analysis": {
        "provider": "openrouter",
        "model": "claude-3-sonnet",
        "temperature": 0.2,
        "reason": "Precise analytical capabilities"
    },
    "quick_tasks": {
        "provider": "openrouter",
        "model": "gpt-4o-mini",
        "temperature": 0.5,
        "reason": "Fast and cost-effective"
    },
}