"""
Configuration settings for the Mobileye Newsletter Generator.
"""

# App settings
APP_TITLE = "Mobileye Newsletter Generator"
APP_SUBTITLE = "Generate professional newsletters with AI assistance"
APP_ICON = "🚗"
DEFAULT_THEME = "Light"
DEFAULT_LANGUAGE = "Hebrew"

# Directory settings
DRAFTS_DIR = "drafts"

# AI model settings
DEFAULT_PROVIDER = "OpenAI"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7

# Newsletter settings
DEFAULT_NUM_REARVIEW = 3
MAX_NUM_REARVIEW = 5
MIN_NUM_REARVIEW = 1

# Language settings
SUPPORTED_LANGUAGES = ["English", "Hebrew"]

# Hebrew month names
HEBREW_MONTHS = [
    "ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", 
    "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"
]

# NewsAPI settings
NEWS_DEFAULT_TOPICS = ["AI", "Auto Industry", "Technology"]
NEWS_DEFAULT_TIMEFRAMES = ["Last Week", "Last Month"]