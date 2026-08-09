"""
config.py
Loads API keys from Streamlit secrets and stores app-wide settings.
"""

import streamlit as st

# --- API Keys (from .streamlit/secrets.toml or Streamlit Cloud) ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")

# --- App Settings ---
MAX_SEARCH_RESULTS = 6                  # Number of web sources to fetch
MAX_CONTEXT_CHARS = 80000               # Total char budget for all sources (~20K tokens)
LLM_MODEL = "llama-3.3-70b-versatile"   # 131K context window, 32K max completion
MAX_REPORT_TOKENS = 8192                # Output cap PER SECTION (ceiling never touched)

# --- Validation ---
def validate_keys():
    """Check if required API keys are set."""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    return missing
