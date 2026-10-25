# recon_ask.py - READ-ONLY map of the agent-task machinery.
# Uses ast (static parse) ONLY: does NOT import, execute, write, or touch
# main.py / .env / gitignore. Cannot crash your engine. Prints the function
# signatures patrol would use, so the next step (the 'ask' router) is built
# on verified green code, not a guess. Save as recon_ask.py in ROOT, run once.
import ast, re
from pathlib import Path

B = Path(__file__).resolve().parent

def funcs_of(path):
    """Return list of (name, args, lineno) for top-level + nested defs/classes."""
    out = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return [("<<SYNTAX ERROR>>", str(e), 0)]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            names = [x.arg for x in a.posonlyargs + a.args]
            if a.vararg: names.append("*" + a.vararg.arg)
            if a.kwarg: names.append("**" + a.kwarg.arg)
            out.append((node.name, "(" + ", ".join(names) + ")", node.lineno))
    return out

print("=" * 66)
print(" READ-ONLY RECON for the 'ask' router (no code executed, no files written)")
print("=" * 66)

# 1) main.py: every function, and the verbatim body of the patrol branch
mp = B / "main.py"
print("\n[main.py] functions defined:")
for n, s, l in funcs_of(mp):
    print("   line %-4d %s%s" % (l, n, s))
msrc = mp.read_text(encoding="utf-8")
print("\n[main.py] lines mentioning patrol / agent / prompt / run / hub:")
for i, ln in enumerate(msrc.splitlines(), 1):
    if re.search(r"patrol|agent|prompt|def run|hub|dispatch|cmd ==", ln, re.I):
        print("   %4d | %s" % (i, ln.rstrip()))

# 2) lib/: every module, its functions, and any signature carrying 'prompt'
lib = B / "lib"
print("\n[lib/] modules and their functions:")
if lib.exists():
    for py in sorted(lib.glob("*.py")):
        fs = funcs_of(py)
        head = fs[0][0] if fs and fs[0][0].startswith("<<") else None
        print("   -- %s%s" % (py.name, "  (" + head + ")" if head else ""))
        for n, s, l in fs:
            mark = "  <== PROMPT-ARG" if "prompt" in s.lower() or "task" in s.lower() or "msg" in s.lower() or "text" in s.lower() else ""
            print("        line %-4d %s%s%s" % (l, n, s, mark))
else:
    print("   lib/ NOT FOUND")

# 3) the verdict line we need for 'ask'
print("\n" + "=" * 66)
print(" VERDICT for building 'ask' (read this, then send screenshot):")
print("  - If you see a function like run_agent(id, prompt) / handle(prompt)")
print("    / dispatch(cmd, args) with a prompt-ish arg  -> 'ask' = thin router,")
print("    calls that function with your argv. GREEN, no adapter.")
print("  - If patrol's prompt is hardcoded inside a no-arg function")
print("    (e.g. patrol() with no prompt param)          -> 'ask' needs a small")
print("    adapter that builds the prompt from argv. Still safe, just +1 fn.")
print("  - Either way main.py stays UNTOUCHED until we see this output.")
print("=" * 66)