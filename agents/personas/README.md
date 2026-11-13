\# Agent Personas (per-agent, runtime)



The `.md` files in this folder are the \*\*runtime personas of the default crew\*\*

(scout, triage, sentinel, scribe, tester, medic, release, bridge, herald, diplomat).

`lib/persona.py` loads `<agent\_id>.md` from here for any agent whose role has no

persona in the registry.



\## Precedence (highest first)



1\. `roles/<role>.json` → `persona` field (role-level, data-driven)

2\. `agents/personas/<agent\_id>.md` (this folder; per-agent narrative)

3\. Fallback inside `lib/persona.py` (see its source)



Consequence to remember: when a role gains a `persona` in `roles/\*.json`, that

persona overrides the per-agent `.md` of every agent holding that role.

Intentional today; scheduled for unification in blueprint cell `role-consolidation`.



\## Editing rules



\- One coherent voice per file: duties, boundaries, approval rules.

\- These files enter every prompt of their agent — brevity is kindness (token cost).

\- No secrets, no machine-specific paths; they ship with the repo.

