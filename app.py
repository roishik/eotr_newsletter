import streamlit as st
import requests
from bs4 import BeautifulSoup
from llm_service import LLMService
import datetime
import os
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Mobileye Newsletter Generator", layout="wide")

# Initialize LLM service
llm_service = LLMService()

# Create necessary directories
os.makedirs("drafts", exist_ok=True)

# Updated default prompts with explicit instructions for brevity
# Updated default prompts with explicit style instructions for the overall prompt
DEFAULT_PROMPTS = {
    "overall": (
        "What are you doing?:\n"
        "You are writing a section inside an internal Mobileye newsletter on autonomous cars, the car industry, and AI news. "
        "Only write about the relevant content of this section - This text will be a part of the big newsletter (no need for welcome notes). "
        "\nWriting style:\n"
        "Write in a dynamic, conversational, and friendly tone, as if speaking directly to the reader. Keep the language approachable but insightful, "
        "mixing professional analysis with a sense of curiosity and enthusiasm. Use simple, clear sentences, but don't shy away from technical terms when necessary—"
        "just explain them naturally and without overcomplication. Add thoughtful commentary that connects news or updates to broader implications, offering personal insights or lessons. "
        "Maintain an optimistic and forward-thinking voice, encouraging readers to reflect and engage while keeping the overall mood warm and encouraging. "
        "Don't be too optimistic and avoid make announcements that are bigger than the actual news."
        "\nLenght\n"
        "Keep the response concise and focused on the key points."
        "\nWhat to write about?\n"
        "Offer a new lens on the news, providing a fresh perspective or a unique angle that doubts the status quo or offers a new way of thinking."
    ),
    "windshield": (
        "Summarize the articles in 2–3 concise paragraphs focusing on their relevance to Mobileye’s work. "
        "Please be succinct and avoid unnecessary details."
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
    for key, value in draft_data.items():
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

def generate_newsletter_html(sections_content):
    """Creates a clean, modern HTML template for the newsletter."""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mobileye Newsletter</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                background-color: #f4f4f9;
                color: #333;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
                color: #2e6c80;
            }}
            .section {{
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #ddd;
            }}
            .section h2 {{
                color: #2e6c80;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Mobileye Newsletter</h1>
            {sections_content}
        </div>
    </body>
    </html>
    """
    return html_template

# ----------------------------------------------------------------
def main():
    if "generated_sections" not in st.session_state:
        st.session_state.generated_sections = {}

    st.title("Mobileye Newsletter Generator")
    st.markdown("Generate your weekly Mobileye newsletter using a clean, modern interface.")

    # Create two columns: middle for Main Panel (33%), and right for Generated Content (67%%)
    main_panel, right_panel = st.columns([1, 2])

    # Add model selection to the sidebar
    st.sidebar.header("Model Selection")

    # Provider selection
    selected_provider = st.sidebar.selectbox(
        "Select Provider",
        options=llm_service.get_providers(),
        key="selected_provider"
    )

    # Model selection based on provider
    models = llm_service.get_models(selected_provider)
    selected_model = st.sidebar.selectbox(
        "Select Model",
        options=list(models.keys()),
        format_func=lambda x: models[x],
        key="selected_model"
    )

    # API key status indicators
    st.sidebar.markdown("### API Key Status")
    api_status = llm_service.check_api_keys()
    for provider, status in api_status.items():
        st.sidebar.markdown(
            f"{provider} API Key: {'✅' if status else '❌'}"
        )   

    # Add drafts section to sidebar
    st.sidebar.markdown("---")  # Add a separator
    st.sidebar.header("Drafts")
    if st.sidebar.button("Save Draft"):
        save_draft()
                
    draft_files = [f for f in os.listdir("drafts") if f.endswith(".json")]
    draft_files.sort(reverse=True)  # Latest drafts first
    selected_draft = st.sidebar.selectbox(
        "Select a draft to load", 
        options=draft_files
    ) if draft_files else None
    if st.sidebar.button("Load Draft") and selected_draft:
        load_draft(selected_draft)

    with main_panel:
        # --- Begin Main Panel (Inputs) ---
        st.header("Main Panel")
        st.subheader("Overall Prompt")
        overall_prompt = st.text_area(
            "Overall Prompt",
            value=st.session_state.get("overall_prompt", DEFAULT_PROMPTS["overall"]),
            height=150,
            key="overall_prompt"
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
                st.write(generated_text)
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
                    generated_text = generate_section_content(
                        "rearview",
                        article_text,
                        st.session_state[f"rearview_notes_{i}"],
                        st.session_state[f"rearview_prompt_{i}"]
                    )
                    st.success(f"Rearview {i} section generated!")
                    st.write(generated_text)
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
                st.write(generated_text)
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
                st.write(generated_text)
                st.session_state.generated_sections["The Next Lane"] = generated_text

        st.markdown("---")
        # Assemble Newsletter Button using fixed order and placeholders
        if st.button("Create Newsletter"):
            with st.spinner("Assembling Newsletter..."):
                sections_content = ""
                # Fixed order: Windshield, Rearview stories, Dashboard, Next Lane
                sections = []
                sections.append(("Windshield View", st.session_state.generated_sections.get("Windshield View", "Not generated yet.")))
                num_rearview = st.session_state.get("num_rearview", 3)
                for i in range(1, int(num_rearview) + 1):
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
                newsletter_html = generate_newsletter_html(sections_content)
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
        st.markdown("This panel displays the generated sections in fixed order. If a section has not been generated yet, a placeholder is shown.")
        def display_section(title, content):
            st.markdown(f"### {title}")
            st.write(content if content else "Not generated yet.")

        display_section("Windshield View", st.session_state.generated_sections.get("Windshield View", ""))
        num_rearview = st.session_state.get("num_rearview", 3)
        for i in range(1, int(num_rearview) + 1):
            display_section(f"Rearview Mirror {i}", st.session_state.generated_sections.get(f"Rearview Mirror {i}", ""))
        display_section("Dashboard Data", st.session_state.generated_sections.get("Dashboard Data", ""))
        display_section("The Next Lane", st.session_state.generated_sections.get("The Next Lane", ""))

if __name__ == "__main__":
    main()