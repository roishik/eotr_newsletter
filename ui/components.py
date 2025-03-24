import streamlit as st

def add_logo_and_banner(title="Mobileye Newsletter Generator", subtitle="Generate professional newsletters with AI assistance"):
    """Renders the application header with logo and banner."""
    st.markdown(
        f"""
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
                <h1 style="margin: 0; font-size: 1.8rem; color: white;">{title}</h1>
                <p style="margin: 0; opacity: 0.8;">{subtitle}</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

def card(title, content, key=None):
    """Create a card-like container with a title and content."""
    is_dark = st.session_state.get('theme', 'Light') == 'Dark'
    
    bg_color = '#3c4043' if is_dark else 'white'
    title_color = '#8ab4f8' if is_dark else '#2e6c80'
    border_color = '#5f6368' if is_dark else '#e6e6e6'
    
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    ">
        <h3 style="
            color: {title_color};
            margin-top: 0;
            font-size: 1.2rem;
            border-bottom: 1px solid {border_color};
            padding-bottom: 8px;
        ">{title}</h3>
        {content}
    </div>
    """, unsafe_allow_html=True)

def loading_animation():
    """Display a loading spinner animation."""
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

def show_completion_status(sections, generated_sections):
    """Display newsletter completion status with progress bar."""
    completed_sections = [section for section in sections 
                        if section in generated_sections]
    
    completion_percentage = int(len(completed_sections) / len(sections) * 100) if sections else 0
    
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
            is_complete = section in generated_sections
            st.markdown(f"{'✅' if is_complete else '⭕'} {section}")
    
    # Close the div for the progress bar
    st.markdown("</div>", unsafe_allow_html=True)

def section_input_form(section_name, urls_key, notes_key, prompt_key, default_prompt):
    """Render a standard section input form."""
    st.subheader(section_name)
    urls = st.text_input(
        "Enter article URLs (separated by ';;')",
        value=st.session_state.get(urls_key, ""),
        key=urls_key
    )
    notes = st.text_area(
        "Notes",
        value=st.session_state.get(notes_key, ""),
        key=notes_key,
        height=100
    )
    prompt = st.text_area(
        "Section Prompt",
        value=st.session_state.get(prompt_key, default_prompt),
        key=prompt_key,
        height=100
    )
    return urls, notes, prompt

def display_language_indicator():
    """Display the current language selection."""
    selected_language = st.session_state.get("language", "English")
    language_indicator = "🇺🇸 English" if selected_language == "English" else "🇮🇱 עברית"
    st.info(f"Selected Language: {language_indicator}", icon="🌐")