import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PERSONAS_DIR = BASE_DIR / os.getenv("PERSONAS_DIR", "agents/personas")
REPORTS_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "memory.sqlite3"

# --- Secrets still from .env (never committed) ---
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Settings layer delegation (S2 milestone) ---
# Try to load from settings.json first; fall back to .env for backward compat.
try:
    from lib import settings as _settings
    _data = _settings.load()
    REPOS = _data.get("repos", [])
    _brains_raw = _data.get("brains", {})
    _settings_loaded = True
except Exception:
    # Fallback to .env (legacy)
    REPOS = [r.strip() for r in os.getenv("REPOS", "").split(",") if r.strip()]
    _brains_raw = {}
    _settings_loaded = False

# --- Provider Hub -----------------------------------------------------
PROVIDERS = {
    "nvidia":     {"base_url": "https://integrate.api.nvidia.com/v1", "key_env": "NVIDIA_API_KEY"},
    "groq":       {"base_url": "https://api.groq.com/openai/v1",      "key_env": "GROQ_API_KEY"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1",        "key_env": "OPENROUTER_API_KEY"},
    "deepseek":   {"base_url": "https://api.deepseek.com/v1",         "key_env": "DEEPSEEK_API_KEY"},
    "mistral":    {"base_url": "https://api.mistral.ai/v1",           "key_env": "MISTRAL_API_KEY"},
}

HOUSE_MODELS = {
    "nvidia": "nvidia/nemotron-3.5-lightning-30b-a3b",
    "groq": "llama-3.1-70b-versatile",
    "openrouter": "deepseek/deepseek-chat",
    "deepseek": "deepseek-chat",
    "mistral": "mistral-large-latest",
}

def _parse_chain(spec):
    """Parse brain chain spec: "provider/model[,provider/model,...]" -> [(prov,model),...]"""
    chain = []
    if not spec:
        return chain
    for part in str(spec).split(","):
        part = part.strip()
        if not part or "/" not in part:
            continue
        prov, model = part.split("/", 1)
        chain.append((prov.strip(), model.strip()))
    return chain

# Build BRAINS dict: from settings.json if available, else from .env fallback
if _settings_loaded and _brains_raw:
    BRAINS = {name: _parse_chain(spec) if isinstance(spec, str) else 
              [(m["provider"], m["model"]) for m in spec] if isinstance(spec, list) and spec and isinstance(spec[0], dict)
              else [("nvidia", HOUSE_MODELS["nvidia"])]
              for name, spec in _brains_raw.items()}
else:
    # Legacy .env fallback
    _legacy = {
        "WORKHORSE":  os.getenv("BRAIN_WORKHORSE")  or os.getenv("BRAIN_PRIMARY"),
        "SPECIALIST": os.getenv("BRAIN_SPECIALIST") or os.getenv("BRAIN_EXPERT"),
        "LIFELINE":   os.getenv("BRAIN_LIFELINE")   or os.getenv("BRAIN_EMERGENCY"),
    }
    BRAINS = {name: (_parse_chain(spec) or [("nvidia", HOUSE_MODELS["nvidia"])])
              for name, spec in _legacy.items()}

# Agent-to-brain mapping (from settings if available, else hardcoded default)
if _settings_loaded and _data.get("agents"):
    AGENT_BRAIN = {aid: a.get("brain", "WORKHORSE") for aid, a in _data["agents"].items()}
else:
    AGENT_BRAIN = {
        "scout": "WORKHORSE", "scribe": "WORKHORSE", "tester": "WORKHORSE",
        "herald": "WORKHORSE", "diplomat": "WORKHORSE", "release": "WORKHORSE",
        "triage": "SPECIALIST", "sentinel": "SPECIALIST", "bridge": "SPECIALIST", "medic": "SPECIALIST",
    }

DEFAULT_BRAIN = "WORKHORSE"

def provider_key(provider: str) -> str:
    return os.getenv(PROVIDERS[provider]["key_env"], "")

def brain_for(agent_id: str) -> str:
    return AGENT_BRAIN.get(agent_id, DEFAULT_BRAIN)