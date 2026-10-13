from config import PERSONAS_DIR

def load(agent_id: str) -> str:
    return (PERSONAS_DIR / f"{agent_id}.md").read_text(encoding="utf-8")

def system_prompt(agent_id: str, extra: str) -> str:
    return load(agent_id) + "\n\n---\n\n# ATURAN EKOSISTEM TAMBAHAN (WAJIB)\n" + extra