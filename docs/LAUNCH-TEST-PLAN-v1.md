# STRATOFLY LAUNCH TEST PLAN v1

> Version: 1.0 · Date: 18 October 2026 · Status: FROZEN — gate for public launch
> Owners: Mr Architect & Mr Visioner
> Rule: NO PUBLIC LAUNCH until Tests 1–3 are signed off by the owner.
> Each test starts only after (a) the app is fully formed and
> (b) the owner has configured settings for that test's needs.

---

## 1. Entry criteria (apply to every test)

- Platform renamed to Stratofly (repo, brand, bot identity)
- Platform-core complete: provider hub, runtime, scheduler, gateway,
  settings layer, self-onboarding
- `settings.json` configured for the test at hand
- Owner approval channel (Telegram) active — draft-first doctrine in force

## 2. 🔬 TEST 1 — General Capability Proof

**Objective:** prove Stratofly executes arbitrary tasks end-to-end.

**Scope:**
- Execute several owner-defined tasks
- Browse the internet for references (web research)
- Read files/folders from the local machine

**New platform primitives REQUIRED before this test:**
- `WEB-RESEARCH` tool (search + fetch + cite)
- `LOCAL-READER` tool (strict allow-list sandbox; zero out-of-scope access)

**Configuration by owner:** task list; allow-listed local directories.

**Success criteria:**
- 100% of assigned tasks completed with cited web references
- Local reads confined to allow-list; any out-of-scope attempt refused and reported
- Every failure delivered as a polite complaint — zero silent failures

**Duration:** owner-defined (suggested: 1 week)
**Exit:** owner sign-off

## 3. 🔬 TEST 2 — Product Operations Month

**Objective:** run real product operations for one full month.

**Scope:**
- Maintain repository `notapeer-app` (private → GitHub auth required)
- Create advertisements (draft-first; owner approval mandatory)
- Act as social media admin on: Instagram, WhatsApp, Telegram, X, Discord

**New platform primitives REQUIRED before this test:**
- Connectors: IG, WA, TG, X, Discord (TG already exists)
- Ad-draft composer (draft-first)

**LEAD-TIME WARNING:** Meta app review (Instagram/WhatsApp) can take
weeks. Paperwork MUST start before Test 1 ends, or Test 2 slips.

**Doctrine in force:** nothing is published anywhere without owner
approval. Drafts expire after 7 days.

**Success criteria:**
- Zero unauthorized posts (100% of published content owner-approved)
- Mentions/messages answered within agreed SLA
- No critical repo issue missed during the month

**Duration:** 1 month
**Exit:** monthly operations report + owner sign-off

## 4. 🔬 TEST 3 — Protocol Long-Run (dogfood)

**Objective:** prove unattended stability over three months on our own ecosystem.

**Scope:** full maintainer crew on `zcp2o-protocol`.

**Success criteria:**
- Patrol uptime ≥ 99%
- Every provider failure self-healed AND notified (polite complaint delivered)
- Memory consistent; no duplicate reports; no silent failures

**Duration:** 3 months
**Exit:** stability report + owner sign-off

## 5. Launch gate

All three tests signed off → **Launching ✅**

Launch checklist:
- Docs updated (PLATFORM-SPEC, SETTINGS-SPEC, PLUGIN-SPEC, GAME-SPEC)
- Economy policy published ($ZPRO gas fee; 25% tax on paid plugins)
- Onboarding wizard live: one-free-key guided path (primary),
  zero-key survival mode (fallback)

## 6. Sequencing note

Default: sequential T1 → T2 → T3 → launch (≈ 4 months).
Option (owner's call): run T3 in parallel with T2 — T3 is daily dogfood
anyway — compressing launch to ≈ 1 month after T2 ends.

## 7. Changelog

- v1.0 (18 Oct 2026): initial gate — three tests, launch criteria,
  primitive prerequisites, Meta lead-time warning.