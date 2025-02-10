#!exi /Users/roishi/miniconda3/envs/eotr_newsletter

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import openai
import os
import datetime

app = Flask(__name__)

# Set your OpenAI API key in an environment variable (e.g., OPENAI_API_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Section-specific prompts
DEFAULT_PROMPTS = {
    "overall": "You are writing an internal Mobileye newsletter on autonomous cars, the car industry, and AI news. The tone is professional and insightful, and the audience is Mobileye employees. Maintain consistency with previous issues.",
    "windshield": "Summarize the article in 2-3 paragraphs, focusing on its key message and its relevance to Mobileye’s work. The tone should be engaging and thought-provoking.",
    "rearview": "Provide a brief headline with a hyperlink followed by 1-3 sentences summarizing the key takeaway from the story.",
    "dashboard": "Write 3 parts:\n- What's new: Describe key trends or insights from the graph or data.\n- Why it matters: Explain the impact of this data on the automotive or AI landscape.\n- What I think: Share your perspective on how Mobileye can act on or respond to this information.",
    "nextlane": "Summarize the competitor’s or academic’s new development in 2-3 paragraphs. Highlight its implications for Mobileye’s current or future strategies and innovation efforts."
}

def extract_article_text(url):
    """Fetch and extract article text from a given URL using BeautifulSoup."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all('p')
        text = "\n".join(p.get_text() for p in paragraphs)
        return text
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

def generate_section_content(section_key, article_text, notes, overall_prompt):
    """Generate content for one newsletter section using the ChatGPT API."""
    # Build the prompt: overall prompt + default section prompt + article content + notes (if any)
    prompt = f"{overall_prompt}\n\n{DEFAULT_PROMPTS[section_key]}\n\nArticle Content:\n{article_text}"
    if notes:
        prompt += f"\n\nNotes: {notes}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300  # Adjust if you need longer responses
    )
    return response.choices[0].message['content'].strip()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", defaultPrompts=DEFAULT_PROMPTS)

@app.route("/generate", methods=["POST"])
def generate_newsletter():
    overall_prompt = request.form.get("overall_prompt", DEFAULT_PROMPTS["overall"])

    # Process Windshield View
    windshield_url = request.form.get("windshield_url")
    windshield_notes = request.form.get("windshield_notes")
    windshield_text = extract_article_text(windshield_url) if windshield_url else ""
    windshield_output = ""
    if windshield_url:
        windshield_output = generate_section_content("windshield", windshield_text, windshield_notes, overall_prompt)

    # Process Rearview Mirror: Allow up to 5 stories
    rearview_outputs = []
    for i in range(1, 6):
        story_url = request.form.get(f"rearview_url_{i}")
        story_notes = request.form.get(f"rearview_notes_{i}")
        if story_url:
            story_text = extract_article_text(story_url)
            output = generate_section_content("rearview", story_text, story_notes, overall_prompt)
            # Format as a headline with a hyperlink followed by the generated summary.
            headline = f'<a href="{story_url}" target="_blank">{story_url}</a>'
            rearview_outputs.append(f"{headline}<br>{output}")
    rearview_output = "\n\n".join(rearview_outputs)

    # Process Dashboard Data
    dashboard_graph_url = request.form.get("dashboard_graph_url")
    dashboard_notes_new = request.form.get("dashboard_notes_new")
    dashboard_notes_matter = request.form.get("dashboard_notes_matter")
    dashboard_notes_think = request.form.get("dashboard_notes_think")
    # Combine the notes for the three parts
    dashboard_combined_notes = (
        f"Notes for What's new: {dashboard_notes_new}\n"
        f"Notes for Why it matters: {dashboard_notes_matter}\n"
        f"Notes for What I think: {dashboard_notes_think}"
    )
    # Include the graph URL in the article text for context
    dashboard_text = f"Graph/Image URL: {dashboard_graph_url}" if dashboard_graph_url else ""
    dashboard_output = ""
    if dashboard_graph_url or dashboard_combined_notes:
        dashboard_output = generate_section_content("dashboard", dashboard_text, dashboard_combined_notes, overall_prompt)

    # Process The Next Lane
    nextlane_url = request.form.get("nextlane_url")
    nextlane_notes = request.form.get("nextlane_notes")
    nextlane_text = extract_article_text(nextlane_url) if nextlane_url else ""
    nextlane_output = ""
    if nextlane_url:
        nextlane_output = generate_section_content("nextlane", nextlane_text, nextlane_notes, overall_prompt)

    # Assemble final newsletter text (each section separated by dividers)
    newsletter = (
        f"---\nWIND SHIELD VIEW\n\n{windshield_output}\n\n"
        f"---\nREARVIEW MIRROR\n\n{rearview_output}\n\n"
        f"---\nDASHBOARD DATA\n\n{dashboard_output}\n\n"
        f"---\nTHE NEXT LANE\n\n{nextlane_output}\n---"
    )

    return render_template("result.html", newsletter=newsletter)

@app.route("/save_draft", methods=["POST"])
def save_draft():
    """Save the final newsletter text to a local file in a 'drafts' folder."""
    newsletter_text = request.form.get("newsletter_text")
    if newsletter_text:
        drafts_dir = "drafts"
        os.makedirs(drafts_dir, exist_ok=True)
        filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_newsletter.txt")
        filepath = os.path.join(drafts_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(newsletter_text)
        return jsonify({"status": "success", "message": f"Draft saved as {filename}"})
    return jsonify({"status": "error", "message": "No newsletter text provided"}), 400

if __name__ == "__main__":
    app.run(debug=True)
