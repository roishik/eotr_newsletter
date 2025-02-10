#!/Users/roishi/miniconda3/envs/ eotr_newsletter

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import openai
import os
import datetime
import json

app = Flask(__name__)

# Folder setup
SECTIONS_DIR = "sections"
FINAL_NEWSLETTERS_DIR = "newsletters"
os.makedirs(SECTIONS_DIR, exist_ok=True)
os.makedirs(FINAL_NEWSLETTERS_DIR, exist_ok=True)

# OpenAI setup
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_PROMPTS = {
    "overall": "You are writing an internal Mobileye newsletter on autonomous cars, the car industry, and AI news. Write in a dynamic, conversational, and friendly tone, as if speaking directly to the reader. Keep the language approachable but insightful, mixing professional analysis with a sense of curiosity and enthusiasm. Use simple, clear sentences, but don't shy away from technical terms when necessary—just explain them naturally and without overcomplication. Add thoughtful commentary that connects news or updates to broader implications, offering personal insights or lessons. Maintain an optimistic and forward-thinking voice, encouraging readers to reflect and engage while keeping the overall mood warm and encouraging.",
    "windshield": "Summarize the articles in 2-3 paragraphs, focusing on their relevance to Mobileye’s work.",
    "rearview": "Provide a brief headline with a hyperlink followed by 1-3 sentences summarizing the key takeaway.",
    "dashboard": "Write 3 parts:\n- What's new: Describe key trends or insights.\n- Why it matters: Explain the impact on Mobileye.\n- What I think: Share personal opinion.",
    "nextlane": "Summarize competitor/academic news in 2-3 paragraphs, highlighting its implications for Mobileye."
}

FINAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobileye Newsletter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2 { color: #2e6c80; }
        .section { border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Mobileye Newsletter</h1>
    <p>Welcome to this week’s issue of Mobileye’s internal newsletter. Below are the latest insights, news, and developments.</p>
    
    {content}
</body>
</html>
"""

def extract_article_text(urls):
    """Fetch and combine article text from multiple URLs."""
    combined_text = ""
    # Split the URLs properly and trim any whitespace
    url_list = [url.strip() for url in urls.split(";;") if url.strip()]
    
    for url in url_list:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (e.g., 404)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all('p')
            combined_text += "\n".join(p.get_text() for p in paragraphs) + "\n\n"
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
    
    return combined_text.strip()


def generate_section_content(section_key, article_text, notes):
    """Generate content using OpenAI."""
    user_content = f"{DEFAULT_PROMPTS[section_key]}\n\nCombined Article Content:\n{article_text}\n\nNotes: {notes if notes else ''}"
    messages = [{"role": "system", "content": DEFAULT_PROMPTS["overall"]}, {"role": "user", "content": user_content}]

    response = client.chat.completions.create(
        model="gpt-4", messages=messages, temperature=0.7, max_tokens=500
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", defaultPrompts=DEFAULT_PROMPTS)

@app.route("/generate_section", methods=["POST"])
def generate_section():
    section_key = request.form.get("section_key")
    article_urls = request.form.get("article_urls")
    notes = request.form.get("notes")

    article_text = extract_article_text(article_urls)
    output = generate_section_content(section_key, article_text, notes)

    section_data = {"article_urls": article_urls, "notes": notes, "output": output}
    with open(f"{SECTIONS_DIR}/{section_key}.json", "w") as f:
        json.dump(section_data, f)

    return jsonify({"output": output})

@app.route("/create_newsletter", methods=["POST"])
def create_newsletter():
    sections = ["windshield", "rearview", "dashboard", "nextlane"]
    formatted_content = ""

    for section in sections:
        with open(f"{SECTIONS_DIR}/{section}.json") as f:
            data = json.load(f)
            formatted_content += f"""
            <div class="section">
                <h2>{section.capitalize()} Section</h2>
                <p>{data['output']}</p>
            </div>
            """

    final_output = FINAL_TEMPLATE.format(content=formatted_content)
    filename = f"newsletter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(FINAL_NEWSLETTERS_DIR, filename)
    
    with open(filepath, "w") as f:
        f.write(final_output)

    return jsonify({"message": "Newsletter created", "filename": filename, "content": final_output})

if __name__ == "__main__":
    app.run(debug=True)
