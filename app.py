"""
Semantic SEO Platform
Based on Koray Tuğberk GÜBÜR's Framework

Main Streamlit application entry point.
"""

from __future__ import annotations

import streamlit as st
from pathlib import Path
import sys

# Add the app directory to path for imports
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from config.settings import get_settings
from config.database import init_db
from utils.session_state import init_session_state, display_notifications

# Page configuration
st.set_page_config(
    page_title="Semantic SEO Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/semantic-seo-platform",
        "Report a bug": "https://github.com/your-repo/semantic-seo-platform/issues",
        "About": """
        # Semantic SEO Platform
        
        Based on **Koray Tuğberk GÜBÜR's** Semantic SEO Framework.
        
        Build topical authority through:
        - Topical Maps
        - Content Briefs
        - Publication Management
        - Performance Analytics
        """
    }
)

# Custom CSS
st.markdown("""
<style>
    /* Main app styling */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Card styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Status colors */
    .status-black { color: #1a1a1a; font-weight: bold; }
    .status-orange { color: #ff8c00; font-weight: bold; }
    .status-yellow { color: #ffd700; font-weight: bold; }
    .status-blue { color: #1e90ff; font-weight: bold; }
    .status-green { color: #32cd32; font-weight: bold; }
    
    /* Section headers */
    .section-header {
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Entity cards */
    .entity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    /* Brief status indicators */
    .brief-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .brief-status-black { background: #1a1a1a; color: white; }
    .brief-status-orange { background: #ff8c00; color: white; }
    .brief-status-yellow { background: #ffd700; color: black; }
    .brief-status-blue { background: #1e90ff; color: white; }
    .brief-status-green { background: #32cd32; color: white; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


def initialize_app():
    """Initialize the application."""
    # Initialize session state
    init_session_state()
    
    # Initialize database
    settings = get_settings()
    try:
        init_db(str(settings.get_database_path()))
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()


def render_sidebar():
    """Render the sidebar with project selector and navigation."""
    with st.sidebar:
        # App branding
        st.markdown("# 🎯 Semantic SEO")
        st.markdown("*Based on Koray's Framework*")
        st.divider()
        
        # Project selector
        render_project_selector()
        
        st.divider()
        
        # Quick stats if project selected
        if st.session_state.get("current_project"):
            render_quick_stats()
            st.divider()
        
        # Settings link
        st.markdown("---")
        with st.expander("⚙️ Quick Settings"):
            settings = get_settings()
            
            # AI Provider status
            providers = settings.get_available_ai_providers()
            active_providers = [p for p, v in providers.items() if v]
            
            if active_providers:
                st.success(f"AI: {', '.join(active_providers)}")
            else:
                st.warning("No AI provider configured")
                st.caption("Go to Settings page to add API keys")
            
            # Debug toggle
            if st.checkbox(
                "Debug Mode",
                value=st.session_state.get("show_debug", False),
                key="debug_toggle"
            ):
                st.session_state.show_debug = True
            else:
                st.session_state.show_debug = False


def render_project_selector():
    """Render project selector in sidebar."""
    from modules.project.service import ProjectService
    
    st.markdown("### 📁 Project")
    
    # Get all projects
    try:
        project_service = ProjectService()
        projects = project_service.get_all_projects()
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        projects = []
    
    if not projects:
        st.info("No projects yet")
        if st.button("➕ Create First Project", use_container_width=True):
            st.session_state.show_create_project = True
    else:
        # Project dropdown
        project_options = {p["id"]: p["name"] for p in projects}
        project_options["__new__"] = "➕ Create New Project"
        
        current_id = st.session_state.get("current_project_id")
        
        selected = st.selectbox(
            "Select Project",
            options=list(project_options.keys()),
            format_func=lambda x: project_options[x],
            index=(
                list(project_options.keys()).index(current_id)
                if current_id in project_options else 0
            ),
            key="project_selector"
        )
        
        if selected == "__new__":
            st.session_state.show_create_project = True
        elif selected != current_id:
            # Load selected project
            project = next(
                (p for p in projects if p["id"] == selected),
                None
            )
            if project:
                st.session_state.current_project_id = project["id"]
                st.session_state.current_project = project
                st.rerun()
    
    # Create project modal
    if st.session_state.get("show_create_project"):
        render_create_project_form()


def render_create_project_form():
    """Render the create project form."""
    from modules.project.service import ProjectService
    
    st.markdown("### New Project")
    
    with st.form("create_project_form"):
        name = st.text_input(
            "Project Name*",
            placeholder="e.g., German Visa Site"
        )
        
        source_context = st.text_area(
            "Source Context",
            placeholder="Who you are and how you make money",
            help="e.g., 'Visa Consultancy helping people relocate to Germany'"
        )
        
        central_entity = st.text_input(
            "Central Entity",
            placeholder="Main subject of your site",
            help="e.g., 'Germany'"
        )
        
        central_search_intent = st.text_area(
            "Central Search Intent",
            placeholder="What users want to know/do",
            help="e.g., 'Know and Go to Germany'"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                "Create Project",
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancelled = st.form_submit_button(
                "Cancel",
                use_container_width=True
            )
        
        if submitted and name:
            try:
                project_service = ProjectService()
                new_project = project_service.create_project(
                    name=name,
                    source_context=source_context or None,
                    central_entity=central_entity or None,
                    central_search_intent=central_search_intent or None,
                )
                st.session_state.current_project_id = new_project["id"]
                st.session_state.current_project = new_project
                st.session_state.show_create_project = False
                st.success(f"Created project: {name}")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating project: {e}")
        
        if cancelled:
            st.session_state.show_create_project = False
            st.rerun()


def render_quick_stats():
    """Render quick project stats in sidebar."""
    project = st.session_state.get("current_project", {})
    
    st.markdown(f"**{project.get('name', 'Project')}**")
    
    # Show project context
    if project.get("central_entity"):
        st.caption(f"Entity: {project.get('central_entity')}")
    
    # Placeholder stats - will be populated when services are implemented
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 Briefs", "0")
    with col2:
        st.metric("🟢 Live", "0")


def main():
    """Main application function."""
    # Initialize
    initialize_app()
    
    # Display any pending notifications
    display_notifications()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.title("🎯 Semantic SEO Platform")
    st.markdown(
        "*Build Topical Authority with Koray's Framework*"
    )
    
    # Check if project selected
    if not st.session_state.get("current_project"):
        st.info(
            "👈 Select or create a project from the sidebar to get started."
        )
        
        # Show welcome/onboarding
        render_welcome()
    else:
        # Show dashboard
        render_dashboard()


def render_welcome():
    """Render welcome screen for new users."""
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Create a Project** - Define your source context and central entity
        2. **Build Topical Map** - Discover entities and attributes
        3. **Generate Briefs** - Create content briefs with CorelIS framework
        4. **Manage Publication** - Track status and momentum
        5. **Analyze Performance** - Monitor topical authority growth
        """)
    
    with col2:
        st.markdown("""
        ### 📚 Key Concepts
        
        - **Source Context**: Who you are and how you monetize
        - **Central Entity**: Main subject of your site
        - **Topical Map**: Entity-attribute relationships
        - **CorelIS**: Contextual Vector, Hierarchy, Structure, Connection
        - **Momentum**: Publication velocity and authority signals
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📊 Framework Overview
    
    > **Topical Authority = Topical Coverage × Historical Data**
    
    This platform implements Koray Tuğberk GÜBÜR's Semantic SEO framework,
    helping you build comprehensive topical coverage and establish authority
    in your niche through systematic content planning and publication.
    """)


def render_dashboard():
    """Render main dashboard for selected project."""
    project = st.session_state.get("current_project", {})
    
    # Project header
    st.markdown(f"## 📁 {project.get('name', 'Project')}")
    
    # Project context summary
    with st.expander("Project Context", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Source Context:**")
            st.write(
                project.get("source_context") or "*Not defined*"
            )
            st.markdown(f"**Central Entity:**")
            st.write(
                project.get("central_entity") or "*Not defined*"
            )
        with col2:
            st.markdown(f"**Central Search Intent:**")
            st.write(
                project.get("central_search_intent") or "*Not defined*"
            )
            st.markdown(f"**Functional Words:**")
            words = project.get("functional_words") or []
            st.write(", ".join(words) if words else "*Not defined*")
    
    # Dashboard tabs
    tabs = st.tabs([
        "📊 Overview",
        "🎯 Quick Actions",
        "📈 Recent Activity"
    ])
    
    with tabs[0]:
        render_overview_tab()
    
    with tabs[1]:
        render_quick_actions_tab()
    
    with tabs[2]:
        render_recent_activity_tab()


def render_overview_tab():
    """Render dashboard overview tab."""
    # Status metrics (placeholder - will use real data)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "⚫ Black",
            "0",
            help="Briefs not ready"
        )
    with col2:
        st.metric(
            "🟠 Orange",
            "0",
            help="Briefs ready"
        )
    with col3:
        st.metric(
            "🟡 Yellow",
            "0",
            help="Writing in progress"
        )
    with col4:
        st.metric(
            "🔵 Blue",
            "0",
            help="Awaiting publication"
        )
    with col5:
        st.metric(
            "🟢 Green",
            "0",
            help="Published"
        )
    
    st.markdown("---")
    
    # Topical Authority score (placeholder)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Topical Authority Score")
        st.progress(0.0)
        st.caption(
            "Coverage: 0% | Depth: 0% | Momentum: 0%"
        )
    
    with col2:
        st.markdown("### 🎯 Next Actions")
        st.markdown("1. Define source context")
        st.markdown("2. Create topical map")
        st.markdown("3. Generate first briefs")


def render_quick_actions_tab():
    """Render quick actions tab."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Content")
        
        if st.button(
            "🗺️ Create Topical Map",
            use_container_width=True
        ):
            st.switch_page("pages/2_🗺️_Topical_Maps.py")
        
        if st.button(
            "📝 New Content Brief",
            use_container_width=True
        ):
            st.switch_page("pages/3_📝_Content_Briefs.py")
        
        if st.button(
            "📅 Publication Queue",
            use_container_width=True
        ):
            st.switch_page("pages/4_📅_Publication_Manager.py")
    
    with col2:
        st.markdown("### 📊 Analysis")
        
        if st.button(
            "🔗 Link Network",
            use_container_width=True
        ):
            st.switch_page("pages/6_🔗_Link_Network.py")
        
        if st.button(
            "📈 Analytics",
            use_container_width=True
        ):
            st.switch_page("pages/5_📊_Analytics.py")
        
        if st.button(
            "⚙️ Settings",
            use_container_width=True
        ):
            st.switch_page("pages/7_⚙️_Settings.py")


def render_recent_activity_tab():
    """Render recent activity tab."""
    st.markdown("### 📋 Recent Activity")
    st.info("Activity tracking will be available once you start creating content.")
    
    # Placeholder for activity feed
    st.markdown("""
    Activity will show:
    - Recently created/updated briefs
    - Publication events
    - AI generation tasks
    - Import/export operations
    """)


if __name__ == "__main__":
    main()