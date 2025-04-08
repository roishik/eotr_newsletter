#!/Users/roishi/miniconda3/envs/eotr_newsletter/bin/python

import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Import configuration first
from config.settings import APP_TITLE, APP_ICON, DEFAULT_THEME, DEFAULT_LANGUAGE

# Set page configuration
st.set_page_config(
    page_title=APP_TITLE, 
    page_icon=APP_ICON, 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Import remaining configuration
from config.prompts import DEFAULT_PROMPTS

# Import services
from services.llm_service import LLMService
from services.news_service import NewsAPIService

# Import models
from models.newsletter import Newsletter

# Import UI components
from ui.components import (
    add_logo_and_banner,
    display_language_indicator,
    add_theme_selector,
    add_keyboard_shortcuts,
    add_drag_drop_support,
    render_section
)
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
from utils.content_utils import export_newsletter
from utils.autosave import setup_autosave
from utils.collaboration import setup_collaboration

# Initialize services
llm_service = LLMService()
news_service = NewsAPIService()

# Setup session state
if "newsletter_data" not in st.session_state:
    st.session_state.newsletter_data = None
if "current_section" not in st.session_state:
    st.session_state.current_section = "Windshield View"
if "newsletter_id" not in st.session_state:
    st.session_state.newsletter_id = f"newsletter_{int(datetime.now().timestamp())}"

# Setup UI components
add_logo_and_banner()
display_language_indicator()
add_theme_selector()
add_keyboard_shortcuts()
add_drag_drop_support()

# Setup auto-save and collaboration
setup_autosave()
setup_collaboration()

# Main content
st.title("Newsletter Generator")

# Sidebar controls
with st.sidebar:
    st.subheader("Controls")
    
    # New newsletter button
    if st.button("📝 New Newsletter"):
        st.session_state.newsletter_data = Newsletter()
        st.session_state.newsletter_id = f"newsletter_{int(datetime.now().timestamp())}"
        st.success("Created new newsletter!")
    
    # Load draft button
    if st.button("📂 Load Draft"):
        st.session_state.show_draft_dialog = True
    
    # Save draft button
    if st.button("💾 Save Draft"):
        if st.session_state.newsletter_data:
            draft_path = Path("drafts") / f"{st.session_state.newsletter_id}.json"
            draft_path.parent.mkdir(exist_ok=True)
            with open(draft_path, "w", encoding="utf-8") as f:
                json.dump(st.session_state.newsletter_data.to_dict(), f, ensure_ascii=False, indent=2)
            st.success("Draft saved successfully!")
    
    # Export options
    st.subheader("Export")
    export_format = st.selectbox(
        "Format",
        ["HTML", "PDF", "DOCX", "Markdown", "JSON", "YAML"]
    )
    if st.button("📤 Export"):
        if st.session_state.newsletter_data:
            output_path = f"exports/{st.session_state.newsletter_id}.{export_format.lower()}"
            export_newsletter(
                st.session_state.newsletter_data.to_html(),
                st.session_state.newsletter_data.to_dict(),
                export_format,
                output_path
            )
            st.success(f"Newsletter exported to {output_path}!")

# Main content area
if st.session_state.newsletter_data:
    # Section selector
    sections = [
        "Windshield View",
        "Dashboard Data",
        "The Next Lane",
        "Rearview Mirror 1",
        "Rearview Mirror 2",
        "Rearview Mirror 3"
    ]
    
    selected_section = st.selectbox(
        "Select Section",
        sections,
        index=sections.index(st.session_state.current_section)
    )
    st.session_state.current_section = selected_section
    
    # Section content
    section_data = st.session_state.newsletter_data.get_section(selected_section)
    if section_data:
        render_section(selected_section, section_data.to_dict())
        
        # Section controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Generate Content"):
                st.session_state.generate_section = True
        
        with col2:
            if st.button("✏️ Edit Content"):
                st.session_state.edit_section = True
        
        # Content generation
        if st.session_state.get("generate_section", False):
            with st.spinner("Generating content..."):
                content = llm_service.generate_content(
                    provider="openai",
                    model="gpt-4",
                    system_prompt=f"Generate content for the {selected_section} section of a Mobileye newsletter.",
                    user_prompt="Please write engaging and informative content."
                )
                section_data.content = content
                st.session_state.newsletter_data.update_section(selected_section, section_data)
                st.session_state.generate_section = False
                st.success("Content generated successfully!")
        
        # Content editing
        if st.session_state.get("edit_section", False):
            edited_content = st.text_area(
                "Edit Content",
                value=section_data.content,
                height=300
            )
            if st.button("Save Changes"):
                section_data.content = edited_content
                st.session_state.newsletter_data.update_section(selected_section, section_data)
                st.session_state.edit_section = False
                st.success("Changes saved successfully!")
else:
    st.info("Create a new newsletter or load a draft to get started!")

# Draft dialog
if st.session_state.get("show_draft_dialog", False):
    with st.sidebar.expander("Load Draft", expanded=True):
        draft_files = list(Path("drafts").glob("*.json"))
        if not draft_files:
            st.info("No drafts found.")
        else:
            selected_draft = st.selectbox(
                "Select Draft",
                [f.name for f in draft_files]
            )
            if st.button("Load"):
                with open(Path("drafts") / selected_draft, "r", encoding="utf-8") as f:
                    draft_data = json.load(f)
                    st.session_state.newsletter_data = Newsletter.from_dict(draft_data)
                    st.session_state.newsletter_id = selected_draft.replace(".json", "")
                    st.success("Draft loaded successfully!")
                    st.session_state.show_draft_dialog = False
                    st.rerun()
        if st.button("Cancel"):
            st.session_state.show_draft_dialog = False

def initialize_app():
    """Initialize the application settings."""
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