import json, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from lib import memory
from config import REPORTS_DIR

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/state':
            agents = memory.get_all_agent_states()
            if not agents:
                agents = [{"agent": a, "state": "idle", "action": "-", "target": "-",
                           "bubble": "menunggu…", "report_id": -1, "since_ts": 0}
                          for a in ['scout','triage','sentinel','scribe','tester',
                                    'medic','release','bridge','herald','diplomat']]
            self._send_json({"schema": 1, "online": True, "ts": __import__('time').time(), "agents": agents})
        
        elif self.path.startswith('/api/activity'):
            limit = 50
            if 'limit=' in self.path:
                try:
                    limit = int(self.path.split('limit=')[1].split('&')[0])
                except:
                    pass
            events = memory.recent_events(limit)
            self._send_json({"schema": 1, "events": events})
        
        elif self.path.startswith('/api/report/'):
            try:
                rid = int(self.path.split('/api/report/')[1])
                f = REPORTS_DIR / f"report_{rid}.md"
                if f.exists():
                    self._send_json({"schema": 1, "id": rid, "markdown": f.read_text(encoding="utf-8")})
                else:
                    self._send_json({"error": "report not found"}, 404)
            except:
                self._send_json({"error": "invalid id"}, 400)
        
        elif self.path == '/health':
            self._send_json({"status": "ok"})
        
        else:
            self._send_json({"error": "not found"}, 404)
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # senyap

def run(port=8765):
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f"🌉 API server hidup di http://127.0.0.1:{port}")
    print("   Endpoint: /api/state · /api/activity · /api/report/<id> · /health")
    print("   Tekan Ctrl+C untuk berhenti.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n API server berhenti.")
        server.server_close()