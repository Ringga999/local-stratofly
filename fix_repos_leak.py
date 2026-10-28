# fix_repos_leak.py - one-shot: remove PRIVATE repo names from the web UI by
# normalizing settings.json["repos"] to a PUBLIC-neutral list. Touches ONLY
# settings.json (data), NOT any .py engine file -> Monday stays frozen.
# Why: WATCHED REPOS panel was rendering literal private-ecosystem names
# (leaked via onboard.py default). They do NOT reach GitHub (settings.json is
# git-ignored) but they DO reach the screen / screenshots / Monday stage, which
# violates our alias doctrine. Fix = replace the whole list with safe public
# repos. Edit REPOS_NETRAL below if you prefer different public targets.
from pathlib import Path
import sys, json, shutil

B = Path(__file__).resolve().parent
SET = B / "settings.json"
BAK = B / "settings.json.bak.reposfix"

# >>> EDIT THIS LIST if you want different PUBLIC repos for the demo <<<
# These are safe to show on stage. local-stratofly is our own public engine,
# so patrol against it is honest AND impressive (jury can open the same repo).
REPOS_NETRAL = [
    "Ringga999/local-stratofly",
]

print("=" * 70)
print(" NORMALIZE WATCHED REPOS (strip private names from web UI)")
print("=" * 70)

if not SET.exists():
    print("  settings.json NOT FOUND - abort (run setup first?)"); sys.exit(1)

shutil.copyfile(SET, BAK)
print("  OK backed up settings.json -> settings.json.bak.reposfix")

d = json.loads(SET.read_text(encoding="utf-8"))
old = d.get("repos", [])
print("  OLD repos (private leak):")
for r in old:
    print("     - " + str(r))

# Mechanical guard: refuse to KEEP any entry that smells private.
PRIVATE_MARKERS = ["zcp2o", "notapeer"]
still_private = [r for r in REPOS_NETRAL if any(m in str(r).lower() for m in PRIVATE_MARKERS)]
if still_private:
    print("  ABORT: REPOS_NETRAL itself contains private markers:", still_private); sys.exit(1)

d["repos"] = list(REPOS_NETRAL)
SET.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print("  NEW repos (public-neutral, safe for stage):")
for r in d["repos"]:
    print("     + " + r)

# Verify on disk: no private marker remains anywhere in the repos field.
chk = json.loads(SET.read_text(encoding="utf-8")).get("repos", [])
leak = [r for r in chk if any(m in str(r).lower() for m in PRIVATE_MARKERS)]
print("  post-write leak scan on repos:", "CLEAN" if not leak else ("STILL LEAKING: " + str(leak)))

print("\n" + "=" * 70)
print(" DONE." if not leak else " DONE (LEAK REMAINS - check REPOS_NETRAL)")
print(" Restart server (Ctrl+C then: python main.py serve) and refresh web.")
print(" WATCHED REPOS panel will now show ONLY the public-neutral list.")
print(" Note: activity feed may still show old 'not implemented yet' rows from")
print("       historical memory events; they are NOT secret and will be pushed")
print("       out by fresh patrol/mock events during the demo. Ignore for now.")
print(" Cleanup after verify:   del fix_repos_leak.py")
print(" Restore point if needed: copy settings.json.bak.reposfix over settings.json")
print("=" * 70)