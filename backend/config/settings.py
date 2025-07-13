# Application settings and configuration
from typing import List

# FastAPI settings
APP_NAME = "ReadingBooks Backend"
APP_VERSION = "1.0.0"
DEBUG = True

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]

# LLM settings
LLM_BACKEND = "ollama"  # Options: "ollama", "openai", "gemini", etc.
LLM_MODEL = "llama3.1"    # Model name for Ollama

# PDF processing settings
MAX_TEXT_LENGTH = 10000  # Maximum text length to process
TEXT_PREVIEW_LENGTH = 500  # Length of text preview 