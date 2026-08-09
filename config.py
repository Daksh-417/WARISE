"""
config.py
Loads environment variables and stores app-wide settings.
"""

import streamlit as st

# --- API Keys ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")

# --- App Settings ---
MAX_SEARCH_RESULTS = 4          # Number of web sources to fetch
LLM_MODEL = "llama-3.3-70b-versatile"   # Groq model to use

# --- Validation ---
def validate_keys():
    """Check if required API keys are set."""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    return missing
