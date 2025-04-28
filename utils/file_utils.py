import os
import json
import datetime
import streamlit as st
from typing import Dict, List, Optional
from models.newsletter import Newsletter

def get_available_drafts(drafts_dir: str = "drafts") -> List[str]:
    """
    Get a list of available draft files.
    
    Args:
        drafts_dir: Directory containing draft files
        
    Returns:
        List of draft filenames
    """
    os.makedirs(drafts_dir, exist_ok=True)
    draft_files = [f for f in os.listdir(drafts_dir) if f.endswith(".json")]
    draft_files.sort(reverse=True)  # Latest first
    return draft_files

def save_draft(newsletter: Newsletter, drafts_dir: str = "drafts") -> str:
    """
    Save the current newsletter state to a draft file.
    
    Args:
        newsletter: Newsletter object to save
        drafts_dir: Directory to save the draft in
        
    Returns:
        Path to the saved draft file
    """
    return newsletter.save(drafts_dir)

def load_draft(filename: str, drafts_dir: str = "drafts") -> Newsletter:
    """
    Load a newsletter from a draft file.
    
    Args:
        filename: Name of the draft file
        drafts_dir: Directory containing draft files
        
    Returns:
        Loaded Newsletter object
    """
    full_path = os.path.join(drafts_dir, filename)
    return Newsletter.load(full_path)

def create_drafts_directory() -> None:
    """Create the drafts directory if it doesn't exist."""
    os.makedirs("drafts", exist_ok=True)

def format_download_filename(prefix: str = "newsletter") -> str:
    """
    Format a filename for downloading the newsletter.
    
    Args:
        prefix: Prefix for the filename
        
    Returns:
        Formatted filename with timestamp
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.html"

def update_session_state_from_newsletter(newsletter: Newsletter) -> None:
    """
    Update the session state from a Newsletter object.
    
    Args:
        newsletter: Newsletter object to load from
    """
    # Save the loaded provider and model separately for display
    st.session_state["loaded_provider"] = newsletter.selected_provider
    st.session_state["loaded_model"] = newsletter.selected_model
    #st.session_state["language"] = newsletter.language # removed to avoid error
    # st.session_state["theme"] = newsletter.theme # removed to avoid error
    
    # Main properties
    st.session_state["overall_prompt"] = newsletter.overall_prompt
    st.session_state["num_rearview"] = newsletter.num_rearview
    st.session_state["generated_sections"] = newsletter.get_generated_sections()
    st.session_state["edited_sections"] = newsletter.edited_sections
    
    # Windshield section
    st.session_state["windshield_urls"] = newsletter.windshield.urls
    st.session_state["windshield_notes"] = newsletter.windshield.notes
    st.session_state["windshield_prompt"] = newsletter.windshield.prompt
    
    # Dashboard section
    st.session_state["dashboard_urls"] = newsletter.dashboard.urls
    st.session_state["dashboard_notes"] = newsletter.dashboard.notes
    st.session_state["dashboard_prompt"] = newsletter.dashboard.prompt
    
    # Next Lane section
    st.session_state["nextlane_urls"] = newsletter.nextlane.urls
    st.session_state["nextlane_notes"] = newsletter.nextlane.notes
    st.session_state["nextlane_prompt"] = newsletter.nextlane.prompt
    
    # Rearview sections
    for i in range(1, newsletter.num_rearview + 1):
        st.session_state[f"rearview_urls_{i}"] = newsletter.rearview_sections[i].urls
        st.session_state[f"rearview_notes_{i}"] = newsletter.rearview_sections[i].notes
        st.session_state[f"rearview_prompt_{i}"] = newsletter.rearview_sections[i].prompt

def create_newsletter_from_session_state() -> Newsletter:
    """
    Create a Newsletter object from the current session state.
    
    Returns:
        Newsletter object with current session state
    """
    newsletter = Newsletter(
        overall_prompt=st.session_state.get("overall_prompt", ""),
        num_rearview=st.session_state.get("num_rearview", 3),
        edited_sections=st.session_state.get("edited_sections", {}),
        selected_provider=st.session_state.get("selected_provider", "OpenAI"),
        selected_model=st.session_state.get("selected_model", "gpt-4o"),
        language=st.session_state.get("language", "English"),
        theme=st.session_state.get("theme", "Light")
    )
    
    # Load main sections
    newsletter.windshield.urls = st.session_state.get("windshield_urls", "")
    newsletter.windshield.notes = st.session_state.get("windshield_notes", "")
    newsletter.windshield.prompt = st.session_state.get("windshield_prompt", "")
    newsletter.windshield.content = st.session_state.get("generated_sections", {}).get("Windshield View", "")
    
    newsletter.dashboard.urls = st.session_state.get("dashboard_urls", "")
    newsletter.dashboard.notes = st.session_state.get("dashboard_notes", "")
    newsletter.dashboard.prompt = st.session_state.get("dashboard_prompt", "")
    newsletter.dashboard.content = st.session_state.get("generated_sections", {}).get("Dashboard Data", "")
    
    newsletter.nextlane.urls = st.session_state.get("nextlane_urls", "")
    newsletter.nextlane.notes = st.session_state.get("nextlane_notes", "")
    newsletter.nextlane.prompt = st.session_state.get("nextlane_prompt", "")
    newsletter.nextlane.content = st.session_state.get("generated_sections", {}).get("The Next Lane", "")
    
    # Load rearview sections
    for i in range(1, newsletter.num_rearview + 1):
        newsletter.rearview_sections[i].urls = st.session_state.get(f"rearview_urls_{i}", "")
        newsletter.rearview_sections[i].notes = st.session_state.get(f"rearview_notes_{i}", "")
        newsletter.rearview_sections[i].prompt = st.session_state.get(f"rearview_prompt_{i}", "")
        newsletter.rearview_sections[i].content = st.session_state.get("generated_sections", {}).get(f"Rearview Mirror {i}", "")
    
    return newsletter