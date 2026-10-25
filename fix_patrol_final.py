# fix_patrol_final.py - robust patrol trigger with better error handling.
from pathlib import Path
import sys, ast, subprocess, time

B = Path(__file__).resolve().parent
LIB = B / "lib"

print("=" * 64)
print(" ROBUST PATROL FIX (write-before-run + stderr capture + timeout)")
print("=" * 64)

# ---------------- STEP 1: test if patrol command works ---------------------
print("\nSTEP 1  Testing patrol command directly...")
try:
    result = subprocess.run([sys.executable, str(B / "main.py"), "patrol"],
                           cwd=str(B), capture_output=True, text=True, timeout=30)
    print("  Patrol exit code:", result.returncode)
    print("  Patrol stdout (first 200 chars):", result.stdout[:200] if result.stdout else "(empty)")
    print("  Patrol stderr (first 200 chars):", result.stderr[:200] if result.stderr else "(empty)")
except subprocess.TimeoutExpired:
    print("  Patrol TIMEOUT (took >30s) - might be blocking/waiting for input")
except Exception as e:
    print("  Patrol ERROR:", str(e))

# ---------------- STEP 2: rewrite web.py with robust patrol ----------------
print("\nSTEP 2  Rewriting lib/web.py (robust patrol + better logging)...")

WEB = """# lib/web.py v4 - robust patrol with write-before-run + stderr capture.
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
            "note": "patrol writes log before starting"}

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
    # Write BEFORE starting (proof we tried)
    LOG_FILE.write_text("=== PATROL STARTED " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===\\n", encoding="utf-8")
    try:
        # Run patrol and capture BOTH stdout and stderr
        proc = subprocess.Popen([sys.executable, str(_ROOT / "main.py"), "patrol"],
                               cwd=str(_ROOT), stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, bufsize=1)
        # Read line by line and append to log
        for line in proc.stdout:
            LOG_FILE.write_text(line, encoding="utf-8")
        proc.wait()
        LOG_FILE.write_text("\\n=== PATROL FINISHED " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===\\n", encoding="utf-8")
    except Exception as e:
        LOG_FILE.write_text("\\n=== PATROL ERROR " + time.strftime("%Y-%m-%d %H:%M:%S") + " ===\\n", encoding="utf-8")
        LOG_FILE.write_text("Error: " + str(e) + "\\n", encoding="utf-8")
    finally:
        patrol_running = False

def _trigger_patrol():
    global patrol_thread
    if patrol_running:
        return {"ok": False, "msg": "Patrol already running."}
    patrol_thread = threading.Thread(target=_run_patrol_background, daemon=True)
    patrol_thread.start()
    return {"ok": True, "msg": "Patrol started. Check log for progress."}

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
    print("(robust patrol with write-before-run). Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("stopped.")

if __name__ == "__main__":
    serve()
"""

try:
    ast.parse(WEB)
except SyntaxError as e:
    print("ABORT: web.py v4 has syntax error (%s)" % e)
    sys.exit(1)

(LIB / "web.py").write_text(WEB, encoding="utf-8")
print("  OK rewrote lib/web.py v4 (robust patrol)")

# ---------------- STEP 3: update dashboard.html (better UI) ----------------
print("\nSTEP 3  Updating lib/dashboard.html (better patrol UI)...")

HTML = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Stratofly - Localhost Dashboard</title>
<style>
:root{--bg:#0e1116;--card:#161b22;--ink:#e6edf3;--mut:#8b949e;--line:#30363d;
--green:#3fb950;--amber:#d29922;--grey:#6e7681;--blue:#58a6ff;--red:#f85149}
@media(prefers-color-scheme:light){:root{--bg:#f6f8fa;--card:#fff;--ink:#1f2328;
--mut:#656d76;--line:#d0d7de}}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 system-ui,Segoe UI,Roboto,sans-serif;
background:var(--bg);color:var(--ink)}
header{padding:18px 22px;border-bottom:1px solid var(--line);display:flex;
align-items:center;gap:12px;flex-wrap:wrap}
header h1{font-size:18px;margin:0}header .tag{color:var(--mut);font-size:12px}
.wrap{padding:22px;max-width:1100px;margin:0 auto;display:grid;gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px}
.card h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:0 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.agent{border:1px solid var(--line);border-radius:8px;padding:10px;display:flex;
flex-direction:column;gap:6px}
.agent .nm{font-weight:600}.agent .dv{color:var(--mut);font-size:12px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:6px}
.armed .dot{background:var(--green)}.standby .dot{background:var(--amber)}.off .dot{background:var(--grey)}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:12px}
.btn{cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--ink);
border-radius:6px;padding:3px 8px;font-size:12px}
.btn:hover{border-color:var(--blue)}
.btn-primary{background:var(--blue);border-color:var(--blue);color:#fff}
.btn-primary:hover{background:#79c0ff}
.btn:disabled{opacity:0.5;cursor:not-allowed}
.brain{border-left:3px solid var(--blue);padding:6px 10px;margin:6px 0;
background:rgba(88,166,255,.06);border-radius:0 6px 6px 0}
.badge{font-size:11px;padding:1px 6px;border-radius:20px;border:1px solid var(--line);color:var(--mut)}
.bar{height:8px;background:var(--line);border-radius:6px;overflow:hidden;margin-top:4px}
.bar i{display:block;height:100%;background:var(--green)}
.bar.full i{background:var(--red)}
.mut{color:var(--mut)}.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px}
.note{font-size:12px;color:var(--mut);border-top:1px dashed var(--line);padding-top:10px;margin-top:6px}
.repolist li{margin:2px 0}
.report{border-left:3px solid var(--green);padding:6px 10px;margin:6px 0;
background:rgba(63,185,80,.06);border-radius:0 6px 6px 0;font-size:12px}
.logbox{background:var(--bg);border:1px solid var(--line);border-radius:6px;
padding:10px;max-height:300px;overflow-y:auto;font-family:ui-monospace,Menlo,Consolas,monospace;
font-size:11px;white-space:pre-wrap;word-break:break-all;line-height:1.4}
.running{color:var(--amber);font-weight:600}
</style></head><body>
<header><h1>&#9876; Stratofly</h1><span class="tag">localhost dashboard &middot; one crew, every free API</span>
<button class="btn btn-primary" id="patrolBtn" onclick="patrol()">Run Patrol Now</button>
<span class="tag" id="clock"></span></header>
<div class="wrap">
 <div class="card"><h2>Crew &middot; config status</h2><div class="grid" id="agents"></div>
   <div class="note" id="note"></div></div>
 <div class="card"><h2>Brains &middot; model-kind aware</h2><div id="brains"></div></div>
 <div class="card"><h2>Free-tier limits</h2><div id="limits"></div></div>
 <div class="card"><h2>Watched repos</h2><ul class="repolist mono" id="repos"></ul></div>
 <div class="card"><h2>Recent reports</h2><div id="reports"></div></div>
 <div class="card"><h2>Patrol log</h2><div class="logbox mono" id="patrolLog">Loading...</div></div>
</div>
<script>
function $(id){return document.getElementById(id);}
async function api(p,opt){var r=await fetch(p,opt);return r.json();}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){
 return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
async function load(){
 var s=await api("/api/state");
 $("note").textContent=s.note||"";
 $("agents").innerHTML=s.agents.map(function(a){
   return '<div class="agent '+a.cls+'">'+
     '<div class="nm"><span class="dot"></span>'+esc(a.id)+'</div>'+
     '<div class="dv">'+esc(a.division)+' &middot; '+esc(a.role||"Operator")+' &middot; '+esc(a.brain)+' &middot; '+a.cadence_hours+'h</div>'+
     '<div class="row">'+
     '<button class="btn" onclick="tog(\\''+esc(a.id)+'\\',\\'autonomous\\')">'+(a.autonomous?"auto:ON":"auto:OFF")+'</button>'+
     '<button class="btn" onclick="tog(\\''+esc(a.id)+'\\',\\'enabled\\')">'+(a.enabled?"live":"paused")+'</button>'+
     '</div></div>';
 }).join("");
 $("brains").innerHTML=Object.keys(s.brains).map(function(k){
   var ch=s.brains[k];
   var inner=ch.length?ch.map(function(e){
     return '<span class="mono">'+esc(e.provider)+"/"+esc(e.model)+'</span> <span class="badge">'+esc(e.kind)+'</span>';
   }).join("<br>"):'<span class="mut">(empty)</span>';
   return '<div class="brain"><strong>'+k+'</strong> <span class="mut">('+ch.length+')</span><br>'+inner+'</div>';
 }).join("");
 var bars=Object.keys(s.per_provider).map(function(p){
   var n=s.per_provider[p];var full=n>=s.max_per_provider;
   return '<div>'+esc(p)+' <span class="mono">'+n+"/"+s.max_per_provider+'</span>'+
     '<div class="bar '+(full?"full":"")+'"><i style="width:'+Math.min(100,n/s.max_per_provider*100)+'%"></i></div></div>';
 }).join("");
 var tfull=s.total>=s.max_total;
 $("limits").innerHTML=bars+'<div style="margin-top:8px">total <span class="mono">'+s.total+"/"+s.max_total+'</span>'+
   '<div class="bar '+(tfull?"full":"")+'"><i style="width:'+Math.min(100,s.total/s.max_total*100)+'%"></i></div></div>';
 $("repos").innerHTML=(s.repos.length?s.repos:["(none)"]).map(function(r){return "<li>"+esc(r)+"</li>";}).join("");
 $("reports").innerHTML=(s.reports.length?s.reports.map(function(r){
   return '<div class="report"><strong>'+esc(r.name)+'</strong><br><span class="mut">'+esc(r.date)+'</span></div>';
 }).join("")):'<span class="mut">(no reports yet)</span>';
 $("clock").textContent="updated "+new Date().toLocaleTimeString();
 loadPatrolLog();
}
async function tog(id,f){
 var s=await api("/api/state");var a=null;
 for(var i=0;i<s.agents.length;i++){if(s.agents[i].id===id){a=s.agents[i];break;}}
 if(!a)return;
 var patch={agents:{}};patch.agents[id]={};patch.agents[id][f]=!a[f];
 await api("/api/settings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(patch)});
 load();
}
async function patrol(){
 var btn=$("patrolBtn");
 if(btn.disabled)return;
 if(!confirm("Trigger patrol now? This will run all enabled agents."))return;
 btn.disabled=true;
 btn.textContent="Starting...";
 try{
   var r=await api("/api/patrol",{method:"POST"});
   if(r.ok){
     btn.textContent="Patrol Running...";
     alert(r.msg||"Patrol started. Check log below.");
   }else{
     alert("Error: "+r.msg);
     btn.disabled=false;
     btn.textContent="Run Patrol Now";
   }
 }catch(e){
   alert("Failed to start patrol: "+e.message);
   btn.disabled=false;
   btn.textContent="Run Patrol Now";
 }
 loadPatrolLog();
}
async function loadPatrolLog(){
 var s=await api("/api/state");
 var btn=$("patrolBtn");
 if(s.patrol_running){
   if(!btn.disabled)btn.disabled=true;
   if(btn.textContent!="Patrol Running...")btn.textContent="Patrol Running...";
 }else{
   if(btn.disabled && btn.textContent=="Patrol Running..."){
     btn.disabled=false;
     btn.textContent="Run Patrol Now";
   }
 }
 var log=await api("/api/patrol/log");
 $("patrolLog").textContent=log.log||"(no log yet)";
}
load();
setInterval(load,5000);
setInterval(loadPatrolLog,1000);
</script></body></html>
'''

(LIB / "dashboard.html").write_text(HTML, encoding="utf-8")
print("  OK rewrote lib/dashboard.html (better patrol UI + error handling)")

# ---------------- STEP 4: smoke test ---------------------------------------
print("\nSTEP 4  Smoke test...")
r = subprocess.run([sys.executable, "-c",
    "from lib import web; print('  import OK'); print('  patrol_running:', web.patrol_running); "
    "print('  log file exists:', (web.LOG_FILE).exists())"])
print("  smoke exit code:", r.returncode)

print("\n" + "=" * 64)
print(" DONE.")
print(" 1. Restart dashboard: python main.py web")
print(" 2. Click 'Run Patrol Now' -> log should update immediately!")
print(" Cleanup: del fix_patrol_final.py")