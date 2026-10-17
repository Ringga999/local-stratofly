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

def _parse_chain(spec: str):
    chain = []
    for part in spec.split(","):
        part = part.strip()
        if not part or "/" not in part:
            continue
        prov, model = part.split("/", 1)
        chain.append((prov.strip(), model.strip()))
    return chain

_BRAIN_SPEC = {
    "PRIMARY": os.getenv("BRAIN_PRIMARY", f"nvidia/{HOUSE_MODELS['nvidia']}"),
    "EXPERT": os.getenv("BRAIN_EXPERT", f"nvidia/{HOUSE_MODELS['nvidia']}"),
    "EMERGENCY": os.getenv("BRAIN_EMERGENCY", f"nvidia/{HOUSE_MODELS['nvidia']}"),
}
BRAINS = {name: (_parse_chain(spec) or [("nvidia", HOUSE_MODELS["nvidia"])])
          for name, spec in _BRAIN_SPEC.items()}

AGENT_BRAIN = {
    "scout": "PRIMARY", "scribe": "PRIMARY", "tester": "PRIMARY",
    "herald": "PRIMARY", "diplomat": "PRIMARY", "release": "PRIMARY",
    "triage": "EXPERT", "sentinel": "EXPERT", "bridge": "EXPERT", "medic": "EXPERT",
}
DEFAULT_BRAIN = "PRIMARY"

def provider_key(provider: str) -> str:
    return os.getenv(PROVIDERS[provider]["key_env"], "")

def brain_for(agent_id: str) -> str:
    return AGENT_BRAIN.get(agent_id, DEFAULT_BRAIN)