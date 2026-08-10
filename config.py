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
MAX_CONTEXT_CHARS = 28000               # ~7K tokens — fits the 12K TPM free tier
LLM_MODEL = "llama-3.3-70b-versatile"   # 131K context window
MAX_REPORT_TOKENS = 2048                # per-section output cap (keeps requests small)

# --- Validation ---
def validate_keys():
    """Check if required API keys are set."""
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    return missing
