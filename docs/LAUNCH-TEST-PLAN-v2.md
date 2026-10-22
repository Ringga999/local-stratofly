# STRATOFLY LAUNCH TEST PLAN v2

> Version: 2.0 · Date: 19 October 2026 · Status: FROZEN — gate for Play Store launch
> Replaces: LAUNCH-TEST-PLAN-v1
> Rule: ALL 7 tests must be signed off before Play Store listing.

---

## Prerequisites (apply to ALL tests)

- **Instabox virtual computer** assigned to every agent involved
- Engineering agents use **`example-engine` repository from GitHub**
- Stratofly platform-core complete (provider hub, runtime, scheduler,
  gateway, settings, self-onboarding, blockchain logging)
- `settings.json` configured per test scenario

---

## 🔬 TEST 1 — General Capability Proof

**Scope:**
- Execute owner-defined tasks
- Take Kahoot quizzes (browser automation + reasoning)
- Web research with cited references
- Read local files/folders (allow-list sandbox)

**New primitives required:**
- `WEB-RESEARCH` tool
- `KAHOOT-PLAYER` tool
- `LOCAL-READER` tool (strict sandbox)

**Duration:** 1 week
**Exit:** owner sign-off

---

## 🔬 TEST 2 — Instagram Social Media Management

**Scope:** 4 specialized agents in a Social Media Division.

**Agent 2A — Mutualan (Follow-back manager)**
- Chatbot interface for commands
- Detect non-followers, auto-unfollow after 1 week
- Follow accounts with >5 mutual connections
- Prioritize private accounts
- Target: 50 follows/day
- NEVER auto-followback

**Agent 2B — Postingan (Content engine)**
- YouTube video clipper (URL → clip → post)
- Daily news posts (auto-curated + drafted)

**Agent 2C — Balas DM (Template responder)**
- Template library configured via chatbot
- Auto-reply using templates

**Agent 2D — Social Media Exchange Handler**
- Access exchange platforms (e.g., example-exchange-platform)
- Handle sacrificial accounts
- Execute daily tasks on exchanges

**Duration:** 1 month
**New primitives required:** IG API/automation layer, content generator,
template engine, exchange platform connectors
**Exit:** monthly report + owner sign-off

---

## 🔬 TEST 3 — AI Intelligence Benchmark

**Scope:**
- Auto-claim crypto faucets
- Solve/bypass captchas (reCAPTCHA, hCaptcha, Cloudflare)

**Purpose:** measure AI problem-solving capability under real constraints.

**Duration:** 1 week
**Exit:** capability report (success rate, average solve time)

---

## 🔬 TEST 4 — Product Operations Month

**Scope:**
- Maintain `example-product-app` repository
- Create ads (draft-first, owner approval mandatory)
- Social media admin: IG, WA, Telegram, X, Discord

**New primitives required:** WA/X/Discord connectors, ad composer

**⚠ Meta paperwork MUST start before Test 2 ends** (weeks-long review).

**Duration:** 1 month
**Exit:** operations report + owner sign-off

---

## 🔬 TEST 5 — REA (Reverse Engineering) — self-development

**Scope:**
- Find games suitable as Godot-based agent activity monitor
- Study `example-3d-monitor` concept
- Reverse-engineer learnings into Stratofly improvements

**Note:** This test IS product development simultaneously.

**New primitives required:** REA toolkit, code analysis tools
**Duration:** 2–4 weeks
**Exit:** implementation PRs + design docs

---

## 🔬 TEST 6 — Protocol Long-Run (dogfood)

**Scope:** full maintainer crew on `example-protocol` for 3 months.

**Required agent capabilities:**
1. Repository solidity audit (principle conflicts, inconsistencies)
2. Cyber security review
3. Problem solving (risk & ecosystem issues)
4. Research & development

**Duration:** 3 months
**Exit:** stability report + owner sign-off

---

## 🔬 TEST 7 — Finance Trading AI Team

**Scope:**
- Agents use `example-trading-terminal` repository for analysis/news/references
- Execute trades autonomously
- Target: positive P&L over 1+ month

**Duration:** 1 month minimum (extendable based on performance)
**New primitives required:** exchange API connectors, risk manager
**Exit:** trading performance report + owner sign-off

---

## Launch gate — Play Store first

All 7 tests signed off → **Play Store listing goes live**

## Sequencing
Month 1: T1 (1 week) + T3 (1 week) + T5 start
Month 2: T2 (1 month) + T5 complete
Month 3: T4 (1 month) + T6 start + T7 start
Month 4: T6 continues + T7 continues
Month 5: T6 completes + T7 completes
Month 6: Sign-off → Play Store launch


Parallelization where safe (T5/T6/T7 are long-running).

## Changelog
- v2.0 (19 Oct 2026): expanded to 7 tests, Instabox + ponytail prerequisites,
  Play Store as primary launch target.