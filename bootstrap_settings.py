# bootstrap_settings.py - ONE-SHOT INSTALLER. Save as THIS exact name in the
# repo ROOT. Run once. It writes 3 files into the correct folders:
#   docs/SETTINGS-SPEC-v1.1.md , lib/settings.py , settings.json
from pathlib import Path

BASE = Path(__file__).resolve().parent

SPEC = r"""# SETTINGS-SPEC v1.1 - Stratofly Instance Settings Contract

Version: 1.1 | Date: 22 October 2026 | Status: ACTIVE (replaces v1.0)
Owners: Mr Architect & Mr Visioner
Source of truth: this document. Changes MUST bump settings_schema and the
document version together.

## 0. What changed from v1.0 (read first)

v1.0 framed settings as the maintainer app config. v1.1 reframes it as ONE
Stratofly instance - the same engine that will later host custom divisions
and agents (Phase 12-13). Three consequences:
1. agents becomes an explicit registry (id -> behavior), not an implicit
   hardcoded list. Template #1 (the 10-soul maintainer crew) is simply the
   default contents of that registry.
2. Every agent gains division (a light grouping label, NOT a permissioned
   entity) and autonomous (the autonomy switch).
3. Hard/soft limits are first-class: max_per_provider (HARD) and
   max_total_agents (SOFT).

v1.0 remains valid history; v1.1 is what code MUST implement.

## 1. Scope

IN scope v1.1:
- Schema of settings.json (single source of truth for behavior)
- lib/settings.py: load / atomic-save / validate / migrate-from-env
- Limit enforcement helpers (per-provider HARD, total SOFT)
- Migration path from legacy .env brains -> settings.json

OUT of scope v1.1 (later phases, do NOT build now):
- The CLI/Telegram/Godot doors that edit this file (Phase S2-S4)
- Custom agent creation beyond Template #1 (Phase 12)
- Plugin loading (PLUGIN-SPEC) and model recipes (RECIPE-SPEC)
- Web 3D / Hermes-style visuals (separate product, not this repo)

## 2. Single source of truth and secrets rule

File path: BASE_DIR/settings.json
- If missing on first run -> create from defaults and, if legacy BRAIN_*
  keys exist in .env, seed brains from them.
- If malformed JSON -> back up as settings.json.bak.{ts}, regenerate from
  defaults, and surface a polite warning (never crash).
- Unknown fields at any level MUST be preserved on write (round-trip safe).

SECRETS NEVER LIVE HERE. API keys and tokens stay in .env only.
settings.json stores metadata about providers (limits, status), never the
keys themselves.

## 3. The localhost contract (clarification of intent)

Run via localhost means the engine emits a single local server that serves
BOTH the JSON API (already built) AND a lightweight static HTML dashboard
(one file, vanilla CSS/JS, fetch to the same API). It does NOT mean a 3D
scene, sprites, or a Godot/WebGL build - those belong to the commercial app
and a later phase. One truth, three faces: CLI text, JSON API, mini HTML.
The 3D room, when it comes, is face #4 consuming the same API.

## 4. Schema (authoritative, settings_schema: 2)

    {
      "settings_schema": 2,
      "crew_template": "zcp2o-maintainer",
      "repos": ["owner/repo"],
      "brains": {
        "WORKHORSE":  [{"provider": "nvidia", "model": "..."}],
        "SPECIALIST": [{"provider": "nvidia", "model": "..."}],
        "LIFELINE":   [{"provider": "nvidia", "model": "..."}]
      },
      "agents": {
        "<agent_id>": {
          "enabled": true,
          "autonomous": true,
          "brain": "WORKHORSE",
          "cadence_hours": 6,
          "division": "Engineering",
          "template_role": "<agent_id>"
        }
      },
      "limits": { "max_total_agents": 30, "max_per_provider": 10 },
      "notifications": {
        "severity_filter": ["info", "warn", "crit"],
        "quiet_hours_utc": null,
        "telegram_deliver_seconds": 10
      }
    }

Field rules:
- settings_schema : int = 2 ; default if missing: treat as 2, warn ; bump on breaking change
- crew_template : string or null ; default: "zcp2o-maintainer" ; null => fully custom crew (Phase 12)
- repos : string[] ; default: [] ; global watch list
- brains.* : ordered [{provider,model}] ; default: NVIDIA house model ; chain order = priority
- agents.<id>.enabled : bool ; default: true ; off => skipped by scheduler
- agents.<id>.autonomous : bool ; default: true ; the autonomy switch
- agents.<id>.brain : WORKHORSE/SPECIALIST/LIFELINE ; default: WORKHORSE ; which chain it draws from
- agents.<id>.cadence_hours : int >= 1 ; default: 6 ; patrol frequency
- agents.<id>.division : string ; default: "General" ; light label, no permissions
- agents.<id>.template_role : string or null ; default: = id ; maps to code agent (Template #1)
- limits.max_per_provider : int ; default: 10 ; HARD
- limits.max_total_agents : int ; default: 30 ; SOFT
- notifications.* : as v1.0 ; unchanged semantics

## 5. Autonomy switch (safe reinterpretation of take over computer)

autonomous: true => the agent acts on its own schedule and may execute
pre-permitted tasks (repo patrol, sandboxed web research, report writing)
without a manual trigger. autonomous: false => the agent moves only when
explicitly commanded.

There is NO mouse/keyboard/system control in this engine. That capability
is reserved for the commercial mobile app (STRATOFLY-APP v1, Agent Khusus)
with its floating pause button and on-chain audit. In this repo, autonomy
means scheduled, permitted, observable - never unattended system takeover.
This is a deliberate safety boundary, not a missing feature.

## 6. Limit enforcement (HARD vs SOFT)

Counting rule: an agent counts toward a provider when that provider is the
first entry of the agent's resolved brain chain (the brain the user actually
feels serving them).

- HARD, per provider (max_per_provider, default 10): adding an agent whose
  primary provider already serves N>=max agents is REFUSED. Polite message
  (English): "Your <provider> key already serves <N> agents - the free-tier
  safe limit. Add a second key or retire one agent to grow."
- SOFT, total (max_total_agents, default 30): crossing the cap is ALLOWED
  but WARNED once per session. Message: "Heads up: your crew now exceeds
  <max> agents. Stratofly recommends <=<max> per instance to keep every key
  healthy and the room fast."

Template #1 ships exactly 10 agents on one provider, so the HARD cap is
demonstrable on stage: try to add an 11th on the same key and watch the
polite refusal land. That is the feature, proven live.

## 7. Migration from legacy .env brains

On first boot after v1.1 lands, lib/settings.py::migrate_if_missing():
1. If settings.json exists -> do nothing (file wins).
2. Else build defaults; if .env has BRAIN_PRIMARY/EXPERT/EMERGENCY (legacy
   names), map them to WORKHORSE/SPECIALIST/LIFELINE and seed brains;
   populate agents with Template #1.
3. Write settings.json atomically; leave .env secrets untouched.
4. Print: "Migrated brain config -> settings.json (Template #1 seeded)."

Legacy .env brain keys become inert once settings.json exists.

## 8. Template #1 default registry (the 10 souls)

- scout    | Engineering | WORKHORSE  | 6  | scout
- triage   | Engineering | SPECIALIST | 6  | triage
- tester   | Engineering | WORKHORSE  | 6  | tester
- sentinel | Security    | SPECIALIST | 6  | sentinel
- bridge   | Security    | SPECIALIST | 12 | bridge
- scribe   | Content     | WORKHORSE  | 12 | scribe
- medic    | Operations  | SPECIALIST | 12 | medic
- release  | Operations  | WORKHORSE  | 12 | release
- herald   | Community   | WORKHORSE  | 4  | herald
- diplomat | Community   | WORKHORSE  | 4  | diplomat

autonomous defaults true for all ten. LIFELINE is the global safety net (no
agent defaults to it; it is drawn only when WORKHORSE and SPECIALIST chains
are exhausted).

## 9. Constraints (non-negotiable)

- NEVER store secrets in settings.json. Keys live in .env only.
- NEVER strip unknown fields on write.
- NEVER empty a brain chain (last entry removal refused).
- NEVER let a door expose a surface the CLI does not also expose.
- NEVER implement system/mouse/keyboard control here.

## 10. Milestones

- S1 (today): lib/settings.py (load/save/validate/migrate) + example
  settings.json (Template #1). Tested standalone.
- S2 (Fri): config.py delegates brains/agents to settings.py; CLI wizard
  "python main.py settings"; limit enforcement wired.
- S3 (Sat): localhost mini-HTML dashboard + GET/POST /api/settings.
- S4 (Sun): Telegram /settings + autonomy switch surfaces.

## 11. Changelog
- v1.1 (22 Oct 2026): platform-instance framing; explicit agent registry
  with division + autonomy; HARD/SOFT limits; localhost = light HTML (not
  3D); Template #1 default registry; migration path.
- v1.0 (18 Oct 2026): initial schema (history).
"""

SETTINGS_PY = r"""import json, os, time, tempfile
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
"""

SETTINGS_JSON = r"""{
  "settings_schema": 2,
  "crew_template": "zcp2o-maintainer",
  "repos": ["Ringga999/zcp2o-protocol", "Ringga999/notapeer-app"],
  "brains": {
    "WORKHORSE": [
      {"provider": "nvidia", "model": "deepseek-ai/deepseek-coder-6.7b-instruct"},
      {"provider": "nvidia", "model": "nvidia/nemotron-3.5-lightning-30b-a3b"}
    ],
    "SPECIALIST": [
      {"provider": "nvidia", "model": "nvidia/nemotron-3.5-lightning-30b-a3b"}
    ],
    "LIFELINE": [
      {"provider": "nvidia", "model": "nvidia/nemotron-3.5-lightning-30b-a3b"}
    ]
  },
  "agents": {
    "scout":    {"enabled": true, "autonomous": true, "brain": "WORKHORSE",  "cadence_hours": 6,  "division": "Engineering", "template_role": "scout"},
    "triage":   {"enabled": true, "autonomous": true, "brain": "SPECIALIST", "cadence_hours": 6,  "division": "Engineering", "template_role": "triage"},
    "tester":   {"enabled": true, "autonomous": true, "brain": "WORKHORSE",  "cadence_hours": 6,  "division": "Engineering", "template_role": "tester"},
    "sentinel": {"enabled": true, "autonomous": true, "brain": "SPECIALIST", "cadence_hours": 6,  "division": "Security",    "template_role": "sentinel"},
    "bridge":   {"enabled": true, "autonomous": true, "brain": "SPECIALIST", "cadence_hours": 12, "division": "Security",    "template_role": "bridge"},
    "scribe":   {"enabled": true, "autonomous": true, "brain": "WORKHORSE",  "cadence_hours": 12, "division": "Content",     "template_role": "scribe"},
    "medic":    {"enabled": true, "autonomous": true, "brain": "SPECIALIST", "cadence_hours": 12, "division": "Operations",  "template_role": "medic"},
    "release":  {"enabled": true, "autonomous": true, "brain": "WORKHORSE",  "cadence_hours": 12, "division": "Operations",  "template_role": "release"},
    "herald":   {"enabled": true, "autonomous": true, "brain": "WORKHORSE",  "cadence_hours": 4,  "division": "Community",   "template_role": "herald"},
    "diplomat": {"enabled": true, "autonomous": true, "brain": "WORKHORSE",  "cadence_hours": 4,  "division": "Community",   "template_role": "diplomat"}
  },
  "limits": { "max_total_agents": 30, "max_per_provider": 10 },
  "notifications": {
    "severity_filter": ["info", "warn", "crit"],
    "quiet_hours_utc": null,
    "telegram_deliver_seconds": 10
  }
}
"""

(BASE / "docs").mkdir(exist_ok=True)
(BASE / "lib").mkdir(exist_ok=True)
(BASE / "docs" / "SETTINGS-SPEC-v1.1.md").write_text(SPEC, encoding="utf-8")
(BASE / "lib" / "settings.py").write_text(SETTINGS_PY, encoding="utf-8")
(BASE / "settings.json").write_text(SETTINGS_JSON, encoding="utf-8")
print("OK: wrote docs/SETTINGS-SPEC-v1.1.md, lib/settings.py, settings.json")