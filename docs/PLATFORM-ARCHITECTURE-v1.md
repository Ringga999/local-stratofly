# STRATOFLY PLATFORM ARCHITECTURE v1

> Version: 1.0 · Date: 19 October 2026 · Status: FROZEN
> Owners: Mr Architect & Mr Visioner
> Scope: two-repo strategy, licensing, security posture, zero-cost stack

---

## 1. Positioning

Stratofly is an always-on AI agent platform that chains free and paid
model APIs from many providers at once, so anyone — especially
students with zero budget — can own a working AI crew.

Two products share one core:

- **local-stratofly** — open-source, self-hosted, hackathon-facing.
  Runs a mini Stratofly locally; users reach it via browser at
  http://localhost:<port>.
- **stratofly** — the commercial cloud app (Play Store first):
  managed infra, marketplace, $ZPRO economy, premium features.

The maintainer crew of the ZCP2O ecosystem is Template #1: the first
crew living on the platform, and its long-term dogfood testbed.

## 2. Why users choose Stratofly when local-stratofly is free

Seven pillars (the founding answer — memorize these):

1. INSTANT ACCESS — login and go; no install, no venv, no .env ritual.
2. MANAGED INFRASTRUCTURE — we run the servers; users run their lives.
3. CROSS-DEVICE UNITY — one crew on phone, tablet, desktop, browser.
4. PREMIUM FEATURES — marketplace, computer-control agent, ZPRO
   terminal, AI bubble assistant.
5. EARNING ECONOMY — the crew produces income (mining, tasks,
   plugin revenue share), not only work.
6. BLOCKCHAIN TRUST — activity logs on-chain; verifiable, tamper-proof.
7. COMMUNITY & DISCOVERY — plugins, Agent Verse, leaderboards.

Philosophical pillar: TWO FREEDOMS.
local-stratofly = freedom to learn, fork, build.
stratofly = freedom to use and earn without technical friction.
Not competition — two roads to the same destination.

## 3. Repository topology

stratofly (commercial app)
  └─ imports stratofly-core (shared Python package)
       └─ imported by local-stratofly (open-source wrapper: CLI + web UI)

Until the core is extracted as its own package (milestone CORE-EXTRACT),
local-stratofly carries the core in-tree. Extraction happens after
Test 1 sign-off. Do not extract earlier.

## 4. Licensing (FINAL DECISION — 19 Oct 2026)

- **Code: Apache License 2.0** for local-stratofly and stratofly-core.
  Use, modify, fork, learn: free for everyone, forever.
- **Trademark: "Stratofly" is protected separately.**
  Forks MUST ship under a different name and remove Stratofly
  branding. The name belongs to the ecosystem.
- **stratofly (cloud app) binaries and backend: proprietary.**
  The app store build is not open source; its server-side logic
  (billing, marketplace ledger, ZPRO wallet) never ships to clients.
- **Plugins: PLUGIN-SPEC rules.** Free plugins pay gas fee
  ($ZPRO = $0.1). Paid plugins pay 25% ecosystem tax + gas fee.
- **Personas derived from MIT-licensed agency sources keep MIT +
  attribution.** They can never be re-licensed as proprietary.

Why not MIT: no protection against instant commercial cloning.
Why not AGPL: scares hackathon contributors and companies away.
Apache 2.0 + trademark = open enough to grow, protected enough to survive.

## 5. Anti-reverse-engineering posture (stratofly app)

Three free layers:

L1 Obfuscation — ProGuard/R8 (Android, built-in), release builds only.
L2 Runtime integrity — Play Integrity API checks, anti-debug
  (Frida/Xposed detection), self-checksum at boot; refuse to run
  when tampered.
L3 Server-side truth — all critical logic (key validation, billing,
  marketplace, wallet ledger, blockchain logging) lives in the cloud
  backend. The app is a remote control; opening it reveals no secrets.

Rule: any secret that must stay secret MUST live server-side.
The client is assumed hostile by design.

## 6. Zero-cost stack (modal $0 doctrine)

| Layer | Service (free tier) | Notes |
|---|---|---|
| LLM brains | NVIDIA NIM, Groq, OpenRouter free tiers | provider hub chains them |
| Database | Supabase (PostgreSQL) | 500 MB |
| Auth | Supabase Auth | Google/WhatsApp/Telegram login |
| Storage | Supabase Storage | 1 GB |
| Backend hosting | Vercel / Railway free tier | serverless functions |
| CI/CD | GitHub Actions | 2000 min/month |
| Error tracking | Sentry free tier | 5k errors/month |
| Agent VMs | Instabox virtual computers (per test plan) | tests only |
| App store | Play Store console fee — ALREADY SECURED by owner | one-time |

Operating cost target: $0/month until revenue exists.

## 7. Guardrails for the open repo (local-stratofly)

Against acquisition & misuse:
- Apache 2.0 + trademark clause in README and TRADEMARK.md
- CODE_OF_CONDUCT.md from day one
- Short CLA for contributors (copyright stays with author;
  ecosystem gets sublicense rights)
- No secrets in repo: .env never committed (gitignore enforced)
- Security policy: SECURITY.md with responsible disclosure route

## 8. Milestone map (pointers)

- Tests & launch gate: docs/LAUNCH-TEST-PLAN-v2.md
- Mobile product: docs/STRATOFLY-APP-v1.md
- Settings layer: docs/SETTINGS-SPEC-v1.md (draft; revision pending
  to match platform framing)
- Plugins: PLUGIN-SPEC (Phase 12)
- Model recipes: RECIPE-SPEC (Phase 12)

## 9. Changelog

- v1.0 (19 Oct 2026): two-repo topology, Apache 2.0 + trademark
  licensing, anti-REA posture, zero-cost stack, guardrails.