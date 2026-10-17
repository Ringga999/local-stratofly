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
    print("   To add a provider later: put its key in .env")
    print("   (GROQ_API_KEY, OPENROUTER_API_KEY, DEEPSEEK_API_KEY, MISTRAL_API_KEY)")
    print("   then restart. The hub picks it up automatically.")

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