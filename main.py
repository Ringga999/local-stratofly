import os, sys, threading

def _needs_onboard() -> bool:
    from config import NVIDIA_API_KEY, REPOS
    return not NVIDIA_API_KEY or not REPOS

def _reload_env():
    from dotenv import load_dotenv
    import config
    load_dotenv(override=True)
    config.NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
    config.REPOS = [r.strip() for r in os.getenv("REPOS", "").split(",") if r.strip()]

def preflight() -> bool:
    from config import NVIDIA_API_KEY, REPOS
    from lib import gh, provider_hub
    ok = True
    if not NVIDIA_API_KEY:
        print("❌ NVIDIA_API_KEY missing — run: python main.py setup"); ok = False
    if not REPOS:
        print("❌ REPOS missing — run: python main.py setup"); ok = False
    mode = gh.token_mode()
    if mode == "anon":
        print("ℹ️  GitHub: tokenless mode → PUBLIC repos readable (enough to start)")
    else:
        print(f"✅ GitHub: mode {mode} → private repos & write actions available")
    avail = provider_hub.available_providers()
    print(f"🧠 Providers with keys: {', '.join(avail) if avail else 'none'}")
    if ok:
        print("✅ Preflight passed")
    return ok

def _show_brains():
    from lib import provider_hub
    print("🧠 PROVIDER HUB — brains and priorities")
    avail = provider_hub.available_providers()
    print(f"   Providers with keys: {', '.join(avail) if avail else 'none'}")
    for name, lines in provider_hub.describe():
        print(f"   [{name}]")
        for ln in lines:
            print(ln)
    print()
    print("   Change a brain with: python main.py model")
    print("   Add a provider later: put its key in .env and restart.")

def _pick_model():
    from lib import provider_hub
    import config as cfg
    brains = list(cfg.BRAINS.keys())
    print("🧠 Which brain do you want to rewire?")
    for n, b in enumerate(brains, 1):
        first = cfg.BRAINS[b][0] if cfg.BRAINS[b] else ("-", "-")
        print(f"   [{n}] {b}  (now: {first[0]}/{first[1]})")
    choice = input("   Pick number: ").strip()
    try:
        brain = brains[int(choice) - 1]
    except Exception:
        print("   Invalid choice."); return
    provs = provider_hub.available_providers()
    if not provs:
        print("   No provider keys found."); return
    print("   Which provider?")
    for n, p in enumerate(provs, 1):
        print(f"   [{n}] {p}")
    choice = input("   Pick number: ").strip()
    try:
        prov = provs[int(choice) - 1]
    except Exception:
        print("   Invalid choice."); return
    print(f"   Fetching live model catalog from {prov}…")
    ids = provider_hub.list_models(prov)
    if not ids:
        custom = input("   Catalog unavailable. Type model id manually: ").strip()
        if custom:
            provider_hub.set_brain_first(brain, prov, custom)
            print(f"✅ {brain} now starts with {prov}/{custom}")
        return
    pref = [i for i in ids if any(k in i for k in
            ("instruct", "chat", "pro", "max", "large", "r1", "v3", "nemotron"))]
    pref = (pref or ids)[:14]
    print("   [0] type a custom model id instead")
    for n, i in enumerate(pref, 1):
        print(f"   [{n}] {i}")
    choice = input("   Pick number: ").strip()
    if choice == "0":
        custom = input("   Type model id: ").strip()
        if custom:
            provider_hub.set_brain_first(brain, prov, custom)
            print(f"✅ {brain} now starts with {prov}/{custom}")
        return
    try:
        model = pref[int(choice) - 1]
    except Exception:
        print("   Invalid choice."); return
    provider_hub.set_brain_first(brain, prov, model)
    print(f"✅ {brain} now starts with {prov}/{model}  (written to .env by the body itself)")

def _serve():
    from lib import api_server
    api_server.run()

def _mock():
    from lib import mock
    mock.run()

def _schedule():
    from lib import scheduler
    scheduler.run_daemon()

def _all():
    from lib import api_server, scheduler
    threading.Thread(target=api_server.run, daemon=True).start()
    scheduler.run_daemon()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "patrol"
    if cmd == "setup":
        from lib import onboard
        onboard.run()
        raise SystemExit(0)
    if cmd == "brains":
        _show_brains()
        raise SystemExit(0)
    elif cmd == "web":
        from lib.web import serve as _ws; _ws()
    elif cmd == "settings":
        from lib.wizard import run as _rs; _rs()
    if cmd == "model":
        _pick_model()
        raise SystemExit(0)
    if cmd == "serve":
        _serve()
        raise SystemExit(0)
    if cmd == "mock":
        _mock()
        raise SystemExit(0)
    if cmd == "schedule":
        _schedule()
        raise SystemExit(0)
    if cmd == "all":
        _all()
        raise SystemExit(0)
    if cmd == "telegram":
        from lib import telegram_gateway
        telegram_gateway.run()
        raise SystemExit(0)
    if _needs_onboard():
        print("🌱 First boot — I will ask for the access I need…")
        from lib import onboard
        onboard.run()
        _reload_env()
    if cmd == "preflight":
        raise SystemExit(0 if preflight() else 1)
    if cmd == "patrol":
        if not preflight():
            raise SystemExit(1)
        from agents import scout
        print("🕵️ Scout starting patrol...")
        print()
        print(scout.patrol())