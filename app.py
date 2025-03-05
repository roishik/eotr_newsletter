#!/Users/roishi/miniconda3/envs/eotr_newsletter/bin/python

import streamlit as st
import requests
from bs4 import BeautifulSoup
from llm_service import LLMService
import datetime
import os
import json
import streamlit.components.v1 as components
from discovery_view import render_news_discovery

# Custom Design Imports
import base64
from io import BytesIO

# Enhanced Configuration
st.set_page_config(
    page_title="Mobileye Newsletter Generator", 
    page_icon="🚗", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom UI Functions
def add_logo_and_banner():
    st.markdown(
        """
        <div style="
            background: linear-gradient(to right, #2e6c80, #5F9EA0);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            color: white;
        ">
            <div style="flex: 0 0 50px;">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="white"/>
                    <path d="M2 17L12 22L22 17" fill="white"/>
                    <path d="M2 12L12 17L22 12" fill="white"/>
                </svg>
            </div>
            <div style="flex: 1; margin-left: 15px;">
                <h1 style="margin: 0; font-size: 1.8rem; color: white;">Mobileye Newsletter Generator</h1>
                <p style="margin: 0; opacity: 0.8;">Generate professional newsletters with AI assistance</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

def card(title, content, key=None):
    """Create a card-like container with a title and content"""
    st.markdown(f"""
    <div style="
        background-color: {'#3c4043' if st.session_state.get('theme', 'Light') == 'Dark' else 'white'};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: {'#8ab4f8' if st.session_state.get('theme', 'Light') == 'Dark' else '#2e6c80'};
            margin-top: 0;
            font-size: 1.2rem;
            border-bottom: 1px solid {'#5f6368' if st.session_state.get('theme', 'Light') == 'Dark' else '#e6e6e6'};
            padding-bottom: 8px;
        ">{title}</h3>
        {content}
    </div>
    """, unsafe_allow_html=True)

def loading_animation():
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div style="
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #5F9EA0;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
    </div>
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

def show_completion_status():
    # Calculate completion percentage (existing implementation)
    sections = ["Windshield View"]
    num_rearview = st.session_state.get("num_rearview", 3)
    for i in range(1, int(num_rearview) + 1):
        sections.append(f"Rearview Mirror {i}")
    sections.extend(["Dashboard Data", "The Next Lane"])
    
    completed_sections = [section for section in sections 
                         if section in st.session_state.get("generated_sections", {})]
    
    completion_percentage = int(len(completed_sections) / len(sections) * 100)
    
    # Color based on completion
    if completion_percentage < 30:
        color = "#dc3545"  # Red
    elif completion_percentage < 70:
        color = "#ffc107"  # Yellow
    else:
        color = "#28a745"  # Green
    
    st.markdown(f"""
    <div style="margin: 20px 0;">
        <h4 style="margin-bottom: 5px;">Newsletter Completion: {completion_percentage}%</h4>
        <div style="
            background-color: #e9ecef;
            border-radius: 4px;
            height: 10px;
            width: 100%;
        ">
            <div style="
                background-color: {color};
                width: {completion_percentage}%;
                height: 100%;
                border-radius: 4px;
                transition: width 0.5s ease;
            "></div>
        </div>
        <div style="
            display: flex;
            flex-wrap: wrap;
            margin-top: 10px;
            gap: 8px;
        ">
    """, unsafe_allow_html=True)
    
    for section in sections:
        is_complete = section in st.session_state.get("generated_sections", {})
        status_color = "#28a745" if is_complete else "#6c757d"
        status_icon = "✓" if is_complete else "○"
        
        st.markdown(f"""
        <div style="
            background-color: {status_color}22;
            color: {status_color};
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            display: inline-block;
        ">
            {status_icon} {section}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Keep your existing imports and configurations here...
# Initialize LLM service
llm_service = LLMService()

# Create necessary directories
os.makedirs("drafts", exist_ok=True)

# Your existing DEFAULT_PROMPTS and other configurations...

def main():
    # Custom theme control
    st.markdown("""
    <style>
    /* Enhanced CSS Styling */
    .stApp {
        background: linear-gradient(to bottom right, #f8f9fa, #e9ecef);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2e6c80;
        letter-spacing: 0.5px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #5F9EA0;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #4F8E90;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add custom logo and banner
    add_logo_and_banner()
    
    # Rest of your main() function remains largely the same...
    if "generated_sections" not in st.session_state:
        st.session_state.generated_sections = {}

    # Sidebar theme and model selection
    st.sidebar.header("Newsletter Settings")
    theme = st.sidebar.radio("Select Theme", options=["Light", "Dark"], index=0)
    st.session_state['theme'] = theme

    # Dark mode styling if selected
    if theme == "Dark":
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(to bottom right, #2C3333, #1A1A1A);
                color: #e8eaed;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )

    # Provider selection (existing code)
    selected_provider = st.sidebar.selectbox(
        "Select Provider",
        options=llm_service.get_providers(),
        key="selected_provider"
    )

    # Section selection
    section = st.sidebar.radio("Choose Section", ["Newsletter", "Discover News"])

    # Newsletter Generation Section
    if section == "Newsletter":
        # Two-column layout
        main_panel, right_panel = st.columns([1, 2])

        with main_panel:
            # Your existing input sections with potential card wrapping
            with st.expander("Overall Prompt", expanded=False):
                st.text_area(
                    "Overall Newsletter Style",
                    value=DEFAULT_PROMPTS["overall"],
                    key="overall_prompt",
                    height=200
                )
            
            # More sections using card() function if desired
            card("Windshield View", """
                <div>
                    <input type="text" placeholder="Enter article URLs" />
                    <textarea placeholder="Additional notes"></textarea>
                </div>
            """)

        with right_panel:
            # Progress and generated content
            show_completion_status()
            
            # Existing right panel content...

    elif section == "Discover News":
        render_news_discovery()

# Existing save_draft(), load_draft(), and other helper functions...

if __name__ == "__main__":
    main()