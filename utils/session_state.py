"""Streamlit session state management utilities."""

from __future__ import annotations

from typing import Optional, Dict, Any, List
import streamlit as st

from utils.database import Project


def init_session_state():
    """Initialize all session state variables with defaults."""
    
    # Current project
    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = None
    
    if "current_project" not in st.session_state:
        st.session_state.current_project = None
    
    # Topical map state
    if "current_topical_map_id" not in st.session_state:
        st.session_state.current_topical_map_id = None
    
    if "selected_entity_id" not in st.session_state:
        st.session_state.selected_entity_id = None
    
    # Content brief state
    if "current_brief_id" not in st.session_state:
        st.session_state.current_brief_id = None
    
    if "brief_edit_mode" not in st.session_state:
        st.session_state.brief_edit_mode = False
    
    # Publication state
    if "publication_filter" not in st.session_state:
        st.session_state.publication_filter = "all"
    
    # Analytics state
    if "analytics_date_range" not in st.session_state:
        st.session_state.analytics_date_range = "30d"
    
    # AI state
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = None
    
    if "ai_model" not in st.session_state:
        st.session_state.ai_model = None
    
    if "ai_processing" not in st.session_state:
        st.session_state.ai_processing = False
    
    # UI state
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = False
    
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False
    
    # Notifications
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    # Cache for expensive operations
    if "cache" not in st.session_state:
        st.session_state.cache = {}


def get_current_project() -> Optional[Dict[str, Any]]:
    """Get the currently selected project."""
    return st.session_state.get("current_project")


def set_current_project(project: Optional[Dict[str, Any]]):
    """
    Set the current project.
    
    Args:
        project: Project dictionary or None
    """
    if project:
        st.session_state.current_project_id = project.get("id")
        st.session_state.current_project = project
    else:
        st.session_state.current_project_id = None
        st.session_state.current_project = None
    
    # Clear related state when project changes
    st.session_state.current_topical_map_id = None
    st.session_state.selected_entity_id = None
    st.session_state.current_brief_id = None


def get_current_project_id() -> Optional[str]:
    """Get the ID of the currently selected project."""
    return st.session_state.get("current_project_id")


def require_project() -> bool:
    """
    Check if a project is selected, show warning if not.
    
    Returns:
        True if project is selected, False otherwise
    """
    if not st.session_state.get("current_project_id"):
        st.warning("⚠️ Please select a project first.")
        return False
    return True


# Topical Map State
def get_current_topical_map_id() -> Optional[str]:
    """Get the ID of the currently selected topical map."""
    return st.session_state.get("current_topical_map_id")


def set_current_topical_map(map_id: Optional[str]):
    """Set the current topical map."""
    st.session_state.current_topical_map_id = map_id
    # Clear entity selection when map changes
    st.session_state.selected_entity_id = None


# Content Brief State
def get_current_brief_id() -> Optional[str]:
    """Get the ID of the currently selected content brief."""
    return st.session_state.get("current_brief_id")


def set_current_brief(brief_id: Optional[str]):
    """Set the current content brief."""
    st.session_state.current_brief_id = brief_id


def is_brief_edit_mode() -> bool:
    """Check if in brief edit mode."""
    return st.session_state.get("brief_edit_mode", False)


def toggle_brief_edit_mode():
    """Toggle brief edit mode."""
    st.session_state.brief_edit_mode = not st.session_state.get(
        "brief_edit_mode", False
    )


# AI State
def get_ai_config() -> Dict[str, Any]:
    """Get current AI configuration."""
    return {
        "provider": st.session_state.get("ai_provider"),
        "model": st.session_state.get("ai_model"),
    }


def set_ai_config(provider: str, model: str):
    """Set AI configuration."""
    st.session_state.ai_provider = provider
    st.session_state.ai_model = model


def is_ai_processing() -> bool:
    """Check if AI is currently processing."""
    return st.session_state.get("ai_processing", False)


def set_ai_processing(processing: bool):
    """Set AI processing state."""
    st.session_state.ai_processing = processing


# Notifications
def add_notification(
    message: str,
    type: str = "info"
):
    """
    Add a notification to display.
    
    Args:
        message: Notification message
        type: Type of notification (info, success, warning, error)
    """
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    st.session_state.notifications.append({
        "message": message,
        "type": type,
    })


def get_notifications() -> List[Dict[str, str]]:
    """Get all pending notifications."""
    return st.session_state.get("notifications", [])


def clear_notifications():
    """Clear all notifications."""
    st.session_state.notifications = []


def display_notifications():
    """Display and clear all notifications."""
    notifications = get_notifications()
    
    for notif in notifications:
        msg = notif["message"]
        notif_type = notif["type"]
        
        if notif_type == "success":
            st.success(msg)
        elif notif_type == "warning":
            st.warning(msg)
        elif notif_type == "error":
            st.error(msg)
        else:
            st.info(msg)
    
    clear_notifications()


# Cache utilities
def get_cached(key: str) -> Optional[Any]:
    """Get a cached value."""
    cache = st.session_state.get("cache", {})
    return cache.get(key)


def set_cached(key: str, value: Any):
    """Set a cached value."""
    if "cache" not in st.session_state:
        st.session_state.cache = {}
    st.session_state.cache[key] = value


def clear_cache(key: Optional[str] = None):
    """Clear cache (specific key or all)."""
    if key:
        if "cache" in st.session_state and key in st.session_state.cache:
            del st.session_state.cache[key]
    else:
        st.session_state.cache = {}


# Debug utilities
def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return st.session_state.get("show_debug", False)


def toggle_debug_mode():
    """Toggle debug mode."""
    st.session_state.show_debug = not st.session_state.get(
        "show_debug", False
    )


def show_debug_info(title: str, data: Any):
    """Show debug information if debug mode is enabled."""
    if is_debug_mode():
        with st.expander(f"🐛 Debug: {title}"):
            st.json(data)