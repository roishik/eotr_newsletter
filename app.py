import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import datetime
import os
import streamlit.components.v1 as components

# Set up your OpenAI API key (make sure the OPENAI_API_KEY environment variable is set)
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

# Default prompts for each section
DEFAULT_PROMPTS = {
    "overall": (
        "You are writing a section inside an internal Mobileye newsletter on autonomous cars, the car industry, and AI news. "
        "Only write about the relevant content of this section - This text will be a part of the big newsletter (no need for welcome notes). "
        "Write in a dynamic, conversational, and friendly tone, as if speaking directly to the reader. Keep the language approachable but insightful, "
        "mixing professional analysis with a sense of curiosity and enthusiasm. Use simple, clear sentences, but don't shy away from technical terms when necessary—"
        "just explain them naturally and without overcomplication. Add thoughtful commentary that connects news or updates to broader implications, offering personal insights or lessons. "
        "Maintain an optimistic and forward-thinking voice, encouraging readers to reflect and engage while keeping the overall mood warm and encouraging."
    ),
    "windshield": "Summarize the articles in 2-3 paragraphs, focusing on their relevance to Mobileye’s work.",
    "rearview": "Provide a brief headline with a hyperlink followed by 1-3 sentences summarizing the key takeaway.",
    "dashboard": (
        "Write 3 parts:\n"
        "- What's new: Describe key trends or insights.\n"
        "- Why it matters: Explain the impact on Mobileye.\n"
        "- What I think: Share personal opinion."
    ),
    "nextlane": "Summarize competitor/academic news in 2-3 paragraphs, highlighting its implications for Mobileye."
}

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

# Updated generate_section_content function using the correct openai API call
def generate_section_content(section_key, article_text, notes, section_prompt):
    """Generates content using OpenAI's API."""
    user_content = (
        f"{section_prompt}\n\nCombined Article Content:\n{article_text}\n\nNotes: {notes if notes else ''}"
    )
    messages = [
        {"role": "system", "content": DEFAULT_PROMPTS["overall"]},
        {"role": "user", "content": user_content}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        generated_text = response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating content: {e}")
        generated_text = ""
    return generated_text

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

def main():
    st.title("Mobileye Newsletter Generator")
    st.markdown("Generate your weekly Mobileye newsletter using a clean, modern interface.")

    # Overall Prompt Section
    st.subheader("Overall Prompt")
    overall_prompt = st.text_area("Overall Prompt", value=DEFAULT_PROMPTS["overall"], height=150)

    # Dictionary to store generated content for each section
    generated_sections = {}

    # Windshield View Section
    st.subheader("Windshield View")
    windshield_urls = st.text_input("Enter article URLs (separated by ';;')", key="windshield_urls")
    windshield_notes = st.text_area("Notes", key="windshield_notes", height=100)
    windshield_prompt = st.text_area("Section Prompt", value=DEFAULT_PROMPTS["windshield"], key="windshield_prompt", height=100)
    if st.button("Generate Windshield Section"):
        with st.spinner("Generating Windshield section..."):
            article_text = extract_article_text(windshield_urls)
            generated_text = generate_section_content("windshield", article_text, windshield_notes, windshield_prompt)
            st.success("Windshield section generated!")
            st.write(generated_text)
            generated_sections["Windshield View"] = generated_text

    # Rearview Mirror Section (multiple stories)
    st.subheader("Rearview Mirror (Multiple Stories)")
    num_rearview = st.number_input("Number of Rearview Stories", min_value=1, max_value=5, value=3, step=1)
    rearview_generated = {}
    for i in range(1, num_rearview + 1):
        st.markdown(f"**Story {i}**")
        story_urls = st.text_input(f"Story {i} URLs (separated by ';;')", key=f"rearview_urls_{i}")
        story_notes = st.text_area(f"Story {i} Notes", key=f"rearview_notes_{i}", height=80)
        story_prompt = st.text_area(f"Story {i} Prompt", value=DEFAULT_PROMPTS["rearview"], key=f"rearview_prompt_{i}", height=80)
        if st.button(f"Generate Story {i}", key=f"generate_rearview_{i}"):
            with st.spinner(f"Generating Rearview Story {i}..."):
                article_text = extract_article_text(story_urls)
                generated_text = generate_section_content(f"rearview_{i}", article_text, story_notes, story_prompt)
                st.success(f"Story {i} generated!")
                st.write(generated_text)
                rearview_generated[f"Rearview Story {i}"] = generated_text
    generated_sections.update(rearview_generated)

    # Dashboard Data Section
    st.subheader("Dashboard Data")
    dashboard_urls = st.text_input("Enter article URLs (separated by ';;')", key="dashboard_urls")
    dashboard_notes = st.text_area("Notes", key="dashboard_notes", height=100)
    dashboard_prompt = st.text_area("Section Prompt", value=DEFAULT_PROMPTS["dashboard"], key="dashboard_prompt", height=100)
    if st.button("Generate Dashboard Section"):
        with st.spinner("Generating Dashboard section..."):
            article_text = extract_article_text(dashboard_urls)
            generated_text = generate_section_content("dashboard", article_text, dashboard_notes, dashboard_prompt)
            st.success("Dashboard section generated!")
            st.write(generated_text)
            generated_sections["Dashboard Data"] = generated_text

    # The Next Lane Section
    st.subheader("The Next Lane")
    nextlane_urls = st.text_input("Enter article URLs (separated by ';;')", key="nextlane_urls")
    nextlane_notes = st.text_area("Notes", key="nextlane_notes", height=100)
    nextlane_prompt = st.text_area("Section Prompt", value=DEFAULT_PROMPTS["nextlane"], key="nextlane_prompt", height=100)
    if st.button("Generate Next Lane Section"):
        with st.spinner("Generating The Next Lane section..."):
            article_text = extract_article_text(nextlane_urls)
            generated_text = generate_section_content("nextlane", article_text, nextlane_notes, nextlane_prompt)
            st.success("The Next Lane section generated!")
            st.write(generated_text)
            generated_sections["The Next Lane"] = generated_text

    # Assemble Newsletter
    st.markdown("---")
    if st.button("Create Newsletter"):
        with st.spinner("Assembling Newsletter..."):
            sections_content = ""
            for title, content in generated_sections.items():
                sections_content += f"""
                <div class="section">
                    <h2>{title}</h2>
                    <p>{content}</p>
                </div>
                """
            newsletter_html = generate_newsletter_html(sections_content)
            st.success("Newsletter Created!")
            # Render the newsletter using an iframe-like component
            components.html(newsletter_html, height=600, scrolling=True)
            st.download_button(
                "Download Newsletter",
                data=newsletter_html,
                file_name=f"newsletter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )

if __name__ == "__main__":
    main()