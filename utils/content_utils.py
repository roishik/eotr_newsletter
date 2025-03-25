import requests
from bs4 import BeautifulSoup
import datetime
import streamlit.components.v1 as components
from typing import List, Dict, Tuple
from services.llm_service import LLMService
from ui.components import loading_animation

def extract_article_text(urls: str) -> str:
    """
    Fetches and combines article content from multiple URLs.
    
    Args:
        urls: String containing URLs separated by ";;"
        
    Returns:
        Combined text from all articles
    """
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
            # Return error message without stopping execution
            combined_text += f"Error fetching URL {url}: {str(e)}\n\n"
    
    return combined_text.strip()

def generate_section_content(
    llm_service: LLMService, 
    section_key: str, 
    article_text: str, 
    notes: str, 
    section_prompt: str,
    provider: str = "OpenAI",
    model: str = "gpt-4o",
    language: str = "English"
) -> str:
    """
    Generates content for a newsletter section using the selected LLM.
    
    Args:
        llm_service: Instance of LLMService
        section_key: Identifier for the section
        article_text: Combined text from articles
        notes: Additional notes from the user
        section_prompt: Prompt specific to this section
        provider: LLM provider name
        model: Model identifier
        language: Target language for generation
        
    Returns:
        Generated content for the section
    """
    loading_animation()
    
    user_content = (
        f"{section_prompt}\n\nCombined Article Content:\n{article_text}\n\nNotes: {notes if notes else ''}"
    )
    
    # Select the appropriate overall prompt based on language
    from config.prompts import DEFAULT_PROMPTS
    
    if language == "Hebrew":
        system_prompt = DEFAULT_PROMPTS["overall_hebrew"]
    else:
        system_prompt = DEFAULT_PROMPTS["overall"]
    
    try:
        generated_text = llm_service.generate_content(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_content
        )
        return generated_text
    except Exception as e:
        return f"Error generating content: {str(e)}"

def edit_section_content(
    llm_service: LLMService, 
    section_key: str, 
    original_text: str, 
    edit_prompt: str,
    provider: str = "OpenAI",
    model: str = "gpt-4o"
) -> str:
    """
    Edits content for a newsletter section using the selected LLM.
    
    Args:
        llm_service: Instance of LLMService
        section_key: Identifier for the section
        original_text: Original section content
        edit_prompt: Instructions for editing
        provider: LLM provider name
        model: Model identifier
        
    Returns:
        Edited content for the section
    """
    loading_animation()
    
    from config.prompts import DEFAULT_PROMPTS
    
    user_content = (
        f"Please edit the following newsletter section according to these instructions: {edit_prompt}\n\n"
        f"Original Section Content:\n{original_text}"
    )
    
    try:
        edited_text = llm_service.generate_content(
            provider=provider,
            model=model,
            system_prompt=DEFAULT_PROMPTS["overall"],
            user_prompt=user_content
        )
        return edited_text
    except Exception as e:
        return f"Error editing content: {str(e)}"

def generate_newsletter_html(
    sections_content: str, 
    theme: str = "light", 
    language: str = "English"
) -> str:
    """
    Generates the complete HTML for the newsletter.
    
    Args:
        sections_content: HTML string containing all newsletter sections
        theme: "light" or "dark"
        language: "English" or "Hebrew"
        
    Returns:
        Complete HTML for the newsletter
    """
    loading_animation()
    
    from ui.styles import get_newsletter_html_style
    
    # Determine text direction based on language
    dir_attr = 'rtl' if language == "Hebrew" else 'ltr'
    lang_attr = 'he' if language == "Hebrew" else 'en'
    
    # Add body direction and language attributes
    body_attrs = f'dir="{dir_attr}" lang="{lang_attr}"'
    
    # Adjust header text based on language
    header_title = "Mobileye Newsletter" if language == "English" else "ניוזלטר מובילאיי"
    header_subtitle = "Insights from the world of autonomous vehicles & AI" if language == "English" else "תובנות מעולם הרכב האוטונומי והבינה המלאכותית"
    
    # Get the appropriate style based on theme
    style = get_newsletter_html_style(theme)
    
    # Footer text based on language
    footer_text = f"© {datetime.datetime.now().year} Mobileye • Generated on {datetime.datetime.now().strftime('%B %d, %Y')}"
    if language == "Hebrew":
        # Format the date in Hebrew style
        today = datetime.datetime.now()
        months_he = ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]
        month_he = months_he[today.month - 1]
        footer_text = f"© {today.year} מובילאיי • נוצר בתאריך {today.day} ב{month_he} {today.year}"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="{lang_attr}">
    <head>
        <meta charset="UTF-8">
        <title>{header_title}</title>
        {style}
    </head>
    <body {body_attrs}>
        <div class="container">
            <div class="header">
                <h1>{header_title}</h1>
                <p>{header_subtitle}</p>
            </div>
            <div class="content">
                {sections_content}
            </div>
            <div class="footer">
                <p>{footer_text}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def render_newsletter_preview(newsletter_html: str, height: int = 600) -> None:
    """
    Renders a preview of the newsletter in the Streamlit app.
    
    Args:
        newsletter_html: Complete HTML for the newsletter
        height: Height of the preview in pixels
    """
    components.html(newsletter_html, height=height, scrolling=True)