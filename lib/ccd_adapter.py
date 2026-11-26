# lib/ccd_adapter.py - C1 backend proxy (MCP testnet-only). No keys; signing stays in wallet.
import json, pathlib, urllib.request
MCP = "https://agent-registry-mcp.concordium.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP = ROOT/"config"/"ccd_agents.json"
def _http(url, data=None, headers=None, timeout=30):
    h = {"User-Agent": "stratofly-c1", "Accept": "application/json, text/event-stream"}
    if headers: h.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    if body is not None: h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "ignore"); sid = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id")
    if raw.lstrip().startswith("{") or raw.lstrip().startswith("["): return json.loads(raw), sid
    out = None
    for line in raw.splitlines():
        if line.startswith("data:"):
            try: out = json.loads(line[5:].strip())
            except Exception: pass
    return out, sid
def mcp(tool, args):
    args = dict(args); args.setdefault("network", "testnet")
    try:
        _, sid = _http(MCP+"/mcp", {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"stratofly","version":"1"}}})
        hh = {"Mcp-Session-Id": sid} if sid else {}
        _http(MCP+"/mcp", {"jsonrpc":"2.0","method":"notifications/initialized"}, hh)
        res, _ = _http(MCP+"/mcp", {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":tool,"arguments":args}}, hh)
        if not res or "error" in res: return {"ok": False, "error": "mcp error"}
        r = res.get("result", {})
        if "structuredContent" in r: return {"ok": True, "data": r["structuredContent"]}
        for c in r.get("content", []):
            if c.get("type") == "text":
                try: return {"ok": True, "data": json.loads(c["text"])}
                except Exception: return {"ok": True, "data": {"text": c["text"]}}
        return {"ok": True, "data": r}
    except Exception as e:
        return {"ok": False, "error": "internal error"}
def _load():
    try: return json.loads(MAP.read_text(encoding="utf-8"))
    except Exception: return {}
def _save(m):
    MAP.parent.mkdir(parents=True, exist_ok=True); MAP.write_text(json.dumps(m, indent=2), encoding="utf-8")
def session(account, genesis):
    if not account: return {"ok": False, "error": "no account"}
    if "testnet" not in (genesis or "").lower(): return {"ok": False, "error": "chain not testnet (fail-closed)"}
    return {"ok": True, "account": account, "genesis": genesis}
def card(agent_id, owner, public_base_url):
    r = mcp("build_agent_card", {"name": agent_id or "Stratofly Crew", "description": "Stratofly crew agent with user-owned on-chain identity.", "owner": owner, "network": "testnet"})
    if not r.get("ok"): return r
    d = r["data"]; cj = d.get("card") or d.get("card_json") or d
    if isinstance(cj, str):
        try: cj = json.loads(cj)
        except Exception: pass
    import hashlib
    h = d.get("sha256") or d.get("hash") or ("0x"+hashlib.sha256(json.dumps(cj, sort_keys=True).encode()).hexdigest())
    uri = (public_base_url or "").rstrip("/")
    try:
        (ROOT/"docs").mkdir(parents=True, exist_ok=True)
        (ROOT/"docs"/"agent-card.json").write_text(json.dumps(cj, indent=2), encoding="utf-8")
    except Exception: pass
    return {"ok": True, "card": cj, "hash": h, "uri": uri, "note": "commit docs/agent-card.json lalu push agar raw URL live"}
def prepare(owner, agent_uri, metadata_hash_hex):
    return mcp("build_register", {"sender": owner, "agent_uri": agent_uri, "metadata_hash_hex": metadata_hash_hex})
def confirm(owner):
    r = mcp("agents_by_owner", {"owner": owner})
    if not r.get("ok"): return r
    d = r["data"]; agents = d.get("agents") or []
    m = _load(); known = set(m.get(owner, {}).get("tokens", []))
    new = [a for a in agents if str(a.get("token_id")) not in known]
    if new:
        rec = m.setdefault(owner, {"tokens": []})
        for a in new: rec["tokens"].append(str(a.get("token_id")))
        _save(m)
    return {"ok": True, "count": d.get("count", len(agents)), "agents": agents, "new": new}
def pin(token_id, card_hash, sender):
    return mcp("build_set_agent_uri", {"token_id": token_id, "metadata_hash_hex": card_hash, "sender": sender})
def status():
    return {"ok": True, "map": _load()}
