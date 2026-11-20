# lib/concordium_read.py - Concordium Agent Registry READ layer (no keys, no signing).
import json, urllib.request, urllib.error
MCP = "https://agent-registry-mcp.concordium.com"
_SEED = [
    {"token_id": 484, "name": "Market Data Agent", "owner": "3z9dkoTnLi2HEZvjnmKrMec2Gk2NKcEhdi4PugDWzP4GQtZiFa", "status": "Active"},
    {"token_id": 512, "name": "Climate Sentinel", "owner": "4NYPraeuAejuvbjity17qqccEng2HqNhFXoPdQ7iNpXfjqvUxx", "status": "Active"},
    {"token_id": 517, "name": "Ledger Clerk", "owner": "3z9dkoTnLi2HEZvjnmKrMec2Gk2NKcEhdi4PugDWzP4GQtZiFa", "status": "Revoked"},
    {"token_id": 530, "name": "Geo Researcher", "owner": "4NYPraeuAejuvbjity17qqccEng2HqNhFXoPdQ7iNpXfjqvUxx", "status": "Active"},
]
def _http(url, data=None, headers=None, timeout=20):
    h = {"User-Agent": "stratofly-ccdread", "Accept": "application/json, text/event-stream"}
    if headers: h.update(headers)
    body = json.dumps(data).encode("utf-8") if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "ignore")
        sid = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id")
    if raw.lstrip().startswith("{") or raw.lstrip().startswith("["):
        return json.loads(raw), sid
    out = None
    for line in raw.splitlines():
        if line.startswith("data:"):
            try: out = json.loads(line[5:].strip())
            except Exception: pass
    return out, sid
def _mcp(tool, args):
    try:
        _, sid = _http(MCP + "/mcp", {"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "stratofly", "version": "1"}}})
        hh = {"Mcp-Session-Id": sid} if sid else {}
        _http(MCP + "/mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"}, hh)
        res, _ = _http(MCP + "/mcp", {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": tool, "arguments": args}}, hh)
        if not res or "error" in res: return None
        r = res.get("result", {})
        if "structuredContent" in r: return r["structuredContent"]
        for c in r.get("content", []):
            if c.get("type") == "text":
                try: return json.loads(c["text"])
                except Exception: return {"text": c["text"]}
        return r
    except Exception:
        return None
def check_badge(badge):
    if not badge: return {"ok": False, "error": "empty badge"}
    try:
        j, _ = _http(MCP + "/v1/check-badge/" + badge)
        return {"ok": True, "data": j}
    except urllib.error.HTTPError as e:
        try: return {"ok": False, "error": json.loads(e.read().decode()).get("message", str(e))}
        except Exception: return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
def _rows(d):
    if isinstance(d, list): return d
    if isinstance(d, dict):
        for k in ("agents", "items", "results", "data"):
            if isinstance(d.get(k), list): return d[k]
        for v in d.values():
            if isinstance(v, list) and v and isinstance(v[0], dict): return v
    return []
def agents(network, q):
    d = _mcp("list_agents", {"network": network})
    rows = _rows(d) if d else []
    source = "live" if rows else "sample"
    if not rows: rows = [dict(x) for x in _SEED]
    out = []
    for a in rows:
        tid = a.get("token_id", a.get("id", a.get("tokenId")))
        own = a.get("owner", a.get("owner_account", a.get("ownerAddress", a.get("account", ""))))
        nm = a.get("name", a.get("agent_name", a.get("title"))) or ("Agent #" + str(tid))
        out.append({"token_id": tid, "name": nm, "owner": own or "",
                    "status": a.get("status") or "Active",
                    "agent_uri": a.get("agent_uri", a.get("agentUri", ""))})
    if q:
        ql = q.lower()
        out = [a for a in out if ql in str(a["name"]).lower() or ql in str(a["owner"]).lower() or ql in str(a["token_id"])]
    return {"ok": True, "source": source, "total": len(out), "agents": out}
