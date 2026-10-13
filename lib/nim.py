from openai import OpenAI, APIStatusError
import config

_client = None
_works = None

FALLBACK_MODELS = [
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "meta/llama-3.1-70b-instruct",
    "qwen/qwen2.5-coder-32b-instruct",
    "deepseek-ai/deepseek-v3",
    "mistralai/mixtral-8x22b-instruct-v0.1",
]

def client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(base_url=config.NVIDIA_BASE_URL, api_key=config.NVIDIA_API_KEY)
    return _client

def list_models():
    return [m.id for m in client().models.list()]

def _remember(m: str):
    global _works
    _works = m
    try:
        from lib import envstore
        envstore.set_value("SCOUT_MODEL", m)
        config.SCOUT_MODEL = m
    except Exception:
        pass

def ask(model: str, system: str, user: str, temperature: float = 0.3) -> str:
    global _works
    chain = []
    for m in ([_works, model] + FALLBACK_MODELS):
        if m and m not in chain:
            chain.append(m)
    last_err = None
    for m in chain:
        try:
            resp = client().chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=1024,
            )
            if m != model:
                print(f"ℹ️  model {model} mati → otomatis pindah & mengingat: {m}")
                _remember(m)
            else:
                _works = m
            return resp.choices[0].message.content or ""
        except APIStatusError as e:
            last_err = e
            if e.status_code in (404, 410):
                continue
            raise
    raise RuntimeError(f"Semua model cadangan gagal. Terakhir: {last_err}. Jalankan: python main.py model")