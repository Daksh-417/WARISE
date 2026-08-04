import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = Path(os.getenv("WARISE_DB_PATH", str(BASE_DIR / "warise_history.db")))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip() or "llama-3.1-8b-instant"

CACHE_TTL = int(os.getenv("WARISE_CACHE_TTL", "1800"))
RATE_LIMIT_SECONDS = int(os.getenv("WARISE_RATE_LIMIT_SECONDS", "5"))
HISTORY_LIMIT = int(os.getenv("WARISE_HISTORY_LIMIT", "20"))