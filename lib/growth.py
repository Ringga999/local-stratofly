# lib/growth.py - GrowthOperator copilot (read-only analysis). No network, no creds, no live actions.
import re
def _rows(text):
    out = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = [x.strip() for x in line.split(",")]
        h = parts[0].lstrip("@").strip()
        if not h: continue
        def num(i, d=None):
            try: return float(parts[i])
            except Exception: return d
        out.append({"handle": h, "followers": num(1), "following": num(2),
                    "mutual": num(3), "active_days": num(4),
                    "visibility": (parts[5].lower() if len(parts) > 5 else "")})
    seen = set(); ded = []
    for r in out:
        if r["handle"] not in seen: seen.add(r["handle"]); ded.append(r)
    return ded
def dryrun(q):
    rows = _rows(q.get("list", ""))
    vis = q.get("visibility", "any"); ratio = q.get("ratio", "any")
    mutual_min = float(q.get("mutual_min", 0) or 0)
    active_max = float(q.get("active_days", 0) or 0)
    not_bot = q.get("not_bot", "0") == "1"
    quota = int(q.get("quota", 100) or 100)
    black = set(x.strip().lstrip("@") for x in q.get("blacklist", "").split(",") if x.strip())
    white = set(x.strip().lstrip("@") for x in q.get("whitelist", "").split(",") if x.strip())
    out = []; n_follow = 0
    for r in rows:
        h = r["handle"]; dec = "follow"; why = []
        has_meta = r["followers"] is not None and r["following"] is not None
        if h in black: dec, why = "skip", ["blacklist"]
        elif h in white: dec, why = "follow", ["whitelist"]
        elif not has_meta: dec, why = "review", ["metadata unknown; manual check"]
        else:
            if vis != "any" and r["visibility"] and r["visibility"] != vis: dec, why = "skip", ["visibility=" + r["visibility"]]
            elif ratio == "lt" and not (r["followers"] < r["following"]): dec, why = "skip", ["ratio not followers<following"]
            elif ratio == "gt" and not (r["followers"] > r["following"]): dec, why = "skip", ["ratio not followers>following"]
            elif mutual_min and (r["mutual"] or 0) < mutual_min: dec, why = "skip", ["mutual<min"]
            elif active_max and (r["active_days"] is not None and r["active_days"] > active_max): dec, why = "skip", ["stale activity"]
            elif not_bot and (r["followers"] == 0 or (r["following"] > 5000 and r["followers"] < 50)): dec, why = "skip", ["bot-suspect"]
        if dec == "follow":
            if n_follow >= quota: dec, why = "review", ["quota reached"]
            else: n_follow += 1; why = why or ["passes criteria"]
        out.append(dict(r, decision=dec, reason="; ".join(why)))
    s = {"total": len(out), "follow": sum(1 for x in out if x["decision"] == "follow"),
         "skip": sum(1 for x in out if x["decision"] == "skip"),
         "review": sum(1 for x in out if x["decision"] == "review")}
    return {"ok": True, "summary": s, "rows": out}
