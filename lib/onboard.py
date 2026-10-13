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
    print("\n🧠 OTAK: saya butuh kunci NVIDIA NIM untuk bisa berpikir.")
    print("   Membuka halaman pembuatan kunci di browser Anda…")
    webbrowser.open("https://build.nvidia.com/settings/api-keys")
    print("   (Login → Generate API Key → copy)")
    key = input("   Tempel kunci (nvapi-…) di sini, lalu Enter: ").strip()
    if not key:
        raise SystemExit("❌ Kunci kosong — ulangi: python main.py setup")
    d["NVIDIA_API_KEY"] = key
    return d

def ensure_repos(d: dict) -> dict:
    if d.get("REPOS"):
        return d
    default = "Ringga999/zcp2o-protocol,Ringga999/notapeer-app"
    ans = input(f"\n📚 REPO yang saya rawat [Enter = {default}]: ").strip()
    d["REPOS"] = ans or default
    return d

def run():
    d = _read_env()
    d = ensure_nvidia(d)
    d = ensure_repos(d)
    _write_env(d)
    print("\n🔗 GITHUB: saat ini mode tanpa-token → repo publik terbaca.")
    print("   Bila nanti butuh repo privat: `gh auth login` — satu klik approve.")
    print("\n✅ .env saya tulis sendiri. Tubuh saya kini punya organ yang ia minta.")