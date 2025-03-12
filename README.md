# Mobileye Newsletter Generator

An AI-powered application for creating professional, customized newsletters for Mobileye with a focus on autonomous vehicles, automotive industry news, and AI developments.

## Overview

The Mobileye Newsletter Generator is a Streamlit-based application that helps content creators quickly produce well-structured company newsletters. It leverages large language models (LLMs) to generate content based on provided articles, URLs, and user instructions. The application supports multiple content sections, draft saving/loading, and an AI-assisted editing mode.

## Features

### Content Generation
- **Multi-section Newsletter Structure**:
  - Windshield View: Main feature that summarizes recent articles
  - Rearview Mirror: Multiple smaller stories (customizable number)
  - Dashboard Data: Key metrics and trend analysis
  - The Next Lane: Competitor and industry future insights

### AI-Powered Content Creation
- Support for multiple AI providers (OpenAI, Anthropic)
- Model selection for optimal content quality
- Customizable prompts for each section

### Editing Mode
- Three-panel interface for content refinement:
  - Original content review and manual editing
  - AI-assisted editing via custom instructions
  - Preview of edited content before finalizing

### News Discovery
- Integrated news search for finding relevant articles
- Filtering by topic, timeframe, and keywords
- Save interesting articles for later use in newsletters

### User Experience
- Light and dark theme support
- Responsive design
- Draft saving and loading
- Progress tracking for newsletter completion
- One-click HTML newsletter generation

## Getting Started

### Prerequisites
- Python 3.7+
- API keys for supported LLM providers (OpenAI, Anthropic)
- NewsAPI key for the news discovery feature

### Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/mobileye-newsletter-generator.git
cd mobileye-newsletter-generator
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables for API keys:
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export NEWSAPI_API_KEY="your-newsapi-key"
```

### Running the Application

Launch the application with:
```bash
streamlit run app.py
```

The application will be accessible at `http://localhost:8501` in your browser.

## Usage Guide

### Generate Mode

1. **Select Provider and Model**: Choose your preferred AI service and model in the sidebar.
2. **Fill in Content Sources**:
   - Enter article URLs (separated by `;;`)
   - Add notes to guide the AI
   - Customize section prompts if needed
3. **Generate Sections**: Click the "Generate" button for each section.
4. **Review Content**: Check the generated content in the right panel.
5. **Create Newsletter**: Click "Create Newsletter" to compile all sections.

### Edit Mode

1. **Switch to Edit Mode**: Use the sidebar toggle or button in Generate mode.
2. **Select a Section**: Choose which section to edit from the dropdown.
3. **Edit Content**:
   - Directly edit in the left panel
   - OR provide editing instructions in the middle panel and click "Apply AI Edit"
4. **Review and Save**: Check edited content in the right panel and click "Keep this edit" if satisfied.
5. **Generate Final Newsletter**: Compile the final version with all edits.

### Discover News

1. **Select Topic and Timeframe**: Choose a topic category and time range.
2. **Add Keywords**: Refine search with additional terms.
3. **Browse Results**: View and filter search results.
4. **Save Articles**: Mark interesting articles to use in your newsletter.

## Saving and Loading Drafts

- **Save Draft**: Click "Save Draft" in the sidebar to store your current work.
- **Load Draft**: Select a previous draft from the dropdown and click "Load Draft".

## Customization

### Default Prompts

You can modify the default prompts in the `DEFAULT_PROMPTS` dictionary in `app.py` to better fit your organization's tone and style requirements.

### Styling

The application's appearance can be customized by modifying the CSS in the `design/styling.css` file.

## File Structure

```
mobileye-newsletter-generator/
├── app.py                 # Main application file
├── llm_service.py         # LLM provider integration
├── news_service.py        # NewsAPI integration
├── discovery_view.py      # News discovery interface
├── design/
│   └── styling.css        # Custom CSS styles
├── drafts/                # Saved newsletter drafts
└── requirements.txt       # Dependencies
```

## Support and Contribution

For questions, issues, or feature requests, please open an issue on the GitHub repository.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

This means you are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- NonCommercial — You may not use the material for commercial purposes.

For more details about this license, please visit: https://creativecommons.org/licenses/by-nc/4.0/
