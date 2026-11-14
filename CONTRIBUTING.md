\# Contributing to Stratofly



Thank you for considering a contribution. Stratofly is an engine in alpha: the core (role registry, brain chains, local memory, Solver orchestration, optional on-chain anchoring) is live; much per-role capability is still open ground. This guide tells you exactly how we work, so your first PR lands cleanly.



\## Before you write code: our six doctrines



These are not slogans; each was paid for by a real incident.



1\. \*\*Push or it didn't happen.\*\* A commit that never reached origin is a local rumor. Every "done" ends with a push.

2\. \*\*Your eyes are the gate.\*\* Run `python main.py serve`, open `http://localhost:8765`, and look. Installer output saying "OK" is not proof; a screenshot of the working UI is.

3\. \*\*Additive over destructive.\*\* Prefer new files and new endpoints over moving or rewriting engine code. When you must patch, use verified anchors, keep a backup, and abort cleanly if an anchor is missing.

4\. \*\*Secrets never enter git.\*\* `.env`, `settings.json`, and `memory.sqlite3` are gitignored forever. After touching config, run `git status` and expect clean. Before adding any `.gitignore` pattern, check it swallows nothing you need: `git check-ignore -v <file>`.

5\. \*\*Verify the simple thing first.\*\* Before building a complex theory, ask: is it pushed? does the file exist on origin? is the venv activated? is the key prefixed `0x`? Most of our worst hours were one-line answers.

6\. \*\*Discuss engine changes before coding.\*\* For non-trivial changes to `lib/\*.py` or `lib/app.html`, open an issue first. Small, reviewable PRs beat heroic diffs.



\## Setup



```bash

git clone https://github.com/Ringga999/local-stratofly.git

cd local-stratofly

python -m venv venv

venv\\Scripts\\activate        # Windows

\# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt

python main.py serve

```



Open `http://localhost:8765`. No API key is needed to explore; use \*\*Mock\*\* mode for demos. Details, OneDrive quirks, and configuration live in `docs/INSTALL.md`.



\## Repo map



| Path | What lives there |

|---|---|

| `main.py` | Entrypoint (`serve`, and friends) |

| `lib/api\_server.py` | HTTP control room + all `/api/\*` endpoints |

| `lib/settings.py` | Config load/save, defaults, limits |

| `lib/memory.py` | SQLite event log \& agent state (the local truth) |

| `lib/scheduler.py` | Autonomous patrol loop |

| `lib/persona.py` | Base role personas |

| `lib/provider\_hub.py` | 3-tier brain chains (WORKHORSE/SPECIALIST/LIFELINE) |

| `lib/ask\_handler.py` | Free-form prompt router |

| `lib/chain\_relay.py` | Optional on-chain anchoring (hybrid mode) |

| `lib/role\_registry.py` | Data-driven roles + recall injection into prompts |

| `lib/plugin\_manager.py` | Plugin catalog + per-agent skill packs |

| `lib/app.html` | The whole control room UI (single file, vanilla JS) |

| `roles/\*.json` | Role definitions: persona, capabilities, tools, modules |

| `plugins/registry.json` | Plugin catalog (prompt-packs + repo links) |

| `agents/personas/*.md` | Runtime per-agent personas for the default crew (loaded by `lib/persona.py`) |

| `docs/` | Specs, blueprints, INSTALL |
Persona precedence (highest first): `roles/<role>.json` persona → `agents/personas/<agent_id>.md` → `lib/persona.py` fallback. Details in `agents/personas/README.md`.



\## Picking work



Start at \*\*`docs/ROLE-MODULES-BLUEPRINT.md`\*\*: ten roles × their modules, each cell marked `planned`, `partial`, or `done`. Pick one `planned` cell, announce it (issue or PR description) so nobody doubles up, and branch as:



```

feature/<role>-<module>     e.g. feature/crafter-code-diff

```



One cell per PR. The blueprint also lists, per module: definition, endpoint, UI state — your spec is already written.



\## Adding a role (data, not code)



1\. Copy `roles/\_TEMPLATE.json` to `roles/<yourrole>.json`.

2\. Fill `name`, `division`, `capabilities`, `tools`, `privileges`, `modules`, `preferred\_kinds`, and a `persona` that states duties, boundaries, and approval rules.

3\. Restart the server. The Add-Agent dropdown and `/api/roles` pick it up automatically — no engine edit needed.

4\. Optional: give its modules pretty names in `lib/app.html` (`moduleLabels`).

5\. If the role appears in the blueprint, update its rows in the same PR.



\## Adding a plugin



Add one entry to `plugins/registry.json`:



```json

{"id": "mytool", "name": "My Tool", "repo": "https://github.com/owner/repo",

&#x20;"status": "cataloged", "category": "coding", "roles": \["Crafter"],

&#x20;"prompt\_pack": "One or two sentences of discipline the agent should follow.",

&#x20;"notes": "what it is, in a phrase"}

```



Rules:

\- \*\*Prompt-packs only.\*\* Plugins shape personas; they never execute third-party code. Execution adapters are separate, reviewed work.

\- \*\*Never guess a repo URL.\*\* Verify it opens, or mark `"status": "link-pending"` with an empty `repo`.

\- Statuses: `link-pending` → `user-provided` → `cataloged`.

\- Enable per agent via the Plugins card in the UI (or `POST /api/plugins/toggle`).



\## Changing the engine



\- Patch via a throwaway script with \*\*verified anchors\*\*: read the file, assert the anchor exists, replace once, `ast.parse` (Python) or a quote-balance sanity check (JS), write. Keep a `.bak`, delete the script afterwards (`install\_\*` / `fix\_\*` names are gitignored by design).

\- In `lib/app.html`, remember: the UI is one giant script. A single missing quote inside a string literal kills every card on the page. When the UI dies wholesale, open \*\*F12 → Console\*\* before theorizing.

\- New endpoints are additive; document them in the relevant `docs/` spec in the same PR.



\## Memory, chain, and keys



\- `memory.sqlite3` is the local source of truth and never leaves the machine.

\- Hybrid mode anchors SHA-256 hashes to Sepolia. \*\*Testnet keys only, ever.\*\* Use keyed RPC endpoints (Infura/Alchemy); public anonymous RPCs get rate-limited.

\- `memory\_recall\_k` (settings) controls how many recent events enter an agent's prompt; `0` disables recall.

\- If anchoring fails, local memory keeps working. Never "fix" chain issues by weakening local-first.



\## Commit \& PR checklist



\- Messages: `feat(scope): ...`, `fix(scope): ...`, `docs: ...` — the scope is the module or role.

\- Before opening the PR:

&#x20; - \[ ] server runs and the change is verified by your own eyes

&#x20; - \[ ] clean-clone test passes if you touched engine code

&#x20; - \[ ] `git status` shows no secrets

&#x20; - \[ ] blueprint/spec statuses updated where relevant

&#x20; - \[ ] pushed (doctrine 1)

\- PR description: what, why, and \*\*how you tested\*\* — paste your gate output or screenshot. Reviewers reproduce it.



\## Definition of done



Works in the UI or API by your own eyes · pushed · documented · no secrets · no dead links · a reviewer reproduced your gate.



\## Questions



Open an issue, or write to \*\*1045weeks@gmail.com\*\*. Collaboration, mentorship, and strange ideas welcome.


## File Permission Matrix

What the team may create / modify / delete, and where review is required.

| Path | Create | Modify | Delete | Review |
|---|---|---|---|---|
| `lib/*.py` (engine core) | ❌ | ⚠️ verified-anchor patch + PR only | ❌ | Maintainer |
| `lib/app.html` (UI) | ❌ | ⚠️ additive sections + PR | ❌ | Maintainer |
| `roles/*.json` | ✅ | ✅ | ⚠️ only if unused | Self + PR |
| `plugins/registry.json` | ✅ entries | ✅ entries | ⚠️ | Self + PR |
| `agents/personas/*.md` | ✅ | ✅ | ⚠️ | Self + PR |
| `docs/**` | ✅ | ✅ | ⚠️ | Self + PR |
| `contracts/*.sol` | ❌ | ⚠️ redeploy + verify + PR | ❌ | Maintainer |
| `.env`, `settings.json`, `memory.sqlite3` | local only | local only | local only | NEVER commit |

Legend: ✅ allowed via PR · ⚠️ allowed with extra gate · ❌ not allowed.

## Change Procedure (every contribution)

1. Pick one `planned` cell in `docs/ROLE-MODULES-BLUEPRINT.md`; comment on the issue/PR to claim it.
2. Branch `feature/<role>-<module>`.
3. Build additively; never move or delete engine files.
4. Gate: `python main.py serve` + verify with your own eyes + clean-clone test for engine changes.
5. The PR flips the blueprint cell to `done` in the same PR.
6. Never commit `.env`, `settings.json`, `memory.sqlite3`.

## AI-Assisted Development Protocol

Using AI (chat assistants / codegen) is encouraged, under these rules:

1. **Feed raw, not rendered.** Paste file contents from disk / raw view, never from a rendered page (rendered copies carry escape artifacts like `\_`, `\#`, `&#x20;`).
2. **Verified anchors.** Any AI-generated patch must target an exact, currently-present anchor string; abort if missing; keep a `.bak` backup; never blind-replace.
3. **Don't trust AI memory.** AI may misremember versions, hashes, APIs. Verify against the live source / dropdown / endpoint before acting.
4. **Gates are human.** AI output is a proposal; a human runs the server, looks at UI/terminal, and confirms behavior before commit.
5. **Secrets never enter AI chat.** No `.env` values, tokens, or keys in prompts or screenshots; mask them.
6. **One cell per PR.** Keep AI-generated changes scoped to a single blueprint cell so review stays tractable.
7. **Record the doctrine.** If a session produces a new lesson, add it to the journal / CONTRIBUTING so the team inherits it.