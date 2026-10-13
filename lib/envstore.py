from config import BASE_DIR

ENV_PATH = BASE_DIR / ".env"

def read() -> dict:
    d = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d

def write(d: dict):
    ENV_PATH.write_text("\n".join(f"{k}={v}" for k, v in d.items()) + "\n", encoding="utf-8")

def set_value(key: str, value: str):
    d = read()
    d[key] = value
    write(d)