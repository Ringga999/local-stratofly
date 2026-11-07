# lib/ask_handler.py - free-form prompt router.
# Routes a free-form prompt to provider_hub.think using the target agent's
# persona and brain chain. Minimal on purpose: read config, build persona,
# think, log one memory event, return the answer string.
from lib import memory, persona, provider_hub, settings


def ask(prompt, agent_id="scout"):
    prompt = (prompt or "").strip()
    if not prompt:
        raise ValueError("empty prompt")
    cfg = settings.load()
    a = (cfg.get("agents") or {}).get(agent_id) or {}
    brain = a.get("brain", "WORKHORSE")
    sys_p = persona.system_prompt(agent_id, extra="")
    ans = provider_hub.think(
        brain=brain,
        system=sys_p,
        user=prompt,
        agent_id=agent_id,
        temperature=0.6,
        max_tokens=1024,
    )
    try:
        memory.log_event(agent_id, "working", "ask", "-", prompt[:48], -1)
    except Exception:
        pass
    return ans or ""
