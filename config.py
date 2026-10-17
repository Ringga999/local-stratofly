import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PERSONAS_DIR = BASE_DIR / os.getenv("PERSONAS_DIR", "agents/personas")
REPORTS_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "memory.sqlite3"

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
REPOS = [r.strip() for r in os.getenv("REPOS", "").split(",") if r.strip()]
SCOUT_MODEL = os.getenv("SCOUT_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"