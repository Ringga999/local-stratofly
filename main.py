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
    config.SCOUT_MODEL = os.getenv("SCOUT_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")

def preflight() -> bool:
    from config import NVIDIA_API_KEY, REPOS
    from lib import gh
    ok = True
    if not NVIDIA_API_KEY:
        print("❌ NVIDIA_API_KEY kosong — jalankan: python main.py setup"); ok = False
    if not REPOS:
        print("❌ REPOS kosong — jalankan: python main.py setup"); ok = False
    mode = gh.token_mode()
    if mode == "anon":
        print("ℹ️  GitHub: mode tanpa-token → repo PUBLIK terbaca (cukup untuk mulai)")
    else:
        print(f"✅ GitHub: mode {mode} → repo privat & aksi tulis tersedia")
    if ok:
        print("✅ Preflight lolos")
    return ok

def _pick_model():
    from lib import nim, envstore
    import config as cfg
    cur = cfg.SCOUT_MODEL
    print(f"🧠 Model aktif: {cur}")
    print("   Mengambil katalog hidup dari NVIDIA…")
    ids = sorted(nim.list_models())
    pref = [i for i in ids if any(k in i for k in ("instruct", "chat", "r1", "v3", "70b", "32b"))]
    pref = [i for i in pref if i != cur][:14]
    print("   [0] pertahankan model aktif")
    for n, i in enumerate(pref, 1):
        print(f"   [{n}] {i}")
    choice = input("   Pilih nomor: ").strip()
    if choice in ("", "0"):
        print("   Model tidak diubah."); return
    try:
        pick = pref[int(choice) - 1]
    except Exception:
        print("   Pilihan tidak sah."); return
    envstore.set_value("SCOUT_MODEL", pick)
    cfg.SCOUT_MODEL = pick
    print(f"✅ Model aktif kini: {pick}  (ditulis tubuh sendiri ke .env)")

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
        print("🌱 Pertama kali hidup — saya akan meminta akses yang saya butuhkan…")
        from lib import onboard
        onboard.run()
        _reload_env()
    if cmd == "preflight":
        raise SystemExit(0 if preflight() else 1)
    if cmd == "patrol":
        if not preflight():
            raise SystemExit(1)
        from agents import scout
        print("🕵️ Scout memulai patroli...")
        print()
        print(scout.patrol())