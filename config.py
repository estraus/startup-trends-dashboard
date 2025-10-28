"""Configuration settings for the Startup Trends Dashboard."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional: for higher rate limits
PRODUCTHUNT_TOKEN = os.getenv("PRODUCTHUNT_TOKEN")  # Optional

# Model Configuration
# Using Claude 3 Haiku (fast and efficient model)
CLAUDE_MODEL = "claude-3-haiku-20240307"

# Data Sources
DATA_SOURCE = os.getenv("DATA_SOURCE", "hybrid")  # Options: 'local', 'url', 'sample', 'hybrid'
DATA_SOURCE_URL = os.getenv("DATA_SOURCE_URL", None)  # CSV URL for live data
YC_COMPANIES_URL = "https://ycombinator.com/companies"
SAMPLE_DATA_PATH = "data/sample_startups.csv"

# Example live data sources (uncomment to use):
# DATA_SOURCE = "url"
# DATA_SOURCE_URL = "https://example.com/startup-data.csv"

# Dashboard Configuration
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050
