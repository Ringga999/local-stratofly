# lib/wizard.py v2 - Stratofly settings wizard (S4: role dropdown).
# ASCII-only. Integrates model_kind (badge + polite warning), settings limits
# (HARD per-provider, SOFT total), and ROLE capability axis (7 roles).
from pathlib import Path
import sys
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from lib import settings
from lib import model_kind

BRAIN_NAMES = ["WORKHORSE", "SPECIALIST", "LIFELINE"]
ROLE_NAMES = ["Solver", "Architect", "Crafter", "Analyst", "Communicator", "Sentinel", "Operator"]
SUGGEST = [
    ("nvidia", "deepseek-ai/deepseek-coder-6.7b-instruct"),
    ("nvidia", "nvidia/nemotron-3.5-lightning-30b-a3b"),
    ("nvidia", "01-ai/yi-large"),
    ("nvidia", "microsoft/phi-3.5-moe-instruct"),
    ("nvidia", "mistralai/codestral-22b-instruct-v0.1"),
    ("nvidia", "meta/llama-3.2-90b-vision-instruct"),
]

def _ask(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("")
        return ""

def _ask_int(prompt, lo, hi):
    while True:
        v = _ask(prompt).strip()
        if v == "":
            return None
        try:
            n = int(v)
        except ValueError:
            print("  (enter a whole number)"); continue
        if lo <= n <= hi:
            return n
        print("  (must be between %d and %d)" % (lo, hi))

def _ask_yes(prompt):
    return _ask(prompt + " [y/N] ").strip().lower() in ("y", "yes")

def _prompt_choice(prompt, choices, back=("b", "")):
    keys = list(choices.keys())
    low = {k.lower(): k for k in keys}
    bl = {x.lower() for x in back}
    while True:
        s = _ask(prompt).strip().lower()
        if s in bl:
            return None
        if s in low:
            return low[s]
        opts = " / ".join("%s=%s" % (k, choices[k]) for k in keys)
        bk = back[0] if back and back[0] else "b"
        print("  (invalid. choose: %s | or '%s' to go back)" % (opts, bk))

def _model_line(prov, model):
    k = model_kind.classify(model)
    safe, _ = model_kind.is_safe_for_text(model)
    tag = "SAFE" if safe else "BLOCK"
    return "  [%s] %s/%s%s" % (tag, prov, model, model_kind.badge(model))

def _confirm_text_model(prov, model):
    safe, kind = model_kind.is_safe_for_text(model)
    if safe:
        return True
    print("  " + "-" * 58)
    print("  WARNING: " + model_kind.explain(kind))
    print("  You are assigning this to a TEXT crew (scout/triage/etc).")
    return _ask_yes("  Use it anyway?")

def _save(data):
    settings.save(data)
    print("  >> saved to settings.json")

# ---- step 1: repos -------------------------------------------------------
def step_repos(data):
    while True:
        print("\n[Repos] watched:")
        for i, r in enumerate(data["repos"]):
            print("  %d. %s" % (i + 1, r))
        if not data["repos"]:
            print("  (none yet)")
        c = _prompt_choice("  action a)dd / d)elete / b)ack > ",
                           {"a": "add", "d": "delete"})
        if c is None:
            return
        if c == "a":
            r = _ask("  repo (owner/name): ").strip()
            if r and "/" in r and r not in data["repos"]:
                data["repos"].append(r); _save(data)
            elif r:
                print("  (needs owner/name, and not already listed)")
        elif c == "d" and data["repos"]:
            n = _ask_int("  delete # (1-%d): " % len(data["repos"]), 1, len(data["repos"]))
            if n:
                data["repos"].pop(n - 1); _save(data)

# ---- step 2: brains ------------------------------------------------------
def _show_chain(data, name):
    ch = data["brains"].get(name, [])
    print("  %s chain (%d entr%s):" % (name, len(ch), "y" if len(ch) == 1 else "ies"))
    if not ch:
        print("     (empty - falls back to house model)")
    for i, e in enumerate(ch):
        print("     #%d %s" % (i + 1, _model_line(e["provider"], e["model"])))

def step_brains(data):
    while True:
        print("\n[Brains]  (#n = entries WITHIN that chain)")
        for nm in BRAIN_NAMES:
            _show_chain(data, nm)
        tok = _prompt_choice("  pick brain 1=WORKHORSE 2=SPECIALIST 3=LIFELINE / b > ",
                             {"1": "WORKHORSE", "2": "SPECIALIST", "3": "LIFELINE"})
        if tok is None:
            return
        name = BRAIN_NAMES[int(tok) - 1]
        act = _prompt_choice(
            "  action r)eplace(=1) a)ppend(=2) d)elete(=3) v)iew(=4) / b > ",
            {"r": "replace", "a": "append", "d": "delete", "v": "view",
             "1": "replace", "2": "append", "3": "delete", "4": "view"})
        if act is None:
            continue
        if act in ("v", "4"):
            continue
        if act in ("r", "1"):
            print("  enter chain as: prov/model,prov/model  (blank cancels)")
            raw = _ask("  > ").strip()
            if not raw:
                continue
            new, ok = [], True
            for part in raw.split(","):
                part = part.strip()
                if not part or "/" not in part:
                    print("  bad entry: " + part); ok = False; break
                pv, md = part.split("/", 1)
                if not _confirm_text_model(pv, md):
                    ok = False; break
                new.append({"provider": pv, "model": md})
            if ok and new:
                data["brains"][name] = new; _save(data)
            elif ok:
                print("  (refused: a brain chain must never be empty)")
        elif act in ("a", "2"):
            print("  suggestions:")
            for i, (pv, md) in enumerate(SUGGEST):
                print("   %d. %s" % (i + 1, _model_line(pv, md)))
            c2 = _prompt_choice("  pick 1-%d / 0=custom / b > " % len(SUGGEST),
                                {str(i + 1): SUGGEST[i][1].split("/")[-1] for i in range(len(SUGGEST))}
                                | {"0": "custom"})
            if c2 is None:
                continue
            if c2 == "0":
                raw = _ask("  prov/model: ").strip()
                if "/" not in raw:
                    print("  (needs prov/model)"); continue
                pv, md = raw.split("/", 1)
            else:
                pv, md = SUGGEST[int(c2) - 1]
            if not _confirm_text_model(pv, md):
                continue
            data["brains"].setdefault(name, []).append({"provider": pv, "model": md})
            _save(data)
        elif act in ("d", "3"):
            ch = data["brains"].get(name, [])
            if len(ch) <= 1:
                print("  (refused: cannot empty the last entry)"); continue
            n = _ask_int("  remove # (1-%d): " % len(ch), 1, len(ch))
            if n:
                ch.pop(n - 1); _save(data)

# ---- step 3: agents (manage/toggle) --------------------------------------
def _agent_table(data):
    print("  id        div          role         brain       cad  auto en")
    for aid, a in data["agents"].items():
        print("  %-9s %-12s %-12s %-11s %3d  %3s  %2s" % (
            aid, a.get("division", "General"), a.get("role", "Operator"),
            a.get("brain", "WORKHORSE"),
            a.get("cadence_hours", 6),
            "yes" if a.get("autonomous", True) else "NO",
            "yes" if a.get("enabled", True) else "NO"))

def step_agents(data):
    while True:
        print("\n[Agents]"); _agent_table(data)
        c = _prompt_choice("  t)oggle-en u)toggle-auto c)adence b)rain r)ole / k > ",
                           {"t": "toggle-enabled", "u": "toggle-autonomy",
                            "c": "cadence", "b": "brain", "r": "role"}, back=("k", "b", ""))
        if c is None:
            return
        aid = _ask("  agent id: ").strip()
        if aid not in data["agents"]:
            print("  (no such agent - see table above)"); continue
        a = data["agents"][aid]
        if c == "t":
            a["enabled"] = not a.get("enabled", True); _save(data)
        elif c == "u":
            a["autonomous"] = not a.get("autonomous", True); _save(data)
        elif c == "c":
            n = _ask_int("  cadence hours (1-168): ", 1, 168)
            if n:
                a["cadence_hours"] = n; _save(data)
        elif c == "b":
            tok = _prompt_choice("  brain 1=WORKHORSE 2=SPECIALIST 3=LIFELINE / b > ",
                                 {"1": "WORKHORSE", "2": "SPECIALIST", "3": "LIFELINE"})
            if tok:
                a["brain"] = BRAIN_NAMES[int(tok) - 1]; _save(data)
        elif c == "r":
            tok = _prompt_choice("  role 1=Solver 2=Architect 3=Crafter 4=Analyst 5=Communicator 6=Sentinel 7=Operator / b > ",
                                 {str(i+1): ROLE_NAMES[i] for i in range(len(ROLE_NAMES))})
            if tok:
                a["role"] = ROLE_NAMES[int(tok) - 1]; _save(data)

# ---- step 4: create agent (role dropdown + limit enforcement) ------------
def step_create(data):
    print("\n[Create Agent]")
    aid = _ask("  new agent id (a-z0-9_-): ").strip()
    if not aid or not all(x.isalnum() or x in "_-" for x in aid):
        print("  (invalid id - use letters/digits/_/-)"); return
    if aid in data["agents"]:
        print("  (id already exists)"); return
    div = _ask("  division (Enter=General): ").strip() or "General"
    tok = _prompt_choice("  role 1=Solver 2=Architect 3=Crafter 4=Analyst 5=Communicator 6=Sentinel 7=Operator / b > ",
                         {str(i+1): ROLE_NAMES[i] for i in range(len(ROLE_NAMES))})
    if tok is None:
        return
    role = ROLE_NAMES[int(tok) - 1]
    bv = _prompt_choice("  brain 1=WORKHORSE 2=SPECIALIST 3=LIFELINE / b > ",
                        {"1": "WORKHORSE", "2": "SPECIALIST", "3": "LIFELINE"})
    if bv is None:
        return
    brain = BRAIN_NAMES[int(bv) - 1]
    cad = _ask_int("  cadence hours (1-168, Enter=6): ", 1, 168) or 6
    auto = _ask_yes("  autonomous?")
    chain = data["brains"].get(brain, [])
    prov = chain[0]["provider"] if chain else "nvidia"
    allowed, reason = settings.check_per_provider(data, prov)
    if not allowed:
        print("  REFUSED (HARD limit): " + reason)
        print("  -> this is the feature working, not a bug.")
        return
    data["agents"][aid] = {
        "enabled": True, "autonomous": auto, "brain": brain, "role": role,
        "cadence_hours": cad, "division": div, "template_role": aid,
    }
    _save(data)
    _, warn = settings.check_total(data)
    if warn:
        print("  NOTE (SOFT limit): " + warn)
    print("  + agent '%s' created as %s on %s/%s" % (aid, role, prov, brain))

# ---- step 5: remove agent ------------------------------------------------
def step_remove(data):
    print("\n[Remove Agent]"); _agent_table(data)
    aid = _ask("  agent id to remove: ").strip()
    if aid in data["agents"]:
        if _ask_yes("  remove '%s'?" % aid):
            del data["agents"][aid]; _save(data); print("  - removed")
    else:
        print("  (no such agent)")

# ---- step 6: notifications ----------------------------------------------
def step_notif(data):
    n = data.setdefault("notifications", {})
    while True:
        print("\n[Notifications]")
        print("  severity_filter: " + ", ".join(n.get("severity_filter", [])))
        print("  quiet_hours_utc: " + str(n.get("quiet_hours_utc")))
        print("  telegram_deliver_seconds: " + str(n.get("telegram_deliver_seconds", 10)))
        c = _prompt_choice("  s)everity q)uiet t)elegram-sec / k > ",
                           {"s": "severity", "q": "quiet-hours", "t": "telegram-sec"},
                           back=("k", "b", ""))
        if c is None:
            return
        if c == "s":
            print("  toggle which (space-separate): i)nfo w)arn c)rit")
            raw = _ask("  > ").strip().lower()
            cur = set(n.get("severity_filter", []))
            mp = {"i": "info", "w": "warn", "c": "crit"}
            for tk in raw.replace(",", " ").split():
                if tk in mp:
                    lvl = mp[tk]
                    cur.discard(lvl) if lvl in cur else cur.add(lvl)
            n["severity_filter"] = [x for x in ["info", "warn", "crit"] if x in cur]
            _save(data)
        elif c == "q":
            v = _ask("  quiet hours 'HH-HH' (Enter=none): ").strip()
            n["quiet_hours_utc"] = v if v and "-" in v else None; _save(data)
        elif c == "t":
            v = _ask_int("  deliver seconds (1-60): ", 1, 60)
            if v:
                n["telegram_deliver_seconds"] = v; _save(data)

# ---- step 7: reset ------------------------------------------------------
def step_reset(data):
    print("\n[Reset] restores Template #1 defaults for brains/agents/limits/notifications.")
    print("Your watched REPOS are KEPT. Backup -> settings.bak.<time>")
    if _ask("  type RESET to confirm: ").strip() != "RESET":
        print("  cancelled"); return
    import time
    bak = settings.SETTINGS_PATH.with_name("settings.bak." + str(int(time.time())))
    try:
        bak.write_text(settings.SETTINGS_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print("  backup -> " + bak.name)
    except Exception as e:
        print("  (backup skipped: %s)" % e)
    fresh = settings.defaults()
    fresh["repos"] = data.get("repos", fresh.get("repos", []))
    settings.save(fresh)
    print("  >> reset done (repos preserved)")

MENU = [
    ("1", "Repos", step_repos),
    ("2", "Brains (with model-type badges)", step_brains),
    ("3", "Agents (toggle / cadence / brain / role)", step_agents),
    ("4", "Create Agent (role dropdown) [HARD 10/API + SOFT 30]", step_create),
    ("5", "Remove Agent", step_remove),
    ("6", "Notifications", step_notif),
    ("7", "Reset to defaults (backup first)", step_reset),
]

def run():
    if len(sys.argv) > 1 and sys.argv[1] in ("selftest", "--selftest"):
        selftest(); return
    print("=" * 60)
    print(" STRATOFLY SETTINGS WIZARD v2 (schema %d, 7 roles)" % settings.SCHEMA)
    print("=" * 60)
    mkeys = {k for k, _l, _f in MENU}
    while True:
        data = settings.load()
        print("\nMain menu:")
        for k, label, _fn in MENU:
            print("  %s. %s" % (k, label))
        print("  0. quit (changes already saved per action)")
        while True:
            c = _ask("  > ").strip().lower()
            if c in ("0", "q"):
                print(" bye."); return
            if c in mkeys:
                break
            print("  (invalid. choose 1-7, or 0/q to quit)")
        fn = next(f for k, _l, f in MENU if k == c)
        fn(data)

def selftest():
    assert callable(_prompt_choice), "_prompt_choice missing"
    print("[selftest] roles:", ROLE_NAMES)
    print("[selftest] model_kind integration on suggested models:")
    for pv, md in SUGGEST:
        print("  " + _model_line(pv, md))
    print("[selftest] limit integration on current settings.json:")
    d = settings.load()
    print("  agents_per_provider:", settings.agents_per_provider(d))
    print("  check_per_provider(nvidia):", settings.check_per_provider(d, "nvidia"))
    print("  check_total:", settings.check_total(d))
    print("[selftest] OK - wizard v2 + roles + badges + limits all loaded.")

if __name__ == "__main__":
    run()
