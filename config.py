"""
Configuration file for the LangGraph Email Parser to User Story Generator
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mistral API Configuration
# Get your API key at: https://console.mistral.ai/
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL: str = "mistral-large-latest"

# Excel Backlog Configuration
BACKLOG_FILE_PATH: str = "data/backlog.xlsx"
BACKLOG_SHEET_NAME: str = "UserStories"

# Document Templates
REQ_DOC_TEMPLATE: str = "templates/req_template.docx"
CR_DOC_TEMPLATE: str = "templates/cr_template.docx"

# Output Directory
OUTPUT_DIR: str = "output"

# Agent Configuration
TEMPERATURE: float = 0.0  # Low temperature for consistent structured output
MAX_TOKENS: int = 4096


def validate_config() -> bool:
    """Validate that required configuration is set"""
    if not MISTRAL_API_KEY:
        print("Error: MISTRAL_API_KEY is not set!")
        print("Please create a .env file with your API key:")
        print("  MISTRAL_API_KEY=your-api-key-here")
        print("Or copy .env.example to .env and add your API key.")
        return False
    return True

