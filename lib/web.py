# lib/web.py v5 - simple patrol: subprocess.run like terminal.
import json, os, sys, subprocess, time, threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from lib import settings
from lib import model_kind

HERE = Path(__file__).resolve().parent
DEFAULT_PORT = 8765
ALLOWED = {"enabled", "autonomous", "cadence_hours", "brain", "division", "role"}
BRAIN_NAMES = ["WORKHORSE", "SPECIALIST", "LIFELINE"]
LOG_FILE = HERE / "patrol_log.txt"
patrol_running = False
patrol_thread = None

def _page():
    return (HERE / "dashboard.html").read_text(encoding="utf-8")

def _get_patrol_log():
    if LOG_FILE.exists():
        return LOG_FILE.read_text(encoding="utf-8")
    return "No patrol log yet."

def _state():
    d = settings.load()
    agents = []
    for aid, a in d.get("agents", {}).items():
        en = bool(a.get("enabled", True))
        au = bool(a.get("autonomous", True))
        status, cls = ("OFF", "off") if not en else (("ARMED", "armed") if au else ("STANDBY", "standby"))
        agents.append({"id": aid, "division": a.get("division", "General"),
                       "role": a.get("role", "Operator"), "brain": a.get("brain", "WORKHORSE"),
                       "cadence_hours": a.get("cadence_hours", 6), "autonomous": au, "enabled": en,
                       "status": status, "cls": cls})
    brains = {nm: [{"provider": e.get("provider"), "model": e.get("model"),
                    "kind": model_kind.classify(e.get("model", "")),
                    "badge": model_kind.badge(e.get("model", ""))} for e in d.get("brains", {}).get(nm, [])]
              for nm in BRAIN_NAMES}
    per = settings.agents_per_provider(d)
    caps = d.get("limits", {})
    total = sum(1 for a in d.get("agents", {}).values() if a.get("enabled", True))
    reports = _list_reports()
    return {"schema": d.get("settings_schema"), "template": d.get("crew_template"),
            "repos": d.get("repos", []), "brains": brains, "agents": agents,
            "per_provider": per, "max_per_provider": caps.get("max_per_provider", 10),
            "max_total": caps.get("max_total_agents", 30), "total": total,
            "reports": reports, "patrol_running": patrol_running,
            "note": "patrol runs like terminal command"}

def _list_reports():
    reports_dir = _ROOT / "reports"
    if not reports_dir.exists():
        return []
    files = sorted([f for f in reports_dir.iterdir() if f.suffix == ".md"],
                   key=lambda f: f.stat().st_mtime, reverse=True)[:5]
    return [{"name": f.stem, "date": f.stat().st_mtime} for f in files]

def _apply_patch(patch):
    d = settings.load()
    changed = []
    if "repos" in patch and isinstance(patch["repos"], list):
        d["repos"] = [r for r in patch["repos"] if isinstance(r, str) and "/" in r]
        changed.append("repos")
    if "limits" in patch and isinstance(patch["limits"], dict):
        for k in ("max_total_agents", "max_per_provider"):
            if k in patch["limits"] and isinstance(patch["limits"][k], int) and patch["limits"][k] >= 1:
                d["limits"][k] = patch["limits"][k]
                changed.append("limits." + k)
    if "agents" in patch and isinstance(patch["agents"], dict):
        for aid, fields in patch["agents"].items():
            if aid not in d["agents"] or not isinstance(fields, dict):
                continue
            for f, v in fields.items():
                if f not in ALLOWED:
                    continue
                if f == "cadence_hours" and not (isinstance(v, int) and 1 <= v <= 168):
                    continue
                if f == "brain" and v not in BRAIN_NAMES:
                    continue
                if f in ("enabled", "autonomous") and not isinstance(v, bool):
                    continue
                if f == "division" and not isinstance(v, str):
                    continue
                if f == "role" and v not in ["Solver","Architect","Crafter","Analyst","Communicator","Sentinel","Operator"]:
                    continue
                d["agents"][aid][f] = v
                changed.append("agents." + aid + "." + f)
    if changed:
        settings.save(d)
    return changed

def _run_patrol_background():
    global patrol_running
    if patrol_running:
        return
    patrol_running = True
    try:
        # Run patrol EXACTLY like terminal: subprocess.run with capture_output
        result = subprocess.run([sys.executable, str(_ROOT / "main.py"), "patrol"],
                               cwd=str(_ROOT), capture_output=True, text=True, timeout=60)
        # Write ALL output to log after patrol finishes
        log_content = "=== PATROL STARTED " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===\n\n"
        if result.stdout:
            log_content += result.stdout
        if result.stderr:
            log_content += "\nSTDERR:\n" + result.stderr
        log_content += "\n=== PATROL FINISHED " + time.strftime("%Y-%m-%d %H:%M:%S") + " ==="
        log_content += " (exit code: " + str(result.returncode) + ")\n"
        LOG_FILE.write_text(log_content, encoding="utf-8")
    except subprocess.TimeoutExpired:
        LOG_FILE.write_text("=== PATROL TIMEOUT (>60s) ===\n", encoding="utf-8")
    except Exception as e:
        LOG_FILE.write_text("=== PATROL ERROR: " + str(e) + " ===\n", encoding="utf-8")
    finally:
        patrol_running = False

def _trigger_patrol():
    global patrol_thread
    if patrol_running:
        return {"ok": False, "msg": "Patrol already running."}
    patrol_thread = threading.Thread(target=_run_patrol_background, daemon=True)
    patrol_thread.start()
    return {"ok": True, "msg": "Patrol started. Log will update when finished."}

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        try:
            if self.path == "/" or self.path.startswith("/index"):
                self._send(200, _page(), "text/html; charset=utf-8")
            elif self.path == "/api/state":
                self._send(200, json.dumps(_state()))
            elif self.path == "/api/settings":
                self._send(200, json.dumps(settings.load()))
            elif self.path == "/api/patrol/log":
                self._send(200, json.dumps({"log": _get_patrol_log(), "running": patrol_running}))
            else:
                self._send(404, json.dumps({"error": "not found"}))
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}))
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n).decode("utf-8") if n else "{}"
            patch = json.loads(raw)
            if self.path == "/api/settings":
                changed = _apply_patch(patch)
                self._send(200, json.dumps({"ok": True, "changed": changed}))
            elif self.path == "/api/patrol":
                result = _trigger_patrol()
                self._send(200, json.dumps(result))
            else:
                self._send(404, json.dumps({"error": "not found"}))
        except Exception as e:
            self._send(400, json.dumps({"error": str(e)}))
    def log_message(self, *a):
        pass

def serve(port=None):
    p = port or int(os.getenv("STRATOFLY_WEB_PORT", DEFAULT_PORT))
    try:
        i = sys.argv.index("web")
        if len(sys.argv) > i + 1:
            p = int(sys.argv[i + 1])
    except Exception:
        pass
    httpd = ThreadingHTTPServer(("127.0.0.1", p), H)
    print("Stratofly dashboard  ->  http://localhost:" + str(p) + "/")
    print("(patrol runs like terminal command). Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("stopped.")

if __name__ == "__main__":
    serve()
