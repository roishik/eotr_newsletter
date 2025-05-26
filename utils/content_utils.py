import requests
from bs4 import BeautifulSoup
import datetime
import streamlit.components.v1 as components
from typing import List, Dict, Tuple
from services.llm_service import LLMService
from ui.components import loading_animation
import pdfkit
import docx
from docx.shared import Inches
import html2text
import json
import yaml
import streamlit as st

def extract_article_text(urls: str) -> str:
    """
    Fetches and combines article content from multiple URLs.
    
    Args:
        urls: String containing URLs separated by ";;"
        
    Returns:
        Combined text from all articles or error message if extraction fails
    """
    print(f"\n[Article Extraction] Starting extraction for URLs: {urls}")
    combined_text = ""
    url_list = [url.strip() for url in urls.split(";;") if url.strip()]
    
    print(f"[Article Extraction] Found {len(url_list)} URLs to process")
    
    if not url_list:
        return ""
    
    # Add headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    failed_urls = []
    for url in url_list:
        try:
            print(f"[Article Extraction] Fetching content from: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"[Article Extraction] Response status code: {response.status_code}")
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try multiple methods to extract content
            article = ""
            
            # Method 1: Look for article content in common containers
            article_containers = soup.find_all(['article', 'main', 'div'], class_=lambda x: x and any(term in str(x).lower() for term in ['article', 'content', 'post', 'entry']))
            if article_containers:
                paragraphs = article_containers[0].find_all(['p', 'div', 'section'])
                article = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            
            # Method 2: If no content found, try all paragraphs
            if not article:
                paragraphs = soup.find_all('p')
                article = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            
            # Method 3: If still no content, try looking for text in any div
            if not article:
                divs = soup.find_all('div')
                article = "\n".join(d.get_text().strip() for d in divs if len(d.get_text().strip()) > 100)
            
            print(f"[Article Extraction] Extracted text length: {len(article)} characters")
            
            if len(article.strip()) == 0:
                failed_urls.append(url)
                continue
                
            combined_text += article + "\n\n"
        except Exception as e:
            error_msg = f"Error fetching URL {url}: {str(e)}"
            print(f"[Article Extraction] {error_msg}")
            failed_urls.append(url)
    
    final_text = combined_text.strip()
    print(f"[Article Extraction] Final combined text length: {len(final_text)} characters")
    
    # If all URLs failed or no content was extracted, return error message
    if len(failed_urls) == len(url_list):
        return f"⚠️ Could not extract content from any of the provided URLs: {', '.join(failed_urls)}"
    elif failed_urls:
        return f"{final_text}\n\n⚠️ Could not extract content from: {', '.join(failed_urls)}"
    
    return final_text

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
    print(f"\n[Content Generation] Starting content generation for section: {section_key}")
    print(f"[Content Generation] Using provider: {provider}, model: {model}")
    print(f"[Content Generation] Article text length: {len(article_text)} characters")
    print(f"[Content Generation] Notes: {notes}")
    print(f"[Content Generation] Section prompt: {section_prompt}")
    
    loading_animation()
    
    user_content = (
        f"{section_prompt}\n\nCombined Article Content:\n{article_text}\n\nNotes: {notes if notes else ''}"
    )
    
    print(f"[Content Generation] Combined prompt length: {len(user_content)} characters")
    
    # Select the appropriate overall prompt based on language
    from config.prompts import DEFAULT_PROMPTS
    
    if language == "Hebrew":
        system_prompt = DEFAULT_PROMPTS["overall_hebrew"]
    else:
        system_prompt = DEFAULT_PROMPTS["overall"]
    
    # Store the full prompt in session state
    if "section_prompts" not in st.session_state:
        st.session_state.section_prompts = {}
    
    st.session_state.section_prompts[section_key] = {
        "system_prompt": system_prompt,
        "user_prompt": user_content,
        "provider": provider,
        "model": model
    }
    
    try:
        print("[Content Generation] Calling LLM service...")
        generated_text = llm_service.generate_content(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_content
        )
        print(f"[Content Generation] Successfully generated content of length: {len(generated_text)} characters")
        return generated_text
    except Exception as e:
        error_msg = f"Error generating content: {str(e)}"
        print(f"[Content Generation] {error_msg}")
        return error_msg

def edit_section_content(
    llm_service: LLMService, 
    section_key: str, 
    original_text: str, 
    edit_prompt: str,
    provider: str = "OpenAI",
    model: str = "gpt-4o",
    # Add new parameters for context
    article_text: str = "",
    notes: str = "",
    section_prompt: str = "",
    overall_prompt: str = ""
) -> str:
    """
    Edits content for a newsletter section using the selected LLM,
    with full context from the original content generation.
    
    Args:
        llm_service: Instance of LLMService
        section_key: Identifier for the section
        original_text: Original section content
        edit_prompt: Instructions for editing
        provider: LLM provider name
        model: Model identifier
        article_text: Combined text from articles used to generate the original content
        notes: Additional notes from the user provided during original generation
        section_prompt: Prompt specific to this section used in original generation
        overall_prompt: Overall newsletter style prompt
        
    Returns:
        Edited content for the section
    """
    loading_animation()
    
    # Build a more comprehensive prompt with all the context
    user_content = (
        f"Please edit the following newsletter section according to these instructions: {edit_prompt}\n\n"
        f"Original Section Content:\n{original_text}\n\n"
    )
    
    # Add context information if available
    if article_text:
        user_content += f"Original Article Content Used:\n{article_text}\n\n"
    
    if notes:
        user_content += f"User's Notes:\n{notes}\n\n"
    
    if section_prompt:
        user_content += f"Section-Specific Guidelines:\n{section_prompt}\n\n"
    
    # Use the provided overall_prompt if available, otherwise use the default
    from config.prompts import DEFAULT_PROMPTS
    system_prompt = overall_prompt if overall_prompt else DEFAULT_PROMPTS["overall"]
    
    try:
        edited_text = llm_service.generate_content(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
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

def export_to_pdf(html_content: str, output_path: str) -> None:
    """Export newsletter to PDF format."""
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    pdfkit.from_string(html_content, output_path, options=options)

def export_to_docx(html_content: str, output_path: str) -> None:
    """Export newsletter to DOCX format."""
    doc = docx.Document()
    
    # Convert HTML to plain text (basic conversion)
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    # Add content to document
    doc.add_paragraph(text)
    
    # Save the document
    doc.save(output_path)

def export_to_markdown(html_content: str, output_path: str) -> None:
    """Export newsletter to Markdown format."""
    # Convert HTML to Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    md_content = h.handle(html_content)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

def export_to_json(newsletter_data: Dict, output_path: str) -> None:
    """Export newsletter to JSON format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(newsletter_data, f, indent=4, ensure_ascii=False)

def export_to_yaml(newsletter_data: Dict, output_path: str) -> None:
    """Export newsletter to YAML format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(newsletter_data, f, allow_unicode=True, sort_keys=False)

def export_newsletter(
    newsletter_html: str,
    newsletter_data: Dict,
    format: str,
    output_path: str
) -> None:
    """
    Export newsletter in the specified format.
    
    Args:
        newsletter_html: HTML content of the newsletter
        newsletter_data: Dictionary containing newsletter data
        format: Export format ('pdf', 'docx', 'md', 'json', 'yaml')
        output_path: Path to save the exported file
    """
    format = format.lower()
    
    if format == 'pdf':
        export_to_pdf(newsletter_html, output_path)
    elif format == 'docx':
        export_to_docx(newsletter_html, output_path)
    elif format == 'md':
        export_to_markdown(newsletter_html, output_path)
    elif format == 'json':
        export_to_json(newsletter_data, output_path)
    elif format == 'yaml':
        export_to_yaml(newsletter_data, output_path)
    else:
        raise ValueError(f"Unsupported export format: {format}")