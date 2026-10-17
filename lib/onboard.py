import webbrowser
from config import BASE_DIR

ENV_PATH = BASE_DIR / ".env"

def _read_env() -> dict:
    d = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d

def _write_env(d: dict):
    ENV_PATH.write_text("\n".join(f"{k}={v}" for k, v in d.items()) + "\n", encoding="utf-8")

def ensure_nvidia(d: dict) -> dict:
    if d.get("NVIDIA_API_KEY"):
        return d
    print("\n🧠 BRAIN: I need an NVIDIA NIM key to think (temporary default).")
    print("   Opening the key page in your browser…")
    webbrowser.open("https://build.nvidia.com/settings/api-keys")
    print("   (Login → Generate API Key → copy)")
    key = input("   Paste the key (nvapi-…) here, then Enter: ").strip()
    if not key:
        raise SystemExit("❌ Empty key — run again: python main.py setup")
    d["NVIDIA_API_KEY"] = key
    return d

def ensure_repos(d: dict) -> dict:
    if d.get("REPOS"):
        return d
    default = "Ringga999/zcp2o-protocol,Ringga999/notapeer-app"
    ans = input(f"\n📚 REPOS I maintain [Enter = {default}]: ").strip()
    d["REPOS"] = ans or default
    return d

def run():
    d = _read_env()
    d = ensure_nvidia(d)
    d = ensure_repos(d)
    _write_env(d)
    print("\n🔗 GITHUB: tokenless mode for now → public repos readable.")
    print("   For private repos later: `gh auth login` — one approve click.")
    print("   Optional provider keys later: GROQ_API_KEY, OPENROUTER_API_KEY, …")
    print("\n✅ .env written by the body itself. Organs acquired.")