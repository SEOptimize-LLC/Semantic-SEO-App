"""
Topical Maps Page - Build and manage topical maps.
"""

import streamlit as st
from pathlib import Path
import sys

# Add app directory to path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from utils.session_state import init_session_state, require_project

st.set_page_config(
    page_title="Topical Maps - Semantic SEO Platform",
    page_icon="🗺️",
    layout="wide"
)


def main():
    init_session_state()
    
    st.title("🗺️ Topical Map Builder")
    st.markdown("*Create entity-attribute maps following Koray's methodology*")
    
    if not require_project():
        st.stop()
    
    st.info("🚧 **Coming in Phase 2**")
    st.markdown("""
    This module will include:
    
    ### Features
    - **AI Entity Discovery** - Automatically discover entities and attributes
    - **PPR Scoring** - Prominence, Popularity, Relevance scoring
    - **Core/Outer Sections** - Organize monetization vs trust content
    - **Attribute Classification** - Unique, Root, Rarer attributes
    - **Visual Map Editor** - Drag-and-drop map building
    - **Export Options** - JSON, CSV, Markdown
    
    ### Workflow
    1. Define Central Entity
    2. AI discovers related entities and attributes
    3. Filter and score with PPR methodology
    4. Classify into Core (monetization) and Outer (trust) sections
    5. Process into content briefs
    """)


if __name__ == "__main__":
    main()