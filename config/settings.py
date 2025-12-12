"""Application settings and configuration management.

Supports configuration from multiple sources (in priority order):
1. Streamlit Secrets (st.secrets) - for Streamlit Cloud deployment
2. Environment Variables (.env) - for local development
3. Default values
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret value from Streamlit secrets or environment variables.
    
    Priority:
    1. Streamlit secrets (st.secrets) - for cloud deployment
    2. Environment variables - for local development
    3. Default value
    
    Args:
        key: The secret key to look up
        default: Default value if not found
    
    Returns:
        The secret value or default
    """
    # Try Streamlit secrets first (works in Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            # Check nested structure (e.g., st.secrets.api_keys.OPENROUTER_API_KEY)
            if 'api_keys' in st.secrets and key in st.secrets.api_keys:
                return st.secrets.api_keys[key]
            # Check flat structure (e.g., st.secrets.OPENROUTER_API_KEY)
            if key in st.secrets:
                return st.secrets[key]
    except Exception:
        pass  # Not running in Streamlit or secrets not configured
    
    # Fall back to environment variable
    return os.getenv(key, default)


def get_secret_bool(key: str, default: bool = False) -> bool:
    """Get a boolean secret value."""
    value = get_secret(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


class AISettings(BaseModel):
    """AI provider settings."""
    
    openrouter_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    
    default_provider: str = Field(default="openrouter")
    default_model: str = Field(default="anthropic/claude-3-sonnet")
    
    # Generation settings
    default_temperature: float = Field(default=0.7)
    default_max_tokens: int = Field(default=4000)


class DatabaseSettings(BaseModel):
    """Database settings."""
    
    path: str = Field(default="data/semantic_seo.db")
    echo: bool = Field(default=False)  # SQL logging


class ExportSettings(BaseModel):
    """Export settings."""
    
    path: str = Field(default="data/exports")
    default_format: str = Field(default="json")


class GSCSettings(BaseModel):
    """Google Search Console settings."""
    
    credentials_path: Optional[str] = Field(default=None)
    token_path: str = Field(default="data/gsc_token.json")


class CloudSyncSettings(BaseModel):
    """Cloud sync settings (optional)."""
    
    enabled: bool = Field(default=False)
    provider: Optional[str] = Field(default=None)  # supabase, firebase
    supabase_url: Optional[str] = Field(default=None)
    supabase_key: Optional[str] = Field(default=None)
    firebase_project_id: Optional[str] = Field(default=None)


class Settings(BaseModel):
    """Main application settings."""
    
    # Application info
    app_name: str = Field(default="Semantic SEO Platform")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Component settings
    ai: AISettings = Field(default_factory=AISettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    export: ExportSettings = Field(default_factory=ExportSettings)
    gsc: GSCSettings = Field(default_factory=GSCSettings)
    cloud_sync: CloudSyncSettings = Field(default_factory=CloudSyncSettings)
    
    # Paths
    base_path: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """
        Create settings from Streamlit secrets or environment variables.
        
        Streamlit secrets take priority over environment variables,
        allowing secure configuration in Streamlit Cloud.
        """
        return cls(
            debug=get_secret_bool("DEBUG_MODE", False),
            ai=AISettings(
                openrouter_api_key=get_secret("OPENROUTER_API_KEY"),
                openai_api_key=get_secret("OPENAI_API_KEY"),
                anthropic_api_key=get_secret("ANTHROPIC_API_KEY"),
                google_api_key=get_secret("GOOGLE_API_KEY"),
                default_provider=get_secret("DEFAULT_AI_PROVIDER", "openrouter"),
                default_model=get_secret("DEFAULT_MODEL", "anthropic/claude-3-sonnet"),
            ),
            database=DatabaseSettings(
                path=get_secret("DATABASE_PATH", "data/semantic_seo.db"),
            ),
            export=ExportSettings(
                path=get_secret("EXPORT_PATH", "data/exports"),
            ),
            gsc=GSCSettings(
                credentials_path=get_secret("GSC_CREDENTIALS_PATH"),
            ),
            cloud_sync=CloudSyncSettings(
                enabled=get_secret("SUPABASE_URL") is not None or get_secret("FIREBASE_PROJECT_ID") is not None,
                supabase_url=get_secret("SUPABASE_URL"),
                supabase_key=get_secret("SUPABASE_KEY"),
                firebase_project_id=get_secret("FIREBASE_PROJECT_ID"),
            ),
        )
    
    def get_database_path(self) -> Path:
        """Get absolute database path."""
        db_path = Path(self.database.path)
        if not db_path.is_absolute():
            db_path = self.base_path / db_path
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path
    
    def get_export_path(self) -> Path:
        """Get absolute export path."""
        export_path = Path(self.export.path)
        if not export_path.is_absolute():
            export_path = self.base_path / export_path
        # Ensure directory exists
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path
    
    def get_available_ai_providers(self) -> Dict[str, bool]:
        """Get dict of available AI providers based on API keys."""
        return {
            "openrouter": self.ai.openrouter_api_key is not None,
            "openai": self.ai.openai_api_key is not None,
            "anthropic": self.ai.anthropic_api_key is not None,
            "google": self.ai.google_api_key is not None,
        }
    
    def has_any_ai_provider(self) -> bool:
        """Check if at least one AI provider is configured."""
        return any(self.get_available_ai_providers().values())
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        key_map = {
            "openrouter": self.ai.openrouter_api_key,
            "openai": self.ai.openai_api_key,
            "anthropic": self.ai.anthropic_api_key,
            "google": self.ai.google_api_key,
        }
        return key_map.get(provider)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings.from_env()


def update_settings(**kwargs) -> Settings:
    """Update settings and clear cache."""
    get_settings.cache_clear()
    # For runtime updates, we'd need to handle this differently
    # For now, return fresh settings
    return get_settings()