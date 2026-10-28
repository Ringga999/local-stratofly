# fix_bubble.py - one-shot: fix bubble logic + installer threading bug.
# 1) api_server.py: filter useless bubbles ("not implemented", "waiting...")
#    and replace with "ready - waiting for task" for idle agents.
# 2) Re-run smoke test with threading imported (fix installer bug).
from pathlib import Path
import sys, ast, re, subprocess, shutil, threading, time, json, urllib.request

B = Path(__file__).resolve().parent
LIB = B / "lib"
API = LIB / "api_server.py"

print("=" * 70)
print(" FIX BUBBLE LOGIC + INSTALLER THREADING BUG")
print("=" * 70)

# ---- STEP 1: patch api_server.py bubble logic ----------------------------
print("\nSTEP 1  Patching lib/api_server.py bubble logic...")
src = API.read_text(encoding="utf-8")

# Find the _state function and replace the bubble logic
# Old logic:
#   bubble = lv.get("bubble")
#   if not bubble:
#       if state == "idle":
#           bubble = "ready - waiting for task"
#       else:
#           bubble = state
# New logic: filter useless bubbles
old_bubble_block = '''        bubble = lv.get("bubble")
        if not bubble:
            if state == "idle":
                bubble = "ready - waiting for task"
            else:
                bubble = state'''

new_bubble_block = '''        bubble = lv.get("bubble") or ""
        # Filter useless bubbles from old mock/patrol runs
        useless = ["not implemented", "waiting..."]
        if state == "idle" and (not bubble or any(u in bubble.lower() for u in useless)):
            bubble = "ready - waiting for task"
        elif not bubble:
            bubble = state'''

if old_bubble_block in src:
    src = src.replace(old_bubble_block, new_bubble_block)
    API.write_text(src, encoding="utf-8")
    print("  OK patched bubble logic (filter useless bubbles)")
else:
    print("  WARNING: could not find old bubble block - manual check needed")
    # Try alternative pattern
    if 'bubble = lv.get("bubble")' in src:
        print("  Found bubble line but pattern differs - trying regex patch")
        src = re.sub(
            r'(\s+)bubble = lv\.get\("bubble"\)\s*\n\s+if not bubble:\s*\n\s+if state == "idle":\s*\n\s+bubble = "ready - waiting for task"\s*\n\s+else:\s*\n\s+bubble = state',
            r'\1bubble = lv.get("bubble") or ""\n\1# Filter useless bubbles from old mock/patrol runs\n\1useless = ["not implemented", "waiting..."]\n\1if state == "idle" and (not bubble or any(u in bubble.lower() for u in useless)):\n\1    bubble = "ready - waiting for task"\n\1elif not bubble:\n\1    bubble = state',
            src
        )
        API.write_text(src, encoding="utf-8")
        print("  OK patched bubble logic via regex")

# ---- STEP 2: runtime smoke test (with threading imported) ----------------
print("\nSTEP 2  Runtime smoke test (threading imported)...")
ok = True
try:
    sys.path.insert(0, str(B))
    # Reload api_server module
    if "lib.api_server" in sys.modules:
        del sys.modules["lib.api_server"]
    from lib import api_server as A
    srv = A.ThreadingHTTPServer(("127.0.0.1", 0), A.Handler)
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    time.sleep(0.5)
    base = "http://127.0.0.1:" + str(port)
    def get(path):
        with urllib.request.urlopen(base + path, timeout=8) as r:
            return r.status, r.read().decode("utf-8", "replace")
    st, body = get("/health")
    print("  /health ->", st); ok &= (st == 200)
    st, body = get("/api/state")
    js = json.loads(body)
    bubbles = [(a["id"], a.get("bubble", "")) for a in js.get("agents", [])]
    bubbles_clean = all("not implemented" not in b for _, b in bubbles)
    print("  /api/state ->", st, "agents:", len(js.get("agents", [])))
    print("  bubbles:", bubbles[:3], "..." if len(bubbles) > 3 else "")
    print("  bubbles_clean:", bubbles_clean)
    ok &= (st == 200 and bubbles_clean)
    st, body = get("/api/agent/scout")
    js = json.loads(body)
    print("  /api/agent/scout ->", st, "role:", js.get("role"), "modules:", len(js.get("modules", [])))
    ok &= (st == 200 and "modules" in js)
    st, body = get("/api/free-apis")
    js = json.loads(body)
    print("  /api/free-apis ->", st, "apis:", len(js.get("apis", [])))
    ok &= (st == 200 and len(js.get("apis", [])) >= 5)
    st, body = get("/")
    has_modal = 'id="agentModal"' in body
    has_menu = 'id="freeApisMenu"' in body
    no_onclick = "onclick=" not in body
    print("  / (app.html) ->", st, "chars:", len(body), "modal:", has_modal, "menu:", has_menu, "no-onclick:", no_onclick)
    ok &= (st == 200 and has_modal and has_menu and no_onclick)
    srv.shutdown(); srv.server_close()
except Exception as e:
    ok = False
    print("  SMOKE EXCEPTION:", repr(e))
print("  SMOKE RESULT:", "ALL GREEN" if ok else "FAILED")

print("\n" + "=" * 70)
print(" DONE." if ok else " DONE (SMOKE FAILED)")
print(" Run:   python main.py serve")
print(" Open:  http://localhost:8765/")
print(" Cleanup: del fix_bubble.py")
print("=" * 70)