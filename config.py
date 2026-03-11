"""
Configuration file for the LangGraph Email Parser to User Story Generator
"""

import os
from typing import Optional

# Mistral API Configuration
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "your-mistral-api-key-here")
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

