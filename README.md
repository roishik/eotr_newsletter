# Mobileye Newsletter Generator

An AI-powered application for creating professional, customized newsletters for Mobileye with a focus on autonomous vehicles, automotive industry news, and AI developments.

## Overview

The Mobileye Newsletter Generator is a Streamlit-based application that helps content creators quickly produce well-structured company newsletters. It leverages large language models (LLMs) to generate content based on provided articles, URLs, and user instructions. The application supports multiple content sections, draft saving/loading, an AI-assisted editing mode, and multilingual output.

## Features

### Content Generation
- **Multi-section Newsletter Structure**:
  - Windshield View: Main feature that summarizes recent articles
  - Rearview Mirror: Multiple smaller stories (customizable number)
  - Dashboard Data: Key metrics and trend analysis
  - The Next Lane: Competitor and industry future insights

### AI-Powered Content Creation
- Support for multiple AI providers (OpenAI, Anthropic, Google Gemini)
- Model selection for optimal content quality
- Customizable prompts for each section
- **Multilingual Support**: Generate newsletters in English or Hebrew

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
- Language toggle (English/Hebrew)
- Responsive design
- Draft saving and loading
- Progress tracking for newsletter completion
- One-click HTML newsletter generation

### Advanced Features
- **Keyboard Shortcuts**: Quick access to common actions
- **Drag-and-Drop**: Reorder sections with ease
- **Auto-save**: Automatic saving of drafts to prevent data loss
- **Real-time Collaboration**: Work together with team members
- **Version Control**: Track changes and restore previous versions
- **Analytics**: Monitor newsletter performance and engagement
- **Rich Media Support**: Add images, videos, charts, and interactive content
- **Multiple Export Formats**: Export to HTML, PDF, DOCX, Markdown, JSON, or YAML

## Getting Started

### Prerequisites
- Python 3.7+
- API keys for supported LLM providers (OpenAI, Anthropic, Google Gemini)
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
export GOOGLE_API_KEY="your-google-key"
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
2. **Choose Theme and Language**: Select between Light/Dark themes and English/Hebrew languages.
3. **Fill in Content Sources**:
   - Enter article URLs (separated by `;;`)
   - Add notes to guide the AI
   - Customize section prompts if needed
4. **Generate Sections**: Click the "Generate" button for each section.
5. **Review Content**: Check the generated content in the right panel.
6. **Create Newsletter**: Click "Create Newsletter" to compile all sections.

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

### Collaboration Features

1. **Join a Session**: Enter your name and join the collaboration session.
2. **Real-time Updates**: See other users' activities and changes.
3. **Version Control**: Track changes and restore previous versions if needed.
4. **Auto-save**: Your work is automatically saved at regular intervals.

### Keyboard Shortcuts

- `Ctrl/Cmd + S`: Save draft
- `Ctrl/Cmd + O`: Open draft
- `Ctrl/Cmd + N`: New draft
- `Ctrl/Cmd + G`: Generate section
- `Ctrl/Cmd + E`: Edit section
- `Ctrl/Cmd + P`: Preview newsletter
- `Ctrl/Cmd + D`: Toggle dark mode
- `Ctrl/Cmd + L`: Toggle language
- `Ctrl/Cmd + ?`: Show keyboard shortcuts help

## Language Support

The application supports generating content in both English and Hebrew:

- **Language Selection**: Use the radio button in the sidebar to switch between languages.
- **Right-to-Left Support**: Hebrew content is automatically displayed with RTL text direction.
- **Localized UI Elements**: Headers, footers, and dates are displayed in the selected language.
- **Saved Language Preference**: Your language choice is saved with drafts.

## Saving and Loading Drafts

- **Save Draft**: Click "Save Draft" in the sidebar to store your current work.
- **Load Draft**: Select a previous draft from the dropdown and click "Load Draft".
- **Auto-save**: Drafts are automatically saved at regular intervals.
- **Version History**: Access previous versions of your newsletter.

## Customization

### Default Prompts

You can modify the default prompts in the `DEFAULT_PROMPTS` dictionary in `prompts.py` to better fit your organization's tone and style requirements. Language-specific prompts are available for multilingual support.

### Styling

The application's appearance can be customized by modifying the CSS in the `design/styling.css` file.

## File Structure

```
mobileye-newsletter-generator/
├── app.py                 # Main application file
├── config/               # Configuration files
│   ├── settings.py       # Global app settings
│   └── prompts.py        # Default prompts
├── services/            # Service layer
│   ├── llm_service.py   # LLM provider integration
│   └── news_service.py  # NewsAPI integration
├── ui/                  # UI components
│   ├── components.py    # Reusable UI components
│   ├── styles.py        # CSS styles
│   ├── generate_view.py # Generate content view
│   ├── edit_view.py     # Edit content view
│   └── discovery_view.py # News discovery view
├── utils/              # Utility functions
│   ├── content_utils.py # Content manipulation
│   ├── file_utils.py    # File operations
│   ├── autosave.py      # Auto-save functionality
│   └── collaboration.py # Collaboration features
├── models/             # Data models
│   └── newsletter.py   # Newsletter data structure
├── drafts/            # Saved newsletter drafts
└── requirements.txt   # Dependencies
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