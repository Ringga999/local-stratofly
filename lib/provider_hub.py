from openai import OpenAI, APIStatusError
import config
from lib import memory

_clients = {}
RETRY_STATUS = (401, 402, 404, 410, 429, 500, 502, 503, 504)

def _client(provider: str) -> OpenAI:
    if provider not in _clients:
        info = config.PROVIDERS[provider]
        _clients[provider] = OpenAI(base_url=info["base_url"],
                                    api_key=config.provider_key(provider))
    return _clients[provider]

def available_providers():
    return [p for p in config.PROVIDERS if config.provider_key(p)]

def _chain(brain: str):
    chain = list(config.BRAINS.get(brain, config.BRAINS[config.DEFAULT_BRAIN]))
    last = memory.get_kv("brain_last_" + brain)
    if last:
        try:
            prov, model = last.split("|", 1)
            pair = (prov, model)
            if pair in chain:
                chain.remove(pair)
                chain.insert(0, pair)
        except Exception:
            pass
    for p in available_providers():
        pair = (p, config.HOUSE_MODELS[p])
        if pair not in chain:
            chain.append(pair)
    return chain

def _notify_fallback(agent_id, brain, failed, used):
    title = "Provider Fallback Triggered"
    body = (f"{agent_id or 'hub'} attempted brain {brain} via {failed[0]}/{failed[1]}, "
            f"but it was unavailable. Automatically switched to {used[0]}/{used[1]}. "
            f"Operation continues normally.")
    memory.add_notification("warn", title, body)
    memory.log_event(agent_id or "hub", "alert", "provider_fallback",
                     f"{failed[0]}->{used[0]}", body[:80])

def think(brain: str, system: str, user: str, agent_id=None, temperature: float = 0.3) -> str:
    chain = _chain(brain)
    last_err = None
    failed_pair = None
    for prov, model in chain:
        if not config.provider_key(prov):
            continue
        try:
            resp = _client(prov).chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
                temperature=temperature,
                max_tokens=1024,
            )
            text = resp.choices[0].message.content or ""
            memory.set_kv("brain_last_" + brain, f"{prov}|{model}")
            if failed_pair is not None:
                _notify_fallback(agent_id, brain, failed_pair, (prov, model))
            return text
        except APIStatusError as e:
            last_err = e
            failed_pair = (prov, model)
            if e.status_code in RETRY_STATUS:
                continue
            raise
        except Exception as e:
            last_err = e
            failed_pair = (prov, model)
            continue
    raise RuntimeError(f"All providers failed for brain {brain}. Last error: {last_err}")

def describe():
    out = []
    for name, chain in config.BRAINS.items():
        lines = []
        for prov, model in chain:
            ok = bool(config.provider_key(prov))
            lines.append(f"   - {prov}/{model} [{'key OK' if ok else 'no key'}]")
        out.append((name, lines))
    return out