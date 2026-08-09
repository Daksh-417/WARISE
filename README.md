# 🔬 WARISE — Web Augmented Research Intelligence and Synthesis Engine

A modular AI research assistant that searches the web, synthesizes
findings section-by-section, and exports a long-form cited report.

## Quick Start

### 1. Install Dependencies
pip install -r requirements.txt

### 2. Set Up API Keys
mkdir .streamlit
# Create .streamlit/secrets.toml:
# GROQ_API_KEY = "..."   → Free at https://console.groq.com
# TAVILY_API_KEY = "..." → Free at https://tavily.com

### 3. Run
streamlit run app.py

## Architecture

User Input (app.py)
       │
       ▼
search_service.py → Tavily (advanced) → clean snippets + smart context budget
       │
       ▼
ai_service.py → Groq Llama 3.3 70B → section-wise streamed synthesis
       │
       ▼
exporter.py → Markdown download with references

## Engineering Decisions

- **st.secrets** over .env → Streamlit-native, deployment-safe key handling.
- **Tavily advanced search** → clean, noise-free content (no HTML scraping).
- **Smart context budget (80K chars ≈ 20K tokens)** → stays safely inside
  the 131,072-token window while maximizing source depth.
- **Section-wise generation** → each call stays under the 8,192-token output
  cap; combined report scales with section count, not the model ceiling.
