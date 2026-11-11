# lib/role_registry.py - data-driven role catalog (additive layer over persona.py).
import json
from pathlib import Path
from lib import settings, persona, plugin_manager

BASE_ROLES = ["Solver", "Architect", "Crafter", "Analyst", "Communicator", "Sentinel", "Operator"]
ROLES_DIR = Path(__file__).resolve().parent.parent / "roles"

def _load():
    out = {}
    if ROLES_DIR.exists():
        for f in sorted(ROLES_DIR.glob("*.json")):
            if f.name.startswith("_"):
                continue
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                out[d.get("name") or f.stem] = d
            except Exception:
                pass
    return out

def catalog():
    return _load()

def role_names():
    extra = [n for n in _load() if n not in BASE_ROLES]
    return BASE_ROLES + extra

def modules_for(role):
    return (_load().get(role) or {}).get("modules") or []

def system_prompt(agent_id, extra=""):
    cfg = settings.load()
    a = (cfg.get("agents") or {}).get(agent_id) or {}
    role = a.get("role") or "Operator"
    d = _load().get(role)
    if d and d.get("persona"):
        base = d["persona"]
        if extra:
            base = base + "\n" + extra
    else:
        base = persona.system_prompt(agent_id, extra=extra)
    packs = plugin_manager.packs_for(agent_id)
    if packs:
        base = base + "\n\nENABLED SKILL PACKS:\n" + packs
    return base
