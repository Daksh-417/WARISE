# 🔬 WARISE — Web Augmented Research Intelligence and Synthesis Engine

A beginner-friendly AI research assistant that searches the web,
synthesizes findings, and generates a cited report.

## Quick Start

### 1. Install Dependencies
pip install -r requirements.txt

### 2. Set Up API Keys
cp .env.example .env

Edit `.env` and add:
- `GROQ_API_KEY` → Free at https://console.groq.com
- `TAVILY_API_KEY` → Free at https://tavily.com

### 3. Run
streamlit run app.py

## Project Structure

warise/
├── app.py                  # Main UI
├── config.py               # Settings & env loader
├── services/
│   ├── search_service.py   # Web search (Tavily)
│   └── ai_service.py       # AI synthesis (Groq)
├── utils/
│   └── exporter.py         # Markdown export
├── requirements.txt
├── .env.example
└── README.md

## How It Works

User Input (app.py)
       │
       ▼
search_service.py ──→ Tavily API ──→ Returns URLs + clean text
       │
       ▼
ai_service.py ──→ Groq API (Llama 3) ──→ Structured report
       │
       ▼
exporter.py ──→ Markdown file download

1. User enters a research question
2. Tavily searches the web and returns clean snippets
3. Groq (Llama 3) synthesizes a structured, cited report
4. User downloads the report as Markdown