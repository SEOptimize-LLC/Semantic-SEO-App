"""AI provider configurations and model definitions."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel


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