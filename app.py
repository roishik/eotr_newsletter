#!/Users/roishi/miniconda3/envs/eotr_newsletter/bin/python

import streamlit as st
import os
import datetime

# Import configuration
from config.settings import APP_TITLE, APP_ICON, DEFAULT_THEME, DEFAULT_LANGUAGE
from config.prompts import DEFAULT_PROMPTS

# Import services
from services.llm_service import LLMService

# Import UI components
from ui.components import add_logo_and_banner
from ui.styles import apply_base_styles, apply_dark_theme
from ui.generate_view import render_generate_view
from ui.edit_view import render_edit_view
from ui.discovery_view import render_news_discovery

# Import utils
from utils.file_utils import (
    create_drafts_directory,
    get_available_drafts,
    save_draft,
    load_draft,
    update_session_state_from_newsletter,
    create_newsletter_from_session_state
)

# Initialize application
def initialize_app():
    """Initialize the application settings."""
    # Page configuration
    st.set_page_config(
        page_title=APP_TITLE, 
        page_icon=APP_ICON, 
        layout="wide", 
        initial_sidebar_state="expanded"
    )
    
    # Apply base styles
    apply_base_styles()
    
    # Create necessary directories
    create_drafts_directory()
    
    # Initialize session state variables if not present
    if "generated_sections" not in st.session_state:
        st.session_state.generated_sections = {}
    
    if "edited_sections" not in st.session_state:
        st.session_state.edited_sections = {}
    
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
        
    if "timestamp" not in st.session_state:
        st.session_state.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if "theme" not in st.session_state:
        st.session_state.theme = DEFAULT_THEME
        
    if "language" not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE

def render_sidebar(llm_service):
    """Render the application sidebar with controls."""
    st.sidebar.header("Newsletter Settings")
    
    # Theme selection
    theme = st.sidebar.radio("Select Theme", options=["Light", "Dark"], index=0, key="theme")
    
    if theme == "Dark":
        apply_dark_theme()
    
    # Language selection
    language = st.sidebar.radio("Select Language", options=["English", "Hebrew"], key="language")
    
    # Provider and model selection
    selected_provider = st.sidebar.selectbox(
        "Select Provider",
        options=llm_service.get_providers(),
        key="selected_provider"
    )
    
    models = llm_service.get_models(selected_provider)
    selected_model = st.sidebar.selectbox(
        "Select Model",
        options=list(models.keys()),
        format_func=lambda x: models[x],
        key="selected_model"
    )
    
    # API key status
    st.sidebar.markdown("### API Key Status")
    api_status = llm_service.check_api_keys()
    for provider, status in api_status.items():
        st.sidebar.markdown(f"{provider} API Key: {'✅' if status else '❌'}")
    
    # Draft controls
    st.sidebar.markdown("---")
    st.sidebar.header("Drafts")
    
    if st.sidebar.button("Save Draft"):
        newsletter = create_newsletter_from_session_state()
        filename = save_draft(newsletter)
        st.sidebar.success(f"Draft saved as {filename}")
    
    draft_files = get_available_drafts()
    selected_draft = st.sidebar.selectbox("Select a draft to load", options=draft_files) if draft_files else None
    
    if st.sidebar.button("Load Draft") and selected_draft:
        newsletter = load_draft(selected_draft)
        update_session_state_from_newsletter(newsletter)
        st.sidebar.success(f"Draft loaded! Language: {st.session_state['language']}")
        st.rerun()
    
    if "loaded_provider" in st.session_state and "loaded_model" in st.session_state:
        st.sidebar.info(f"Loaded provider: {st.session_state['loaded_provider']} with model: {st.session_state['loaded_model']}")

    # Add toggle for Edit Mode
    st.sidebar.markdown("---")
    st.sidebar.header("Newsletter Mode")
    edit_mode = st.sidebar.radio(
        "Choose Mode",
        ["Generate Mode", "Edit Mode"],
        index=0 if not st.session_state.edit_mode else 1
    )
    st.session_state.edit_mode = True if edit_mode == "Edit Mode" else False

def main():
    """Main application entry point."""
    # Initialize the application
    initialize_app()
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Render header
    add_logo_and_banner()
    
    # Render sidebar
    render_sidebar(llm_service)
    
    # Section selection
    section = st.sidebar.radio("Choose Section", ["Newsletter", "Discover News"])

    # Render the appropriate view
    if section == "Newsletter":
        if not st.session_state.edit_mode:
            # Generation Mode
            render_generate_view(llm_service)
        else:
            # Edit Mode
            render_edit_view(llm_service)
    else:
        # News Discovery Mode
        render_news_discovery()

if __name__ == "__main__":
    main()