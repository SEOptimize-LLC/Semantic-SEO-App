"""
Settings Page - API key management and application configuration.
"""

from __future__ import annotations

import streamlit as st
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Settings - Semantic SEO Platform",
    page_icon="⚙️",
    layout="wide"
)

# Add app directory to path
import sys
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from config.settings import get_settings, Settings
from config.ai_providers import AI_PROVIDERS, get_provider_config
from utils.session_state import init_session_state


def main():
    """Main settings page."""
    init_session_state()
    
    st.title("⚙️ Settings")
    st.markdown("Configure API keys and application settings")
    
    # Tabs for different settings
    tabs = st.tabs([
        "🤖 AI Providers",
        "🔗 Integrations", 
        "💾 Data & Export",
        "🎨 Appearance"
    ])
    
    with tabs[0]:
        render_ai_settings()
    
    with tabs[1]:
        render_integration_settings()
    
    with tabs[2]:
        render_data_settings()
    
    with tabs[3]:
        render_appearance_settings()


def render_ai_settings():
    """Render AI provider settings."""
    st.markdown("### 🤖 AI Provider Configuration")
    st.markdown(
        "Configure API keys for AI providers. "
        "At least one provider is required for AI features."
    )
    
    settings = get_settings()
    
    # Current status
    providers = settings.get_available_ai_providers()
    active = [p for p, v in providers.items() if v]
    
    if active:
        st.success(f"✅ Active providers: {', '.join(active)}")
    else:
        st.warning(
            "⚠️ No AI providers configured. "
            "AI features will be disabled."
        )
    
    st.divider()
    
    # OpenRouter (recommended)
    with st.expander("🌐 OpenRouter (Recommended)", expanded=True):
        st.markdown("""
        OpenRouter provides access to multiple AI models through a single API.
        
        **Supported Models:**
        - Claude 3.5 Sonnet, Claude 3 Sonnet
        - GPT-4 Turbo, GPT-4o, GPT-4o Mini
        - Gemini Pro, Gemini 1.5 Pro
        - And many more...
        
        [Get API Key →](https://openrouter.ai)
        """)
        
        openrouter_key = st.text_input(
            "OpenRouter API Key",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password",
            key="openrouter_key"
        )
        
        if openrouter_key:
            st.success("✓ OpenRouter key configured")
            
            # Test connection button
            if st.button("Test Connection", key="test_openrouter"):
                with st.spinner("Testing..."):
                    success = test_openrouter_connection(openrouter_key)
                    if success:
                        st.success("✅ Connection successful!")
                    else:
                        st.error("❌ Connection failed")
    
    # OpenAI Direct
    with st.expander("🟢 OpenAI Direct"):
        st.markdown("""
        Direct connection to OpenAI API.
        
        **Models:** GPT-4 Turbo, GPT-4o, GPT-4o Mini
        
        [Get API Key →](https://platform.openai.com/api-keys)
        """)
        
        openai_key = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            key="openai_key"
        )
        
        if openai_key:
            st.success("✓ OpenAI key configured")
    
    # Anthropic Direct
    with st.expander("🟣 Anthropic Direct"):
        st.markdown("""
        Direct connection to Anthropic API.
        
        **Models:** Claude 3.5 Sonnet, Claude 3 Haiku
        
        [Get API Key →](https://console.anthropic.com/)
        """)
        
        anthropic_key = st.text_input(
            "Anthropic API Key",
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            type="password",
            key="anthropic_key"
        )
        
        if anthropic_key:
            st.success("✓ Anthropic key configured")
    
    # Google (Gemini)
    with st.expander("🔵 Google AI (Gemini)"):
        st.markdown("""
        Google's Gemini models.
        
        **Models:** Gemini Pro, Gemini 1.5 Pro
        
        [Get API Key →](https://makersuite.google.com/app/apikey)
        """)
        
        google_key = st.text_input(
            "Google API Key",
            value=os.getenv("GOOGLE_API_KEY", ""),
            type="password",
            key="google_key"
        )
        
        if google_key:
            st.success("✓ Google key configured")
    
    st.divider()
    
    # Default provider selection
    st.markdown("### Default Provider")
    
    available_providers = []
    if openrouter_key:
        available_providers.append("openrouter")
    if openai_key:
        available_providers.append("openai")
    if anthropic_key:
        available_providers.append("anthropic")
    if google_key:
        available_providers.append("google")
    
    if available_providers:
        default_provider = st.selectbox(
            "Default AI Provider",
            options=available_providers,
            format_func=lambda x: AI_PROVIDERS[x].display_name,
            key="default_provider"
        )
        
        # Default model for provider
        if default_provider:
            provider_config = get_provider_config(default_provider)
            if provider_config:
                model_options = list(provider_config.models.keys())
                default_model = st.selectbox(
                    "Default Model",
                    options=model_options,
                    format_func=lambda x: provider_config.models[x].name,
                    key="default_model"
                )
                
                # Store in session state
                st.session_state.ai_provider = default_provider
                st.session_state.ai_model = default_model
    
    # Save button
    st.divider()
    
    if st.button("💾 Save API Keys to .env", type="primary"):
        save_api_keys_to_env(
            openrouter=openrouter_key,
            openai=openai_key,
            anthropic=anthropic_key,
            google=google_key
        )
        st.success("✅ API keys saved to .env file")
        st.info("Restart the app to apply changes")


def render_integration_settings():
    """Render integration settings (GSC, SERP, etc.)."""
    st.markdown("### 🔗 External Integrations")
    
    # Google Search Console
    with st.expander("📊 Google Search Console", expanded=True):
        st.markdown("""
        Connect to Google Search Console for:
        - Performance analytics
        - Query data import
        - 3-Column analysis
        
        **Setup:**
        1. Create OAuth credentials in Google Cloud Console
        2. Download the credentials JSON file
        3. Upload below
        """)
        
        gsc_creds = st.file_uploader(
            "Upload GSC Credentials (JSON)",
            type=["json"],
            key="gsc_credentials"
        )
        
        if gsc_creds:
            # Save credentials
            creds_path = Path(__file__).parent.parent / "data" / "gsc_credentials.json"
            creds_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(creds_path, "wb") as f:
                f.write(gsc_creds.getvalue())
            
            st.success(f"✅ Credentials saved to {creds_path}")
        
        # Check if already configured
        existing_creds = Path(__file__).parent.parent / "data" / "gsc_credentials.json"
        if existing_creds.exists():
            st.info("✓ GSC credentials file exists")
            
            if st.button("🗑️ Remove GSC Credentials", key="remove_gsc"):
                existing_creds.unlink()
                st.success("Credentials removed")
                st.rerun()
    
    # SERP API
    with st.expander("🔍 SERP API (Serper)"):
        st.markdown("""
        SERP API for competitor analysis and query research.
        
        [Get API Key →](https://serper.dev)
        """)
        
        serper_key = st.text_input(
            "Serper API Key",
            value=os.getenv("SERPER_API_KEY", ""),
            type="password",
            key="serper_key"
        )
        
        if serper_key:
            st.success("✓ Serper key configured")


def render_data_settings():
    """Render data and export settings."""
    st.markdown("### 💾 Data Management")
    
    settings = get_settings()
    
    # Database info
    with st.expander("🗄️ Database", expanded=True):
        db_path = settings.get_database_path()
        
        st.markdown(f"**Database Location:** `{db_path}`")
        
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            st.markdown(f"**Size:** {size_mb:.2f} MB")
            st.success("✓ Database exists")
        else:
            st.warning("Database not yet created")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Backup Database", key="backup_db"):
                backup_database(db_path)
        
        with col2:
            if st.button("⚠️ Reset Database", key="reset_db"):
                st.session_state.confirm_reset = True
        
        if st.session_state.get("confirm_reset"):
            st.warning("This will DELETE all data. Are you sure?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Reset", type="primary"):
                    from config.database import reset_db
                    reset_db()
                    st.session_state.confirm_reset = False
                    st.success("Database reset complete")
                    st.rerun()
            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_reset = False
                    st.rerun()
    
    # Export settings
    with st.expander("📤 Export Settings"):
        export_path = settings.get_export_path()
        
        st.markdown(f"**Export Directory:** `{export_path}`")
        
        # List existing exports
        if export_path.exists():
            exports = list(export_path.glob("*"))
            if exports:
                st.markdown(f"**Exports:** {len(exports)} files")
                
                if st.button("🗑️ Clear Exports", key="clear_exports"):
                    for f in exports:
                        f.unlink()
                    st.success("Exports cleared")
            else:
                st.info("No exports yet")
    
    # Cloud sync (future)
    with st.expander("☁️ Cloud Sync (Coming Soon)"):
        st.markdown("""
        Cloud sync will allow you to:
        - Backup data to cloud storage
        - Sync across devices
        - Collaborate with team members
        
        **Planned Integrations:**
        - Supabase
        - Firebase
        - Custom API
        """)
        
        st.info("Cloud sync is coming in a future update")


def render_appearance_settings():
    """Render appearance and UI settings."""
    st.markdown("### 🎨 Appearance")
    
    # Theme (Streamlit handles this)
    st.markdown("""
    **Theme Settings**
    
    Use Streamlit's built-in theme settings:
    - Click the ☰ menu in the top right
    - Select "Settings"
    - Choose your theme
    """)
    
    st.divider()
    
    # Display preferences
    st.markdown("### Display Preferences")
    
    show_debug = st.checkbox(
        "Show Debug Information",
        value=st.session_state.get("show_debug", False),
        help="Display detailed debug info throughout the app"
    )
    st.session_state.show_debug = show_debug
    
    # Compact mode (future)
    st.checkbox(
        "Compact Mode",
        value=False,
        disabled=True,
        help="Coming soon - Reduce spacing for more content"
    )


def test_openrouter_connection(api_key: str) -> bool:
    """Test OpenRouter API connection."""
    try:
        import httpx
        
        response = httpx.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        return response.status_code == 200
    except Exception:
        return False


def save_api_keys_to_env(
    openrouter: str = "",
    openai: str = "",
    anthropic: str = "",
    google: str = ""
):
    """Save API keys to .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    
    # Read existing env if exists
    existing = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing[key] = value
    
    # Update with new values
    if openrouter:
        existing["OPENROUTER_API_KEY"] = openrouter
    if openai:
        existing["OPENAI_API_KEY"] = openai
    if anthropic:
        existing["ANTHROPIC_API_KEY"] = anthropic
    if google:
        existing["GOOGLE_API_KEY"] = google
    
    # Write back
    with open(env_path, "w") as f:
        f.write("# Semantic SEO Platform - Environment Variables\n\n")
        for key, value in existing.items():
            f.write(f"{key}={value}\n")


def backup_database(db_path: Path):
    """Create a backup of the database."""
    import shutil
    from datetime import datetime
    
    if not db_path.exists():
        st.error("Database does not exist")
        return
    
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"semantic_seo_{timestamp}.db"
    
    shutil.copy(db_path, backup_path)
    
    st.success(f"✅ Backup created: {backup_path}")


if __name__ == "__main__":
    main()