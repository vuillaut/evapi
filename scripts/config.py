"""Configuration and constants for EVERSE Unified API."""

import os
from pathlib import Path
from typing import Dict, List

# Source repositories configuration
SOURCES = {
    "indicators": {
        "repo": "https://github.com/EVERSE-ResearchSoftware/indicators",
        "path": "indicators",
        "file_pattern": "*.json",
    },
    "tools": {
        "repo": "https://github.com/EVERSE-ResearchSoftware/TechRadar",
        "path": "data/software-tools",
        "file_pattern": "*.json",
    },
    "dimensions": {
        "repo": "https://github.com/EVERSE-ResearchSoftware/indicators",
        "path": "dimensions",
        "file_pattern": "*.json",
    },
}

# API endpoints
RAW_GITHUB_BASE = "https://raw.githubusercontent.com"
GITHUB_API_BASE = "https://api.github.com"

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
API_DIR = Path(os.path.join(BASE_DIR, "api", "v1"))
CACHE_DIR = Path(os.path.join(BASE_DIR, ".cache"))

# Ensure directories exist
for directory in [DATA_DIR, API_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Create directories if they don't exist
for directory in [DATA_DIR, API_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# API Configuration
API_VERSION = "v1"
API_BASE_URL = os.getenv("API_BASE_URL", "https://vuillaut.github.io/evapi/api/v1")
API_CONTEXT = "https://w3id.org/everse/api/v1/context.jsonld"

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Timeout for HTTP requests (seconds)
HTTP_TIMEOUT = 30

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # Exponential backoff multiplier
