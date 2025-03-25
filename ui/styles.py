import streamlit as st

def apply_base_styles():
    """Apply base application styles."""
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

def apply_dark_theme():
    """Apply dark theme styles."""
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

def apply_news_card_styles():
    """Apply styles for news cards in discovery view."""
    is_dark = st.session_state.get("theme", "Light") == "Dark"
    
    st.markdown(f"""
    <style>
    .news-card {'{ background-color: #3c4043; border-left: 4px solid #8ab4f8; }' if is_dark else '{ background-color: white; border-left: 4px solid #5F9EA0; }'}
    .news-card {{
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,{0.2 if is_dark else 0.1});
    }}
    .trending-tag {{
        background-color: #5F9EA0;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        margin-left: 8px;
    }}
    .read-more-btn {{
        background-color: #5F9EA0;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        text-decoration: none;
        font-size: 0.8rem;
        margin-top: 10px;
        display: inline-block;
    }}
    .search-container {'{ background-color: #3c4043; }' if is_dark else '{ background-color: white; }'}
    .search-container {{
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,{0.2 if is_dark else 0.1});
    }}
    </style>
    """, unsafe_allow_html=True)

def get_newsletter_html_style(theme="light"):
    """Get HTML style for newsletter output."""
    if theme.lower() == "dark":
        return """
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
        return """
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