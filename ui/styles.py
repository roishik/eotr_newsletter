import streamlit as st
from typing import Dict, Optional

class ThemeManager:
    """Manages custom themes and branding."""
    
    def __init__(self):
        self.themes: Dict[str, Dict] = {
            "Light": {
                "primary_color": "#5F9EA0",
                "secondary_color": "#2e6c80",
                "background_color": "#f8f9fa",
                "text_color": "#333",
                "accent_color": "#7FB3D5",
                "border_color": "#e6e6e6",
                "success_color": "#28a745",
                "warning_color": "#ffc107",
                "error_color": "#dc3545",
                "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            },
            "Dark": {
                "primary_color": "#8ab4f8",
                "secondary_color": "#5F9EA0",
                "background_color": "#2C3333",
                "text_color": "#e8eaed",
                "accent_color": "#7FB3D5",
                "border_color": "#5f6368",
                "success_color": "#28a745",
                "warning_color": "#ffc107",
                "error_color": "#dc3545",
                "font_family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            }
        }
    
    def get_theme(self, theme_name: str) -> Dict:
        """Get theme configuration by name."""
        return self.themes.get(theme_name, self.themes["Light"])
    
    def add_custom_theme(self, name: str, config: Dict) -> None:
        """Add a custom theme configuration."""
        self.themes[name] = config
    
    def update_theme(self, name: str, config: Dict) -> None:
        """Update an existing theme configuration."""
        if name in self.themes:
            self.themes[name].update(config)
    
    def get_css(self, theme_name: str) -> str:
        """Generate CSS for the specified theme."""
        theme = self.get_theme(theme_name)
        
        return f"""
        <style>
        /* Base styles */
        .stApp {{
            background: linear-gradient(to bottom right, {theme['background_color']}, #e9ecef);
            color: {theme['text_color']};
            font-family: {theme['font_family']};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {theme['secondary_color']};
            letter-spacing: 0.5px;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {theme['primary_color']};
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {theme['accent_color']};
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transform: translateY(-1px);
        }}
        
        /* Cards */
        .card {{
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border-left: 4px solid {theme['primary_color']};
        }}
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea {{
            border-color: {theme['border_color']};
            border-radius: 4px;
            padding: 8px;
        }}
        
        /* Success messages */
        .success-message {{
            background-color: {theme['success_color']}20;
            color: {theme['success_color']};
            border-left: 4px solid {theme['success_color']};
            padding: 10px 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        
        /* Warning messages */
        .warning-message {{
            background-color: {theme['warning_color']}20;
            color: {theme['warning_color']};
            border-left: 4px solid {theme['warning_color']};
            padding: 10px 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        
        /* Error messages */
        .error-message {{
            background-color: {theme['error_color']}20;
            color: {theme['error_color']};
            border-left: 4px solid {theme['error_color']};
            padding: 10px 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        </style>
        """

def apply_base_styles():
    """Apply base application styles."""
    theme_manager = ThemeManager()
    st.markdown(theme_manager.get_css("Light"), unsafe_allow_html=True)

def apply_dark_theme():
    """Apply dark theme styles."""
    theme_manager = ThemeManager()
    st.markdown(theme_manager.get_css("Dark"), unsafe_allow_html=True)

def apply_custom_theme(theme_name: str, custom_config: Optional[Dict] = None):
    """Apply a custom theme with optional configuration."""
    theme_manager = ThemeManager()
    if custom_config:
        theme_manager.add_custom_theme(theme_name, custom_config)
    st.markdown(theme_manager.get_css(theme_name), unsafe_allow_html=True)

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
            .section[dir="rtl"] {
                text-align: right;
            }
            .section[dir="rtl"] h2 {
                text-align: right;
            }
            .section[dir="rtl"] p {
                text-align: right;
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
            .section[dir="rtl"] {
                text-align: right;
            }
            .section[dir="rtl"] h2 {
                text-align: right;
            }
            .section[dir="rtl"] p {
                text-align: right;
            }
        </style>
        """