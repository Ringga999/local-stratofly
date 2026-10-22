# lib/model_kind.py - heuristic model-type detector (Stratofly).
# Why: today a VISION model was chosen for a TEXT agent and the triage table
# never appeared. This module lets every door (catalog, wizard, hub) know WHAT
# KIND a model is BEFORE it is trusted with a task. English strings only.
# Heuristic = fast, offline, zero-dependency. The long-term truth lives in the
# live recipe manifest (RECIPE-SPEC, Phase 12); this is the safety net that
# makes the demo immune to the exact failure we hit today.

_VISION = ("vision", "-vl", "vl-", "llava", "moondream", "pixtral", "image")
_AUDIO  = ("audio", "whisper", "asr", "tts", "speech", "sonar")
_REASON = ("reasoning", "thinker", "thinking", "-r1", "qwq", "nemotron")
_CODER  = ("coder", "codestral", "codegen", "starcoder", "codellama",
           "swe-", "code-instruct", "code-")

def classify(model_id):
    m = (model_id or "").lower()
    if any(k in m for k in _VISION):
        return "vision"
    if any(k in m for k in _AUDIO):
        return "audio"
    if any(k in m for k in _REASON):
        return "reasoning"
    if any(k in m for k in _CODER):
        return "coder"
    return "text"

def badge(model_id):
    # Short tag for catalog rows: "  [vision]". Empty for plain text models.
    k = classify(model_id)
    return "" if k == "text" else "  [" + k + "]"

def is_safe_for_text(model_id):
    # All Template #1 agents are TEXT workers. Vision/audio models cannot
    # reliably answer a text prompt, so they are NOT safe for these agents.
    k = classify(model_id)
    return (k not in ("vision", "audio")), k

def explain(kind):
    # Polite English guidance the wizard (Friday) will show on a risky pick.
    return {
        "vision":   "This looks like a VISION model (image input). Text agents "
                    "like scout/triage need a TEXT model - picking this may "
                    "produce empty answers.",
        "audio":    "This looks like an AUDIO model (speech input). It is not "
                    "suitable for text agents.",
        "reasoning":"This is a REASONING model. It works for text, but may place "
                    "its answer in a reasoning field; the hub already handles "
                    "that. Expect slower, deeper replies.",
        "coder":    "This is a CODER model. Great for engineering agents "
                    "(scout/triage/tester/bridge); less ideal for social/content "
                    "agents.",
        "text":     "General TEXT model - safe default for every agent.",
    }.get(kind, "Unknown model type - treat as text, verify on first patrol.")
