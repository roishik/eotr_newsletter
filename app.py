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
    
    # Display the progress bar
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
    """, unsafe_allow_html=True)
    
    # Create horizontal layout using Streamlit columns
    cols = st.columns(len(sections))
    
    for i, (col, section) in enumerate(zip(cols, sections)):
        with col:
            is_complete = section in st.session_state.get("generated_sections", {})
            if is_complete:
                st.markdown(f"✅ {section}")
            else:
                st.markdown(f"⭕ {section}")
    
    # Close the div for the progress bar
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# Initialize LLM service
llm_service = LLMService()

# Create necessary directories
os.makedirs("drafts", exist_ok=True)

# Default prompts and configuration
DEFAULT_PROMPTS = {
    "overall": (
        "What are you doing?:\n"
        "You are writing a section inside an internal Mobileye newsletter on autonomous cars, the car industry, and AI news. "
        "Only write about the relevant content of this section - This text will be a part of the big newsletter (no need for welcome notes). "
        "Avoid AI chatbot introductions, such as 'here is the response to your request'.\n"
        "Writing style:\n"
        "Write in a dynamic, conversational, and friendly tone, as if speaking directly to the reader. Keep the language approachable but insightful, "
        "mixing professional analysis with a sense of curiosity and enthusiasm. Use simple, clear sentences, but don't shy away from technical terms when necessary—"
        "just explain them naturally and without overcomplication. Add thoughtful commentary that connects news or updates to broader implications, offering personal insights or lessons. "
        "Maintain an optimistic and forward-thinking voice, encouraging readers to reflect and engage while keeping the overall mood warm and encouraging. "
        "Don't be too optimistic and avoid making announcements that are bigger than the actual news.\n"
        "Length:\n"
        "Keep the response concise and focused on the key points.\n"
        "What to write about?\n"
        "Offer a new lens on the news, providing a fresh perspective or a unique angle that doubts the status quo or offers a new way of thinking."
    ),
    "windshield": (
        "Summarize the articles in 2–3 concise paragraphs focusing on their relevance to Mobileye's work. "
        "Please be succinct and avoid unnecessary details. Write in first-person singular."
    ),
    "rearview": (
        "Provide a brief headline (bolded text, not an actual headline) and a one-sentence summary. Keep the response extremely concise—no more than 2 sentences total."
    ),
    "dashboard": (
        "Write 3 parts:\n"
        "- What's New: Describe key trends or insights concisely.\n"
        "- Why It Matters: Explain the impact on Mobileye succinctly.\n"
        "- What I Think: Share a brief personal opinion."
    ),
    "nextlane": (
        "Summarize competitor/academic news in 2–3 concise paragraphs, highlighting its implications for Mobileye. "
        "Keep it brief and to the point."
    )
}

# ----------------------------------------------------------------
# Functions for saving and loading draft data

def save_draft():
    """Saves the current state of all input fields and generated sections to a JSON file in the drafts folder."""
    draft_data = {
        "overall_prompt": st.session_state.get("overall_prompt", DEFAULT_PROMPTS["overall"]),
        "windshield_urls": st.session_state.get("windshield_urls", ""),
        "windshield_notes": st.session_state.get("windshield_notes", ""),
        "windshield_prompt": st.session_state.get("windshield_prompt", DEFAULT_PROMPTS["windshield"]),
        "num_rearview": st.session_state.get("num_rearview", 3),
        "dashboard_urls": st.session_state.get("dashboard_urls", ""),
        "dashboard_notes": st.session_state.get("dashboard_notes", ""),
        "dashboard_prompt": st.session_state.get("dashboard_prompt", DEFAULT_PROMPTS["dashboard"]),
        "nextlane_urls": st.session_state.get("nextlane_urls", ""),
        "nextlane_notes": st.session_state.get("nextlane_notes", ""),
        "nextlane_prompt": st.session_state.get("nextlane_prompt", DEFAULT_PROMPTS["nextlane"]),
        "generated_sections": st.session_state.get("generated_sections", {}),
        "edited_sections": st.session_state.get("edited_sections", {}),
        "selected_provider": st.session_state.get("selected_provider", "OpenAI"),
        "selected_model": st.session_state.get("selected_model", "gpt-4o"),
    }
    for i in range(1, 6):
        draft_data[f"rearview_urls_{i}"] = st.session_state.get(f"rearview_urls_{i}", "")
        draft_data[f"rearview_notes_{i}"] = st.session_state.get(f"rearview_notes_{i}", "")
        draft_data[f"rearview_prompt_{i}"] = st.session_state.get(f"rearview_prompt_{i}", DEFAULT_PROMPTS["rearview"])
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"drafts/draft_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(draft_data, f, indent=4)
    st.sidebar.success(f"Draft saved as {filename}")

def load_draft(filename):
    """Loads the selected draft and updates session state accordingly."""
    with open(f"drafts/{filename}", "r") as f:
        draft_data = json.load(f)
    
    # Save the loaded provider and model separately for display
    st.session_state["loaded_provider"] = draft_data.get("selected_provider", "Unknown")
    st.session_state["loaded_model"] = draft_data.get("selected_model", "Unknown")

    for key, value in draft_data.items():
        if key not in ["selected_provider", "selected_model"]:  # don't update provider/model due to Streamlit limitation
            st.session_state[key] = value

    st.sidebar.success("Draft loaded!")
    st.rerun()

# ----------------------------------------------------------------
# Functions for newsletter generation

def extract_article_text(urls):
    """Fetches and combines article content from multiple URLs."""
    combined_text = ""
    url_list = [url.strip() for url in urls.split(";;") if url.strip()]
    for url in url_list:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            article = "\n".join(p.get_text() for p in paragraphs)
            combined_text += article + "\n\n"
        except Exception as e:
            st.error(f"Error fetching URL {url}: {e}")
    return combined_text.strip()

def generate_section_content(section_key, article_text, notes, section_prompt):
    loading_animation()
    """Generates content using the selected model through LLM service."""
    user_content = (
        f"{section_prompt}\n\nCombined Article Content:\n{article_text}\n\nNotes: {notes if notes else ''}"
    )
    try:
        generated_text = llm_service.generate_content(
            provider=st.session_state.get("selected_provider", "OpenAI"),
            model=st.session_state.get("selected_model", "gpt-4o"),
            system_prompt=DEFAULT_PROMPTS["overall"],
            user_prompt=user_content
        )
        return generated_text
    except Exception as e:
        st.error(str(e))
        return ""

def edit_section_content(section_key, original_text, edit_prompt):
    loading_animation()
    """Edits the content of a section according to the edit prompt."""
    user_content = (
        f"Please edit the following newsletter section according to these instructions: {edit_prompt}\n\n"
        f"Original Section Content:\n{original_text}"
    )
    try:
        edited_text = llm_service.generate_content(
            provider=st.session_state.get("selected_provider", "OpenAI"),
            model=st.session_state.get("selected_model", "gpt-4o"),
            system_prompt=DEFAULT_PROMPTS["overall"],
            user_prompt=user_content
        )
        return edited_text
    except Exception as e:
        st.error(str(e))
        return ""

def generate_newsletter_html(sections_content, theme="light"):
    loading_animation()
    if theme.lower() == "dark":
        style = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #303134;
                color: #e8eaed;
                line-height: 1.6;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: #3c4043;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                border-radius: 12px;
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #1e3a8a, #3b82f6);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 28px;
                letter-spacing: 1px;
            }
            .header p {
                margin: 10px 0 0;
                opacity: 0.8;
            }
            .content {
                padding: 30px;
            }
            .section {
                margin-bottom: 40px;
                border-bottom: 1px solid #5f6368;
                padding-bottom: 20px;
            }
            .section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            .section h2 {
                color: #8ab4f8;
                font-size: 22px;
                margin-top: 0;
                margin-bottom: 15px;
            }
            .footer {
                background-color: #292b2f;
                padding: 20px;
                text-align: center;
                font-size: 14px;
                color: #9aa0a6;
            }
        </style>
        """
    else:
        style = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: #fff;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border-radius: 12px;
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #5F9EA0, #7FB3D5);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 28px;
                letter-spacing: 1px;
            }
            .header p {
                margin: 10px 0 0;
                opacity: 0.8;
            }
            .content {
                padding: 30px;
            }
            .section {
                margin-bottom: 40px;
                border-bottom: 1px solid #eee;
                padding-bottom: 20px;
            }
            .section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            .section h2 {
                color: #2e6c80;
                font-size: 22px;
                margin-top: 0;
                margin-bottom: 15px;
            }
            .footer {
                background-color: #f9f9f9;
                padding: 20px;
                text-align: center;
                font-size: 14px;
                color: #777;
            }
        </style>
        """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mobileye Newsletter</title>
        {style}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mobileye Newsletter</h1>
                <p>Insights from the world of autonomous vehicles & AI</p>
            </div>
            <div class="content">
                {sections_content}
            </div>
            <div class="footer">
                <p>© {datetime.datetime.now().year} Mobileye • Generated on {datetime.datetime.now().strftime("%B %d, %Y")}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

# ----------------------------------------------------------------
def main():
    # Apply custom theme control
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
    
    # Ensure required session state variables exist
    if "generated_sections" not in st.session_state:
        st.session_state.generated_sections = {}
    
    if "edited_sections" not in st.session_state:
        st.session_state.edited_sections = {}
    
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    # Sidebar controls
    st.sidebar.header("Newsletter Settings")
    theme = st.sidebar.radio("Select Theme", options=["Light", "Dark"], index=0)
    st.session_state['theme'] = theme

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
        save_draft()
    draft_files = [f for f in os.listdir("drafts") if f.endswith(".json")]
    draft_files.sort(reverse=True)  # Latest first
    selected_draft = st.sidebar.selectbox("Select a draft to load", options=draft_files) if draft_files else None
    if st.sidebar.button("Load Draft") and selected_draft:
        load_draft(selected_draft)
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
    
    # Section selection
    section = st.sidebar.radio("Choose Section", ["Newsletter", "Discover News"])

    if section == "Newsletter":
        if not st.session_state.edit_mode:
            # Generation Mode
            # Two-column layout
            main_panel, right_panel = st.columns([1, 2])

            with main_panel:
                st.header("Content Generation")
                with st.expander("Overall Prompt", expanded=False):
                    st.text_area(
                        "Overall Newsletter Style",
                        value=st.session_state.get("overall_prompt", DEFAULT_PROMPTS["overall"]),
                        key="overall_prompt",
                        height=150
                    )

                # Windshield View Section
                st.subheader("Windshield View")
                windshield_urls = st.text_input(
                    "Enter article URLs (separated by ';;')",
                    value=st.session_state.get("windshield_urls", ""),
                    key="windshield_urls"
                )
                windshield_notes = st.text_area(
                    "Notes",
                    value=st.session_state.get("windshield_notes", ""),
                    key="windshield_notes",
                    height=100
                )
                windshield_prompt = st.text_area(
                    "Section Prompt",
                    value=st.session_state.get("windshield_prompt", DEFAULT_PROMPTS["windshield"]),
                    key="windshield_prompt",
                    height=100
                )
                if st.button("Generate Windshield Section"):
                    with st.spinner("Generating Windshield section..."):
                        article_text = extract_article_text(windshield_urls)
                        generated_text = generate_section_content("windshield", article_text, windshield_notes, windshield_prompt)
                        st.success("Windshield section generated!")
                        st.session_state.generated_sections["Windshield View"] = generated_text

                # Rearview Mirror Section (multiple stories)
                st.subheader("Rearview Mirror (Multiple Stories)")
                num_rearview = st.number_input(
                    "Number of Rearview Stories",
                    min_value=1,
                    max_value=5,
                    value=st.session_state.get("num_rearview", 3),
                    step=1,
                    key="num_rearview"
                )
                for i in range(1, int(num_rearview) + 1):
                    st.markdown(f"**Story {i}**")
                    story_urls = st.text_input(
                        f"Story {i} URLs (separated by ';;')",
                        value=st.session_state.get(f"rearview_urls_{i}", ""),
                        key=f"rearview_urls_{i}"
                    )
                    story_notes = st.text_area(
                        f"Story {i} Notes",
                        value=st.session_state.get(f"rearview_notes_{i}", ""),
                        key=f"rearview_notes_{i}",
                        height=80
                    )
                    story_prompt = st.text_area(
                        f"Story {i} Prompt",
                        value=st.session_state.get(f"rearview_prompt_{i}", DEFAULT_PROMPTS["rearview"]),
                        key=f"rearview_prompt_{i}",
                        height=80
                    )
                    if st.button(f"Generate Rearview {i} Section"):
                        with st.spinner(f"Generating Rearview {i} section..."):
                            article_text = extract_article_text(st.session_state[f"rearview_urls_{i}"])
                            generated_text = generate_section_content("rearview", article_text, st.session_state[f"rearview_notes_{i}"], st.session_state[f"rearview_prompt_{i}"])
                            st.success(f"Rearview {i} section generated!")
                            st.session_state.generated_sections[f"Rearview Mirror {i}"] = generated_text

                # Dashboard Data Section
                st.subheader("Dashboard Data")
                dashboard_urls = st.text_input(
                    "Enter article URLs (separated by ';;')",
                    value=st.session_state.get("dashboard_urls", ""),
                    key="dashboard_urls"
                )
                dashboard_notes = st.text_area(
                    "Notes",
                    value=st.session_state.get("dashboard_notes", ""),
                    key="dashboard_notes",
                    height=100
                )
                dashboard_prompt = st.text_area(
                    "Section Prompt",
                    value=st.session_state.get("dashboard_prompt", DEFAULT_PROMPTS["dashboard"]),
                    key="dashboard_prompt",
                    height=100
                )
                if st.button("Generate Dashboard Section"):
                    with st.spinner("Generating Dashboard section..."):
                        article_text = extract_article_text(dashboard_urls)
                        generated_text = generate_section_content("dashboard", article_text, dashboard_notes, dashboard_prompt)
                        st.success("Dashboard section generated!")
                        st.session_state.generated_sections["Dashboard Data"] = generated_text

                # The Next Lane Section
                st.subheader("The Next Lane")
                nextlane_urls = st.text_input(
                    "Enter article URLs (separated by ';;')",
                    value=st.session_state.get("nextlane_urls", ""),
                    key="nextlane_urls"
                )
                nextlane_notes = st.text_area(
                    "Notes",
                    value=st.session_state.get("nextlane_notes", ""),
                    key="nextlane_notes",
                    height=100
                )
                nextlane_prompt = st.text_area(
                    "Section Prompt",
                    value=st.session_state.get("nextlane_prompt", DEFAULT_PROMPTS["nextlane"]),
                    key="nextlane_prompt",
                    height=100
                )
                if st.button("Generate Next Lane Section"):
                    with st.spinner("Generating The Next Lane section..."):
                        article_text = extract_article_text(nextlane_urls)
                        generated_text = generate_section_content("nextlane", article_text, nextlane_notes, nextlane_prompt)
                        st.success("The Next Lane section generated!")
                        st.session_state.generated_sections["The Next Lane"] = generated_text

                st.markdown("---")
                if st.button("Create Newsletter"):
                    with st.spinner("Assembling Newsletter..."):
                        sections_content = ""
                        # Fixed order: Windshield, Rearview stories, Dashboard, Next Lane
                        sections = []
                        sections.append(("Windshield View", st.session_state.generated_sections.get("Windshield View", "Not generated yet.")))
                        for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                            sections.append((f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", "Not generated yet.")))
                        sections.append(("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", "Not generated yet.")))
                        sections.append(("The Next Lane", st.session_state.generated_sections.get("The Next Lane", "Not generated yet.")))
                        for title, content in sections:
                            sections_content += f"""
                            <div class="section">
                                <h2>{title}</h2>
                                <p>{content}</p>
                            </div>
                            """
                        newsletter_html = generate_newsletter_html(sections_content, theme=theme)
                        st.success("Newsletter Created!")
                        components.html(newsletter_html, height=600, scrolling=True)
                        st.download_button(
                            "Download Newsletter",
                            data=newsletter_html,
                            file_name=f"newsletter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
            with right_panel:
                st.header("Newsletter Summary")
                # Display completion status at the top
                show_completion_status()
                st.markdown("This panel displays the generated sections in fixed order. If a section has not been generated yet, a placeholder is shown.")
                def display_section(title, content):
                    st.markdown(f"### {title}")
                    st.write(content if content else "Not generated yet.")
                display_section("Windshield View", st.session_state.generated_sections.get("Windshield View", ""))
                for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                    display_section(f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", ""))
                display_section("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", ""))
                display_section("The Next Lane", st.session_state.generated_sections.get("The Next Lane", ""))
                
                # Add button to switch to edit mode
                st.markdown("---")
                if st.button("Switch to Edit Mode"):
                    st.session_state.edit_mode = True
                    st.rerun()
        
        else:
            # Edit Mode
            st.header("Newsletter Edit Mode")
            st.markdown("""
            <div style="
                background-color: #f8f9fa;
                border-left: 4px solid #5F9EA0;
                padding: 10px 15px;
                margin-bottom: 20px;
                border-radius: 4px;
            ">
                <h4 style="margin-top: 0; color: #2e6c80;">📝 Edit Mode</h4>
                <p>In this mode, you can review and edit each section of your newsletter, then ask the AI to refine it based on your instructions.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if any sections have been generated
            if not st.session_state.generated_sections:
                st.warning("No sections have been generated yet. Please switch to Generate Mode first to create content.")
                if st.button("Switch to Generate Mode"):
                    st.session_state.edit_mode = False
                    st.rerun()
            else:
                # Layout for edit mode
                sections = []
                sections.append("Windshield View")
                for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                    sections.append(f"Rearview Mirror {i}")
                sections.append("Dashboard Data")
                sections.append("The Next Lane")
                
                # Setup three-column layout as per requirements
                selected_section = st.selectbox("Select section to edit", sections)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.subheader("Original Content")
                    original_text = st.session_state.generated_sections.get(selected_section, "")
                    if original_text:
                        # Use text area to allow manual edits
                        edited_text = st.text_area(
                            "You can also edit directly:",
                            value=original_text,
                            height=300,
                            key=f"manual_edit_{selected_section}"
                        )
                        # Store manual edits in session state
                        if edited_text != original_text:
                            st.session_state.edited_sections[selected_section] = edited_text
                    else:
                        st.info(f"No content has been generated for {selected_section} yet.")
                
                with col2:
                    st.subheader("Edit Instructions")
                    edit_prompt = st.text_area(
                        "Enter your editing instructions",
                        value="",
                        height=150,
                        placeholder="e.g., Make it shorter, Use more technical language, Add more industry context, etc.",
                        key=f"edit_prompt_{selected_section}"
                    )
                    
                    if st.button("Apply AI Edit"):
                        if not original_text:
                            st.error("Cannot edit empty content. Please generate content first.")
                        elif not edit_prompt:
                            st.error("Please provide editing instructions.")
                        else:
                            with st.spinner("Applying edits..."):
                                # Get the latest version (either original or manually edited)
                                text_to_edit = st.session_state.edited_sections.get(selected_section, original_text)
                                edited_text = edit_section_content(selected_section, text_to_edit, edit_prompt)
                                st.session_state.edited_sections[selected_section] = edited_text
                                st.success("Edit applied!")
                                st.rerun()
                
                with col3:
                    st.subheader("Edited Result")
                    edited_text = st.session_state.edited_sections.get(selected_section, "")
                    if edited_text:
                        st.write(edited_text)
                        if st.button("Keep this edit"):
                            st.session_state.generated_sections[selected_section] = edited_text
                            st.success(f"Updated {selected_section} with edited version!")
                    else:
                        st.info("No edits applied yet.")
                
                # Button to generate final newsletter with edits
                st.markdown("---")
                if st.button("Generate Final Newsletter"):
                    with st.spinner("Assembling final newsletter..."):
                        # First update any edited sections into the generated_sections
                        for section, content in st.session_state.edited_sections.items():
                            if content:  # Only update if there's content
                                st.session_state.generated_sections[section] = content
                        
                        # Then generate the newsletter with the updated sections
                        sections_content = ""
                        # Fixed order as before
                        section_pairs = []
                        section_pairs.append(("Windshield View", st.session_state.generated_sections.get("Windshield View", "Not generated yet.")))
                        for i in range(1, int(st.session_state.get("num_rearview", 3)) + 1):
                            section_pairs.append((f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", "Not generated yet.")))
                        section_pairs.append(("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", "Not generated yet.")))
                        section_pairs.append(("The Next Lane", st.session_state.generated_sections.get("The Next Lane", "Not generated yet.")))
                        
                        for title, content in section_pairs:
                            sections_content += f"""
                            <div class="section">
                                <h2>{title}</h2>
                                <p>{content}</p>
                            </div>
                            """
                        
                        newsletter_html = generate_newsletter_html(sections_content, theme=theme)
                        st.success("Final Newsletter Created!")
                        components.html(newsletter_html, height=600, scrolling=True)
                        st.download_button(
                            "Download Final Newsletter",
                            data=newsletter_html,
                            file_name=f"final_newsletter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
                
                # Option to return to generation mode
                if st.button("Return to Generate Mode"):
                    st.session_state.edit_mode = False
                    st.rerun()
    
    elif section == "Discover News":
        render_news_discovery()

if __name__ == "__main__":
    main()