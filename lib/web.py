# lib/web.py - Stratofly localhost dashboard (S3). Stdlib only.
# Reads the page from lib/dashboard.html (no embedded HTML -> no quote traps).
# Consumes the GREEN lib.settings + lib.model_kind. Zero new dependencies.
import json, os, sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from lib import settings
from lib import model_kind

HERE = Path(__file__).resolve().parent
DEFAULT_PORT = 8765
ALLOWED = {"enabled", "autonomous", "cadence_hours", "brain", "division"}
BRAIN_NAMES = ["WORKHORSE", "SPECIALIST", "LIFELINE"]

def _page():
    return (HERE / "dashboard.html").read_text(encoding="utf-8")

def _state():
    d = settings.load()
    agents = []
    for aid, a in d.get("agents", {}).items():
        en = bool(a.get("enabled", True))
        au = bool(a.get("autonomous", True))
        if not en:
            status, cls = "OFF", "off"
        elif au:
            status, cls = "ARMED", "armed"
        else:
            status, cls = "STANDBY", "standby"
        agents.append({"id": aid, "division": a.get("division", "General"),
                       "brain": a.get("brain", "WORKHORSE"),
                       "cadence_hours": a.get("cadence_hours", 6),
                       "autonomous": au, "enabled": en,
                       "status": status, "cls": cls})
    brains = {}
    for nm in BRAIN_NAMES:
        ch = d.get("brains", {}).get(nm, [])
        brains[nm] = [{"provider": e.get("provider"), "model": e.get("model"),
                       "kind": model_kind.classify(e.get("model", "")),
                       "badge": model_kind.badge(e.get("model", ""))} for e in ch]
    per = settings.agents_per_provider(d)
    caps = d.get("limits", {})
    total = sum(1 for a in d.get("agents", {}).values() if a.get("enabled", True))
    return {"schema": d.get("settings_schema"), "template": d.get("crew_template"),
            "repos": d.get("repos", []), "brains": brains, "agents": agents,
            "per_provider": per,
            "max_per_provider": caps.get("max_per_provider", 10),
            "max_total": caps.get("max_total_agents", 30), "total": total,
            "note": "config view - live telemetry arrives with the scheduler bridge (S4)"}

def _apply_patch(patch):
    d = settings.load()
    changed = []
    if "repos" in patch and isinstance(patch["repos"], list):
        d["repos"] = [r for r in patch["repos"] if isinstance(r, str) and "/" in r]
        changed.append("repos")
    if "limits" in patch and isinstance(patch["limits"], dict):
        for k in ("max_total_agents", "max_per_provider"):
            if k in patch["limits"]:
                v = patch["limits"][k]
                if isinstance(v, int) and v >= 1:
                    d["limits"][k] = v
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
                d["agents"][aid][f] = v
                changed.append("agents." + aid + "." + f)
    if changed:
        settings.save(d)
    return changed

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
    print("(config view; live telemetry with S4 scheduler bridge). Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("stopped.")

if __name__ == "__main__":
    serve()
