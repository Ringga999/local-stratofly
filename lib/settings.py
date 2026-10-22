import json, os, time, tempfile
from pathlib import Path
import config

SETTINGS_PATH = config.BASE_DIR / "settings.json"
SCHEMA = 2

TEMPLATE_AGENTS = {
    "scout":    {"division": "Engineering", "brain": "WORKHORSE",  "cadence_hours": 6,  "template_role": "scout"},
    "triage":   {"division": "Engineering", "brain": "SPECIALIST", "cadence_hours": 6,  "template_role": "triage"},
    "tester":   {"division": "Engineering", "brain": "WORKHORSE",  "cadence_hours": 6,  "template_role": "tester"},
    "sentinel": {"division": "Security",    "brain": "SPECIALIST", "cadence_hours": 6,  "template_role": "sentinel"},
    "bridge":   {"division": "Security",    "brain": "SPECIALIST", "cadence_hours": 12, "template_role": "bridge"},
    "scribe":   {"division": "Content",     "brain": "WORKHORSE",  "cadence_hours": 12, "template_role": "scribe"},
    "medic":    {"division": "Operations",  "brain": "SPECIALIST", "cadence_hours": 12, "template_role": "medic"},
    "release":  {"division": "Operations",  "brain": "WORKHORSE",  "cadence_hours": 12, "template_role": "release"},
    "herald":   {"division": "Community",   "brain": "WORKHORSE",  "cadence_hours": 4,  "template_role": "herald"},
    "diplomat": {"division": "Community",   "brain": "WORKHORSE",  "cadence_hours": 4,  "template_role": "diplomat"},
}

def defaults() -> dict:
    house = config.HOUSE_MODELS["nvidia"]
    return {
        "settings_schema": SCHEMA,
        "crew_template": "zcp2o-maintainer",
        "repos": list(config.REPOS),
        "brains": {
            "WORKHORSE":  [{"provider": "nvidia", "model": house}],
            "SPECIALIST": [{"provider": "nvidia", "model": house}],
            "LIFELINE":   [{"provider": "nvidia", "model": house}],
        },
        "agents": {aid: {"enabled": True, "autonomous": True, **meta}
                   for aid, meta in TEMPLATE_AGENTS.items()},
        "limits": {"max_total_agents": 30, "max_per_provider": 10},
        "notifications": {
            "severity_filter": ["info", "warn", "crit"],
            "quiet_hours_utc": None,
            "telegram_deliver_seconds": 10,
        },
    }

def _merge(base: dict, incoming: dict) -> dict:
    # Round-trip safe: keep unknown keys, fill missing from base.
    out = dict(base)
    for k, v in incoming.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out

def load() -> dict:
    if not SETTINGS_PATH.exists():
        return defaults()
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        bak = SETTINGS_PATH.with_suffix(".bak." + str(int(time.time())))
        try:
            bak.write_text(SETTINGS_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass
        return defaults()
    return _merge(defaults(), raw)

def save(data: dict) -> None:
    data.setdefault("settings_schema", SCHEMA)
    fd, tmp = tempfile.mkstemp(dir=str(SETTINGS_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, SETTINGS_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise

def migrate_if_missing() -> bool:
    # Seed settings.json from legacy .env brains if absent. True if created.
    if SETTINGS_PATH.exists():
        return False
    data = defaults()
    legacy = {
        "WORKHORSE":  os.getenv("BRAIN_WORKHORSE")  or os.getenv("BRAIN_PRIMARY"),
        "SPECIALIST": os.getenv("BRAIN_SPECIALIST") or os.getenv("BRAIN_EXPERT"),
        "LIFELINE":   os.getenv("BRAIN_LIFELINE")   or os.getenv("BRAIN_EMERGENCY"),
    }
    for name, spec in legacy.items():
        chain = _parse_env_chain(spec)
        if chain:
            data["brains"][name] = chain
    save(data)
    return True

def _parse_env_chain(spec):
    chain = []
    if not spec:
        return chain
    for part in spec.split(","):
        part = part.strip()
        if not part or "/" not in part:
            continue
        prov, model = part.split("/", 1)
        chain.append({"provider": prov.strip(), "model": model.strip()})
    return chain

# ---- limit helpers (HARD per-provider, SOFT total) -------------------

def _primary_provider(data: dict, agent_id: str):
    a = data["agents"].get(agent_id, {})
    brain = a.get("brain", "WORKHORSE")
    chain = data["brains"].get(brain) or []
    return chain[0]["provider"] if chain else None

def agents_per_provider(data: dict) -> dict:
    counts = {}
    for aid, a in data["agents"].items():
        if not a.get("enabled", True):
            continue
        p = _primary_provider(data, aid)
        if p:
            counts[p] = counts.get(p, 0) + 1
    return counts

def check_per_provider(data: dict, provider: str) -> tuple:
    # HARD. Returns (allowed, reason_en).
    cap = data["limits"]["max_per_provider"]
    n = agents_per_provider(data).get(provider, 0)
    if n >= cap:
        return False, ("Your " + provider + " key already serves " + str(n) +
                       " agents - the free-tier safe limit (" + str(cap) +
                       "). Add a second key or retire one agent to grow.")
    return True, None

def check_total(data: dict) -> tuple:
    # SOFT. Returns (allowed, warning_en). Always allowed.
    cap = data["limits"]["max_total_agents"]
    n = sum(1 for a in data["agents"].values() if a.get("enabled", True))
    if n > cap:
        return True, ("Heads up: your crew now exceeds " + str(cap) +
                      " agents. Stratofly recommends <=" + str(cap) +
                      " per instance to keep every key healthy and the room fast.")
    return True, None
