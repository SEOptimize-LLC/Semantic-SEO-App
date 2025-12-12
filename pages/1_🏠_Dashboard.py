"""
Dashboard Page - Main overview and quick actions.
Redirects to main app.py dashboard functionality.
"""

import streamlit as st
from pathlib import Path
import sys

# Add app directory to path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

st.set_page_config(
    page_title="Dashboard - Semantic SEO Platform",
    page_icon="🏠",
    layout="wide"
)

# Redirect to main page or show dashboard
st.markdown("# 🏠 Dashboard")
st.info("👈 Use the main app entry point for the full dashboard experience.")
st.markdown("[← Go to Main Dashboard](/)")