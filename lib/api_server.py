# lib/api_server.py v2 - Stratofly control-room server (Phase 1).
# Fixes: bubble state shows real idle/ready (not "not implemented yet").
# Adds: /api/agent/<id> endpoint for detail modal.
# Adds: Free APIs menu data via /api/free-apis.
# Still serves lib/app.html at /. ThreadingHTTPServer.
import json, os, sys, time, threading, hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from lib import memory, settings, model_kind, ask_handler, scheduler, mock
from lib import onboard, persona
from config import REPORTS_DIR

HERE = Path(__file__).resolve().parent
APP_HTML = HERE / "app.html"
DEFAULT_PORT = 8765
BRAIN_NAMES = ["WORKHORSE", "SPECIALIST", "LIFELINE"]
ROLE_NAMES = ["Solver", "Architect", "Crafter", "Analyst", "Communicator", "Sentinel", "Operator"]
ALLOWED_AGENT = {"enabled", "autonomous", "cadence_hours", "brain", "division", "role"}

_MOCK_STOP = threading.Event()
_MOCK_STOP.set()
_MOCK_THREAD = None
_PATROL_LOCK = threading.Lock()

FREE_APIS = [
    {"name": "NVIDIA NIM", "url": "https://build.nvidia.com/settings/api-keys",
     "desc": "Free serverless APIs for development (default brain provider)"},
    {"name": "Groq", "url": "https://console.groq.com/keys",
     "desc": "Fast inference, free tier available"},
    {"name": "OpenRouter", "url": "https://openrouter.ai/keys",
     "desc": "Unified API for many models, free models available"},
    {"name": "DeepSeek", "url": "https://platform.deepseek.com/api_keys",
     "desc": "Strong coding models, free tier"},
    {"name": "Mistral", "url": "https://console.mistral.ai/api-keys/",
     "desc": "European LLM provider, free tier"},
    {"name": "GitHub (tokenless)", "url": "https://github.com/settings/tokens",
     "desc": "Public repos readable without token; private needs token"},
]

def _page():
    return APP_HTML.read_text(encoding="utf-8")

def _env_status():
    d = onboard._read_env()
    return {"nvidia": bool(d.get("NVIDIA_API_KEY")), "github": bool(d.get("GITHUB_TOKEN"))}

def _state():
    cfg = settings.load()
    live = {}
    try:
        for e in memory.get_all_agent_states():
            live[e.get("agent")] = e
    except Exception:
        live = {}
    agents = []
    for aid, a in (cfg.get("agents") or {}).items():
        lv = live.get(aid, {})
        state = lv.get("state") or "idle"
        bubble = lv.get("bubble") or ""
        # Filter useless bubbles from old mock/patrol runs
        useless = ["not implemented", "waiting..."]
        if state == "idle" and (not bubble or any(u in bubble.lower() for u in useless)):
            bubble = "ready - waiting for task"
        elif not bubble:
            bubble = state
        agents.append({
            "id": aid,
            "division": a.get("division", "General"),
            "role": a.get("role", "Operator"),
            "brain": a.get("brain", "WORKHORSE"),
            "cadence_hours": a.get("cadence_hours", 6),
            "autonomous": bool(a.get("autonomous", True)),
            "enabled": bool(a.get("enabled", True)),
            "state": state,
            "action": lv.get("action", "-"),
            "target": lv.get("target", "-"),
            "bubble": bubble,
            "since_ts": lv.get("since_ts", 0),
        })
    per = settings.agents_per_provider(cfg)
    caps = cfg.get("limits", {})
    total = sum(1 for a in (cfg.get("agents") or {}).values() if a.get("enabled", True))
    return {"schema": 2, "online": True, "ts": time.time(), "agents": agents,
            "per_provider": per, "max_per_provider": caps.get("max_per_provider", 10),
            "max_total": caps.get("max_total_agents", 30)}

def _agent_detail(aid):
    cfg = settings.load()
    agents = cfg.get("agents") or {}
    if aid not in agents:
        return None
    a = agents[aid]
    live = {}
    try:
        for e in memory.get_all_agent_states():
            if e.get("agent") == aid:
                live = e; break
    except Exception:
        pass
    events = []
    try:
        events = memory.recent_events(10)
        events = [e for e in events if e.get("agent") == aid]
    except Exception:
        pass
    brain_chain = cfg.get("brains", {}).get(a.get("brain", "WORKHORSE"), [])
    brain_detail = []
    for entry in brain_chain:
        m = entry.get("model", "")
        brain_detail.append({
            "provider": entry.get("provider"),
            "model": m,
            "kind": model_kind.classify(m),
            "badge": model_kind.badge(m),
        })
    role = a.get("role", "Operator")
    role_modules = {
        "Solver": ["upload", "delegation", "simulation", "draft_queue"],
        "Architect": ["audit_viewer", "dependency_graph", "redesign_editor"],
        "Crafter": ["spec_input", "code_diff", "test_runner", "pr_creator"],
        "Analyst": ["research_input", "source_list", "trend_chart", "report_gen"],
        "Communicator": ["platform_selector", "tone_selector", "draft_composer", "approval_queue", "mention_monitor"],
        "Sentinel": ["scope_selector", "cve_dashboard", "breaking_flags", "compliance_checklist"],
        "Operator": ["routine_list", "handoff_timeline", "pipeline_health", "ops_summary", "alert_log"],
    }
    return {
        "id": aid, "division": a.get("division", "General"),
        "role": role, "brain": a.get("brain", "WORKHORSE"),
        "brain_chain": brain_detail,
        "cadence_hours": a.get("cadence_hours", 6),
        "autonomous": bool(a.get("autonomous", True)),
        "enabled": bool(a.get("enabled", True)),
        "state": live.get("state", "idle"),
        "bubble": live.get("bubble") or "ready - waiting for task",
        "action": live.get("action", "-"),
        "recent_events": events[:5],
        "modules": role_modules.get(role, []),
        "template_role": a.get("template_role", aid),
    }

def _apply_patch(patch):
    d = settings.load()
    changed = []
    if "repos" in patch and isinstance(patch["repos"], list):
        d["repos"] = [r for r in patch["repos"] if isinstance(r, str) and "/" in r]
        changed.append("repos")
    if "limits" in patch and isinstance(patch["limits"], dict):
        for k in ("max_total_agents", "max_per_provider"):
            v = patch["limits"].get(k)
            if isinstance(v, int) and v >= 1:
                d["limits"][k] = v
                changed.append("limits." + k)
    if "agents" in patch and isinstance(patch["agents"], dict):
        for aid, fields in patch["agents"].items():
            if aid not in d.get("agents", {}) or not isinstance(fields, dict):
                continue
            for f, v in fields.items():
                if f not in ALLOWED_AGENT:
                    continue
                if f == "cadence_hours" and not (isinstance(v, int) and 1 <= v <= 168):
                    continue
                if f == "brain" and v not in BRAIN_NAMES:
                    continue
                if f == "role" and v not in ROLE_NAMES:
                    continue
                if f in ("enabled", "autonomous") and not isinstance(v, bool):
                    continue
                if f == "division" and not isinstance(v, str):
                    continue
                d["agents"][aid][f] = v
                changed.append("agents." + aid + "." + f)
    if changed:
        settings.save(d)
    return changed

def _add_agent(body):
    d = settings.load()
    aid = (body.get("id") or "").strip()
    if not aid or not all(c.isalnum() or c in "_-" for c in aid):
        return {"ok": False, "msg": "invalid id (a-z0-9_-)"}
    if aid in d.get("agents", {}):
        return {"ok": False, "msg": "id already exists"}
    role = body.get("role") if body.get("role") in ROLE_NAMES else "Operator"
    brain = body.get("brain") if body.get("brain") in BRAIN_NAMES else "WORKHORSE"
    cad = body.get("cadence_hours")
    cad = cad if isinstance(cad, int) and 1 <= cad <= 168 else 6
    chain = d.get("brains", {}).get(brain, [])
    prov = chain[0].get("provider", "nvidia") if chain else "nvidia"
    allowed, reason = settings.check_per_provider(d, prov)
    if not allowed:
        return {"ok": False, "msg": "REFUSED (HARD limit): " + reason}
    d.setdefault("agents", {})[aid] = {
        "enabled": True, "autonomous": bool(body.get("autonomous", True)),
        "brain": brain, "role": role, "cadence_hours": cad,
        "division": (body.get("division") or "General"), "template_role": aid,
    }
    settings.save(d)
    _, warn = settings.check_total(d)
    msg = "+ agent '" + aid + "' as " + role + " on " + prov + "/" + brain
    if warn:
        msg += "  |  NOTE (SOFT): " + warn
    return {"ok": True, "msg": msg}

def _remove_agent(body):
    d = settings.load()
    aid = (body.get("id") or "").strip()
    if aid in d.get("agents", {}):
        del d["agents"][aid]
        settings.save(d)
        return {"ok": True, "msg": "removed " + aid}
    return {"ok": False, "msg": "no such agent"}

def _onboard(body):
    key = (body.get("key") or "").strip()
    if not key:
        return {"ok": False, "msg": "empty key"}
    d = onboard._read_env()
    d["NVIDIA_API_KEY"] = key
    onboard._write_env(d)
    return {"ok": True, "msg": "NVIDIA key saved to .env"}

def _ask(body):
    prompt = (body.get("prompt") or "").strip()
    agent = (body.get("agent_id") or "scout").strip()
    if not prompt:
        return {"ok": False, "answer": "", "error": "empty prompt"}
    try:
        ans = ask_handler.ask(prompt, agent_id=agent)
        return {"ok": True, "answer": ans}
    except Exception as e:
        return {"ok": False, "answer": "", "error": str(e)}

def _patrol_async():
    if not _PATROL_LOCK.acquire(blocking=False):
        return {"ok": False, "msg": "patrol already running"}
    def _job():
        try:
            scheduler.run_once()
        except Exception:
            pass
        finally:
            _PATROL_LOCK.release()
    threading.Thread(target=_job, daemon=True).start()
    return {"ok": True, "msg": "patrol dispatched in background"}

def _mock_loop():
    import random
    agents = list(mock.MOCK_AGENTS.keys())
    states = mock.STATES
    while not _MOCK_STOP.is_set():
        aid = random.choice(agents)
        st = random.choice(states)
        ac = random.choice(mock.MOCK_AGENTS[aid]["actions"])
        bub = mock.MOCK_AGENTS[aid]["emoji"] + " " + aid + " is " + ac + "..."
        try:
            memory.update_agent_state(aid, st, ac, "-", bub, -1)
            memory.log_event(aid, st, ac, "-", bub, -1)
        except Exception:
            pass
        _MOCK_STOP.wait(3)

def _mock_start():
    global _MOCK_THREAD
    if not _MOCK_STOP.is_set():
        return {"ok": False, "msg": "mock already running"}
    _MOCK_STOP.clear()
    _MOCK_THREAD = threading.Thread(target=_mock_loop, daemon=True)
    _MOCK_THREAD.start()
    return {"ok": True, "msg": "mock running (offline demo mode)"}

def _mock_stop():
    _MOCK_STOP.set()
    return {"ok": True, "msg": "mock stopped"}


def _solve(body):
    prompt = (body.get("prompt") or "").strip()
    agent = (body.get("agent_id") or "scout").strip()
    if not prompt:
        return {"ok": False, "answer": "", "error": "empty prompt"}
    try:
        # Import persona module to get SOLVER_PERSONA
        from lib import persona
        system_prompt = getattr(persona, "SOLVER_PERSONA", None)
        # Call provider_hub.think with Solver persona
        from lib import provider_hub
        # Get agent brain chain
        cfg = settings.load()
        agent_cfg = (cfg.get("agents") or {}).get(agent, {})
        brain = agent_cfg.get("brain", "WORKHORSE")
        response = provider_hub.think(
            brain=brain,
            system=system_prompt or "",
            user=prompt,
            agent_id=agent,
            temperature=0.7,
            max_tokens=2048
        )
        return {"ok": True, "answer": response}
    except Exception as e:
        return {"ok": False, "answer": "", "error": str(e)}


def _solve_plan(body):
    prompt = (body.get("prompt") or "").strip()
    agent = (body.get("agent_id") or "scout").strip()
    if not prompt:
        return {"ok": False, "answer": "", "delegations": [], "error": "empty prompt"}
    try:
        from lib import provider_hub
        cfg = settings.load()
        agents = cfg.get("agents") or {}
        agent_cfg = agents.get(agent, {})
        brain = agent_cfg.get("brain", "WORKHORSE")
        crew = "\n".join(("- " + aid + " (role: " + (a.get("role") or "Operator") + ")") for aid, a in agents.items())
        sys_prompt = (getattr(persona, "SOLVER_PERSONA", "") or "") + (
            "\n\nAVAILABLE CREW - you may delegate ONLY to these exact ids:\n" + crew +
            "\n\nAfter your narrative plan, append 0-4 delegation lines, each EXACTLY:"
            "\n[DELEGATE: <agent_id> | <short concrete sub-task for that agent>]"
            "\nUse only ids from the list above. If the work is single-step, output zero DELEGATE lines."
        )
        raw = provider_hub.think(brain=brain, system=sys_prompt, user=prompt, agent_id=agent, temperature=0.6, max_tokens=2048)
        dels = []
        for m in re.findall(r"\[DELEGATE:\s*([^\|\]]+)\|([^\]]+)\]", raw or ""):
            tid = m[0].strip(); tsk = m[1].strip()
            dels.append({"agent": tid, "task": tsk, "valid": tid in agents})
        return {"ok": True, "answer": raw or "", "delegations": dels}
    except Exception as e:
        return {"ok": False, "answer": "", "delegations": [], "error": str(e)}

def _delegate(body):
    to_agent = (body.get("to_agent") or "").strip()
    task = (body.get("task") or "").strip()
    frm = (body.get("from_solver") or "solver").strip()
    if not to_agent or not task:
        return {"ok": False, "answer": "", "error": "missing to_agent or task"}
    try:
        from lib import provider_hub
        cfg = settings.load()
        agents = cfg.get("agents") or {}
        if to_agent not in agents:
            return {"ok": False, "answer": "", "error": "unknown agent: " + to_agent}
        brain = agents[to_agent].get("brain", "WORKHORSE")
        sys_p = persona.system_prompt(to_agent, extra="")
        ans = provider_hub.think(brain=brain, system=sys_p, user=task, agent_id=to_agent, temperature=0.6, max_tokens=1024)
        try:
            memory.log_event(frm, "delegate", "dispatch", to_agent, "delegated: " + task[:48], -1)
            memory.log_event(to_agent, "working", "sub_task", frm, "executing for " + frm + ": " + task[:40], -1)
        except Exception:
            pass
        return {"ok": True, "answer": ans or "", "agent": to_agent}
    except Exception as e:
        return {"ok": False, "answer": "", "error": str(e)}

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def _read_body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n).decode("utf-8") if n else "{}"
        try:
            return json.loads(raw)
        except Exception:
            return {}
    def do_GET(self):
        try:
            p = self.path
            if p == "/" or p.startswith("/index") or p.startswith("/app"):
                self._send_html(_page())
            elif p == "/api/state":
                self._send_json(_state())
            elif p == "/api/settings":
                self._send_json(settings.load())
            elif p == "/api/env-status":
                self._send_json(_env_status())
            elif p == "/api/free-apis":
                self._send_json({"apis": FREE_APIS})
            elif p.startswith("/api/agent/"):
                aid = p.split("/api/agent/")[1].split("?")[0]
                detail = _agent_detail(aid)
                if detail:
                    self._send_json(detail)
                else:
                    self._send_json({"error": "agent not found"}, 404)
            elif p.startswith("/api/activity"):
                limit = 50
                if "limit=" in p:
                    try:
                        limit = int(p.split("limit=")[1].split("&")[0])
                    except Exception:
                        pass
                self._send_json({"schema": 2, "events": memory.recent_events(limit)})
            elif p.startswith("/api/report/"):
                try:
                    rid = int(p.split("/api/report/")[1])
                    f = REPORTS_DIR / ("report_" + str(rid) + ".md")
                    if f.exists():
                        self._send_json({"schema": 2, "id": rid, "markdown": f.read_text(encoding="utf-8")})
                    else:
                        self._send_json({"error": "report not found"}, 404)
                except Exception:
                    self._send_json({"error": "invalid id"}, 400)
            elif p == "/health":
                self._send_json({"status": "ok"})
            else:
                self._send_json({"error": "not found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
    def do_POST(self):
        try:
            p = self.path
            b = self._read_body()
            if p == "/api/settings":
                self._send_json({"ok": True, "changed": _apply_patch(b)})
            elif p == "/api/agent/add":
                self._send_json(_add_agent(b))
            elif p == "/api/agent/remove":
                self._send_json(_remove_agent(b))
            elif p == "/api/onboard":
                self._send_json(_onboard(b))
            elif p == "/api/solve":
                self._send_json(_solve_plan(b))
            elif p == "/api/delegate":
                self._send_json(_delegate(b))
            elif p == "/api/ask":
                self._send_json(_ask(b))
            elif p == "/api/patrol":
                self._send_json(_patrol_async())
            elif p == "/api/mock/start":
                self._send_json(_mock_start())
            elif p == "/api/mock/stop":
                self._send_json(_mock_stop())
            else:
                self._send_json({"error": "not found"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 400)
    def log_message(self, format, *args):
        pass

def run(port=DEFAULT_PORT):
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Stratofly control room  ->  http://localhost:" + str(port) + "/")
    print("  GET  /api/state /api/settings /api/env-status /api/free-apis /api/agent/<id> /api/activity /api/report/<id> /health")
    print("  POST /api/ask /api/patrol /api/settings /api/agent/add /api/agent/remove /api/onboard /api/mock/start /api/mock/stop")
    print("  Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("stopped.")
        srv.server_close()

if __name__ == "__main__":
    run()
