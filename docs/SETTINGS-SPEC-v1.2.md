# SETTINGS-SPEC v1.2 - Stratofly Instance Settings Contract

Version: 1.2 | Date: 24 October 2026 | Status: ACTIVE (replaces v1.1)
Owners: Mr Architect & Mr Visioner
Source of truth: this document. Changes MUST bump settings_schema and the
document version together.

IMPORTANT - spec leads code: this document targets settings_schema = 3. The
constant SCHEMA in lib/settings.py stays at 2 until the role + memory fields
are actually implemented (milestone S5). Until that commit, real files remain
schema 2 and the loader remains schema 2 - consistent. Do not bump the code
constant before the fields it promises exist.

## 0. What changed from v1.1 (read first)

v1.1 introduced the explicit agent registry with division + autonomy +
hard/soft limits. v1.2 adds two orthogonal ideas discussed at the drawing
table on 24 Oct 2026:

1. ROLE - a capability axis for an agent (what the brain is good at), kept
   SEPARATE from division (the domain where it works). See section 1.
2. MEMORY - a top-level block describing the division-scoped recollection
   feature (see MEMORY-SPEC v1). The settings file only holds memory
   METADATA and the chain-switch; memory CONTENT is not stored here.
3. settings_schema bumps 2 -> 3 (additive; v1.1 files still load via the
   round-trip merger, missing role/memory filled by defaults).

## 1. Taxonomy: division vs role (two perpendicular axes)

This is the most important conceptual change. Earlier drafts mixed the two
axes and produced non-orthogonal categories (e.g. treating "Social Media" as
a capability). v1.2 fixes it:

    DIVISION = WHERE the agent works (the domain / org unit).
               Examples: Engineering, Security, Content, Operations,
               Community, Marketing. A light label, no permissions.

    ROLE     = WHAT the brain is good at (the capability / profession).
               Examples: Solver, Architect, Crafter, Analyst, Communicator,
               Sentinel, Operator. Drives model preference + tools + rights.

They are independent: a Communicator (role) can sit in the Marketing
division; an Analyst (role) can sit in Engineering. "Social media" is a
DIVISION concern (Community/Marketing), NOT a role - it is realized by agents
whose ROLE is Communicator (or Analyst for research). Never put a domain word
in the role list.

## 2. The seven roles (capability axis)

Each role = { required capabilities, ordered preferred models (filtered at
runtime by model_kind against the providers you actually have keys for),
default toolset, rights, persona hint }. Role is METADATA that wraps things
the engine already has (model_kind detection, fallback chain, polite
complaint, persona). It does not invent a new engine.

    Solver       orchestrate + solve complex tasks; the ONLY role with
                 SUPERVISION rights (may task/revise other agents).
                 preferred: reasoning > long-context text > vision (to absorb
                 PDFs/images). tools: task-solving, supervise, simulate.
                 persona: decisive, structured, asks-before-acting.

    Architect    see the forest: repo structure audit, principle-conflict
                 detection, redesign proposals. preferred: reasoning > coder.
                 tools: read-structure, propose-change. rights: read + propose
                 (does not execute edits itself).

    Crafter      the technical hands: write/refactor/debug code, open PRs,
                 write+run tests. preferred: coder. tools: write-code,
                 run-tests.

    Analyst      eyes + synthesizer: web research, absorb documents (vision),
                 produce cited insights/reports. preferred: long-context text
                 > vision. tools: read-web, read-file, produce-report.

    Communicator the public voice: draft posts/threads/DMs/devlogs, monitor
                 mentions, escalate sensitively. preferred: instruct text.
                 tools: draft, send-for-approval. rights: DRAFT-FIRST only
                 (never auto-post).

    Sentinel     the shield: security + dependency audit, CVE detection,
                 flag breaking changes. preferred: coder > reasoning.
                 tools: read-security, flag-change.

    Operator     the clock: run scheduled routines and hand-offs (patrol,
                 CI, release, bridge). preferred: text / light coder.
                 tools: run-routine, hand-off.

## 3. Solver and supervision (the flagship role)

Solver is the value proposition: a user drops RAW material (photo/PDF/link/
example answer) + a prompt, and receives a structured output. Solver may
research other agents' work and ORDER revisions (e.g. tell Crafter to fix a
code section, tell Analyst to complete data), assemble the result, run
what-if simulations on the user's main project, then hand the DRAFT to the
user for approval (draft-first is sacred).

Design choice for Template #1: the default maintainer crew does NOT ship a
Solver. Solver is an AD-HOC orchestrator a user creates on demand (the
makalah example). This keeps the routine crew lean and demonstrates the
Create-Agent wizard (pick role -> engine fills preferred model + tools +
rights). Supervision is therefore OFF by default everywhere and ON only for
a Solver the user explicitly creates.

## 4. New agent field: role

Every agent record gains:

    "role": "Solver" | "Architect" | "Crafter" | "Analyst" |
            "Communicator" | "Sentinel" | "Operator"

Default if missing after migration: see section 8. The wizard's Create-Agent
step presents role as a dropdown; choosing a role auto-fills brain
preference (via the roles block) and rights, but the user can still override
the brain chain manually.

## 5. New top-level block: roles (the definition table)

    "roles": {
      "Solver":       {"capabilities": ["orchestrate","solve","supervise"],
                       "preferred_kinds": ["reasoning","text","vision"],
                       "tools": ["task-solving","supervise","simulate"],
                       "privileges": ["supervise"]},
      "Architect":    {"capabilities": ["structure-audit","redesign"],
                       "preferred_kinds": ["reasoning","coder"],
                       "tools": ["read-structure","propose-change"],
                       "privileges": []},
      "Crafter":      {"capabilities": ["code","test"],
                       "preferred_kinds": ["coder"],
                       "tools": ["write-code","run-tests"],
                       "privileges": []},
      "Analyst":      {"capabilities": ["research","synthesize"],
                       "preferred_kinds": ["text","vision"],
                       "tools": ["read-web","read-file","produce-report"],
                       "privileges": []},
      "Communicator": {"capabilities": ["draft","engage"],
                       "preferred_kinds": ["text"],
                       "tools": ["draft","send-for-approval"],
                       "privileges": ["draft-first"]},
      "Sentinel":     {"capabilities": ["security","dependency-audit"],
                       "preferred_kinds": ["coder","reasoning"],
                       "tools": ["read-security","flag-change"],
                       "privileges": []},
      "Operator":     {"capabilities": ["routine","handoff"],
                       "preferred_kinds": ["text","coder"],
                       "tools": ["run-routine","hand-off"],
                       "privileges": []}
    }

preferred_kinds are matched against lib/model_kind.classify() over the LIVE
provider catalog. The wizard only offers models whose kind is in the role's
preferred_kinds AND whose provider you have a key for. If a provider has no
matching model, the engine falls back to the house model and sends a polite
complaint (the exact self-healing mechanism proven on 21 Oct 2026). This is
how "not every API lists the model we want" is solved: role stores a CANDIDATE
LIST filtered by live catalog + kind, never a single rigid model id.

## 6. New top-level block: memory (metadata only)

    "memory": {
      "mode": "local",
      "per_division_quota_mb": 64,
      "retain_days": 0,
      "chain": {"enabled": false, "network": "sepolia",
                "contract": "0x0000000000000000000000000000000000000000",
                "rpc": "", "wallet_env": "STRATOFLY_CHAIN_KEY"}
    }

Semantics live in MEMORY-SPEC v1. The wallet secret is referenced by ENV-VAR
NAME (wallet_env) only; the value lives in .env. settings.json never holds a
secret. memory.content is NOT stored in this file.

## 7. Wizard Create-Agent contract (Friday/Saturday surface)

When the user runs the settings wizard and picks Create Agent, the engine:
  a) asks id, division, then ROLE (dropdown of the 7);
  b) looks up roles[ROLE].preferred_kinds;
  c) filters the live catalog of each provider-with-key by model_kind in
     those kinds, and shows only SAFE-for-text candidates (vision/audio are
     hidden unless the role explicitly prefers them, e.g. Solver/Analyst);
  d) if the user still picks a non-text model for a text-only role, the
     polite warning from model_kind.explain() fires and asks confirmation;
  e) fills brain chain from the chosen candidate(s), tools/privileges from
     roles[ROLE], then enforces HARD 10/provider and SOFT 30 totals;
  f) saves. No persona/code is edited (settings-are-data rule).

## 8. Template #1 role mapping (the 10 souls, capability axis added)

crew_template = "maintainer-crew" seeds these roles. (Solver intentionally
absent from the default crew - see section 3.)

    scout    | Engineering | Analyst      (synthesize + categorize issues)
    triage   | Engineering | Crafter      (review PRs, technical comments)
    tester   | Engineering | Crafter      (analyze CI/test results)
    sentinel | Security    | Sentinel     (security + dependency audit)
    bridge   | Security    | Architect    (detect API/SDK drift, breaking)
    scribe   | Content     | Communicator (docs + changelog)
    medic    | Operations  | Analyst      (absorb + synthesize incidents)
    release  | Operations  | Operator     (scheduled release pipeline)
    herald   | Community   | Communicator (draft threads/devlogs)
    diplomat | Community   | Communicator (monitor mentions, draft replies)

Distribution: Analyst 2, Crafter 2, Sentinel 1, Architect 1, Communicator 3,
Operator 1 = 10. Multiple agents sharing a role is correct - role is a
capability many can hold.

Migration rule (v1.1 -> v1.2): for crew_template = maintainer-crew, fill each
agent's role from the table above. For a custom crew, an agent missing a role
defaults to "Operator" and the loader warns once (Operator is the safest
least-privileged capability). Existing v1.1 files load unchanged otherwise.

## 9. Coherence with model_kind (why this is cheap, not a new engine)

    model_kind  = the DETECTION layer (vision/coder/reasoning/text)  [built]
    role        = the INTENT layer (what capability we want)          [this spec]
    provider_hub= the EXECUTION layer (chain + fallback + complaint)  [built]
    persona     = the VOICE layer                                     [built]

role sits on top of detection+execution we already shipped green. Adding role
is adding metadata + a filtered dropdown, not a subsystem. That is why it can
land before the hackathon without risk.

## 10. Full schema 3 example (authoritative shape)

    {
      "settings_schema": 3,
      "crew_template": "maintainer-crew",
      "repos": ["example-org/example-repo"],
      "brains": {
        "WORKHORSE":  [{"provider":"nvidia","model":"example-org/example-model"}],
        "SPECIALIST": [{"provider":"nvidia","model":"example-org/example-model"}],
        "LIFELINE":   [{"provider":"nvidia","model":"example-org/example-model"}]
      },
      "roles": { "...see section 5..." : {} },
      "agents": {
        "scout": {"enabled":true,"autonomous":true,"brain":"WORKHORSE",
                  "cadence_hours":6,"division":"Engineering",
                  "role":"Analyst","template_role":"scout"}
      },
      "limits": {"max_total_agents":30,"max_per_provider":10},
      "memory": { "...see section 6..." : {} },
      "notifications": {"severity_filter":["info","warn","crit"],
                        "quiet_hours_utc":null,"telegram_deliver_seconds":10}
    }

## 11. Constraints (non-negotiable, inherited + new)

- NEVER store secrets in settings.json (keys in .env; wallet by env-name).
- NEVER strip unknown fields on write (round-trip safe).
- NEVER empty a brain chain.
- Division and role are DIFFERENT axes; never merge them (section 1).
- Supervision rights exist ONLY on role=Solver, and only when a user creates
  such an agent (section 3).
- The engine NEVER performs system/mouse/keyboard control (safety boundary).
- Do NOT bump the code SCHEMA constant to 3 until roles{} + memory{} are
  implemented (spec-leads-code rule at the top).

## 12. Milestones

- S3 (Sat): dashboard localhost renders division + role + memory-mode badges
  from settings.json (read-only first).
- S4 (Sun): wizard Create-Agent exposes the role dropdown + filtered catalog.
- S5 (post-hackathon): implement lib/memory.py (M1 local) + bump SCHEMA 2->3
  + wire roles{} preferred_kinds into provider_hub catalog filtering.

## 13. Changelog
- v1.2 (24 Oct 2026): role capability axis (7 roles) separated from division;
  roles{} definition block; memory{} block (metadata, points to MEMORY-SPEC);
  Solver supervision rule; Template #1 role mapping; wizard create-agent
  contract; schema target 3 with spec-leads-code guard.
- v1.1 (22 Oct 2026): platform-instance framing; agent registry; hard/soft
  limits; autonomy switch (history).
- v1.0 (18 Oct 2026): initial schema (history).
