# recon_server.py - READ-ONLY. Prints the RAW SOURCE of the three files that
# decide how the full localhost app must be assembled: api_server.py (the
# EXISTING server we must unify into, not duplicate), onboard.py (API-input
# flow), mock.py (offline guarantee). Also lists every file in lib/ so we know
# no fourth server hides there. Uses plain file reads ONLY: no import, no exec,
# no write, no network, no git. Cannot touch main.py or your engine.
from pathlib import Path

B = Path(__file__).resolve().parent
LIB = B / "lib"

def dump(rel):
    p = B / rel
    print("\n" + "=" * 70)
    print(" RAW SOURCE :: " + rel)
    print("=" * 70)
    if not p.exists():
        print("  <<FILE NOT FOUND>>")
        return
    txt = p.read_text(encoding="utf-8", errors="replace")
    for i, ln in enumerate(txt.splitlines(), 1):
        print("  %3d | %s" % (i, ln.rstrip()))

# 1) the existing server we must unify INTO
dump("lib/api_server.py")
# 2) the API-input / onboarding flow
dump("lib/onboard.py")
# 3) the offline demo guarantee
dump("lib/mock.py")

# 4) make sure no other server / entrypoint hides in lib/
print("\n" + "=" * 70)
print(" lib/ INVENTORY (watch for any OTHER server/entrypoint file)")
print("=" * 70)
if LIB.exists():
    for f in sorted(LIB.glob("*.py")):
        head = ""
        try:
            first = f.read_text(encoding="utf-8", errors="replace").splitlines()
            head = first[0][:60] if first else ""
        except Exception as e:
            head = "<<unreadable: %s>>" % e
        print("  %-22s %s" % (f.name, head))
else:
    print("  lib/ NOT FOUND")

print("\n" + "=" * 70)
print(" END OF READ-ONLY RECON. Nothing was written or executed.")
print(" Next step (after you send this): ONE installer that builds the full")
print(" localhost app ON TOP OF api_server.py - unify, never duplicate.")
print("=" * 70)