# lib/plugin_manager.py - plugin catalog + per-agent enablement (data-only MVP).
# Plugins are prompt-packs + repo links. NO third-party code is executed here.
import json
from pathlib import Path
from lib import settings

REG_PATH = Path(__file__).resolve().parent.parent / "plugins" / "registry.json"

def catalog():
    try:
        return json.loads(REG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

def enabled_map():
    return settings.load().get("agent_plugins") or {}

def enabled_for(aid):
    return enabled_map().get(aid) or []

def toggle(aid, pid, on):
    ids = [p.get("id") for p in catalog()]
    if pid not in ids:
        return {"ok": False, "msg": "unknown plugin: " + str(pid)}
    d = settings.load()
    m = d.setdefault("agent_plugins", {})
    cur = list(m.get(aid) or [])
    if on and pid not in cur:
        cur.append(pid)
    if not on and pid in cur:
        cur.remove(pid)
    m[aid] = cur
    settings.save(d)
    return {"ok": True, "agent": aid, "enabled": cur}

def packs_for(aid):
    want = enabled_for(aid)
    if not want:
        return ""
    chunks = []
    for p in catalog():
        if p.get("id") in want and p.get("prompt_pack"):
            chunks.append("- [" + p["id"] + "] " + p["prompt_pack"])
    return "\n".join(chunks)

def status():
    return {"plugins": catalog(), "enabled": enabled_map()}
