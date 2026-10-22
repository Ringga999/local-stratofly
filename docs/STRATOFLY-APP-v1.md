# STRATOFLY APP v1 — Mobile Product Spec

> Version: 1.0 · Date: 19 October 2026 · Status: FROZEN
> Target: Play Store first, iOS second

---

## User Journey (happy path)

1. Open app → login (Google/Gmail/WhatsApp/Telegram)
2. Create a **Division** (e.g., "Marketing", "Engineering")
3. Create **Agents** inside the division
4. Add API keys (free tier → agent created; paid → auto-provisioned)
5. Configure each agent (tasks, brain, cadence)
6. Agents start working → activity visible in Agent Verse
7. User earns via ZPRO mining, plugin marketplace, faucet claims

---

## 12 Core Features

| # | Feature | Purpose |
|---|---------|---------|
| 1 | Login/Register | Google, Gmail, WhatsApp, Telegram only |
| 2 | Dashboard | Activity charts, total agents, history |
| 3 | Agent Settings | Per-agent brain, cadence, tasks |
| 4 | Chatbot | Agent ↔ Telegram/etc bridge |
| 5 | Agent Verse | Visual world of agent activity |
| 6 | Profile | User account, divisions, API keys |
| 7 | Plugin | AI plugins, knowledge, skills |
| 8 | Dev Portal | Upload plugins (AI-confirmed) |
| 9 | $ZPRO Wallet | Captcha mining, wallet, tasks, ZPRO PoW terminal |
| 10 | AI Chatbot Bubble | Copilot-style in-app assistant |
| 11 | Settings | App preferences, notifications |
| 12 | FAQ | Self-serve help |

---

## Premium Features

### Pricing Tiers
- **Free:** unlimited agents up to 100, ads supported
- **Pro ($5/month or $35/year):** 100+ agents, no ads, ZPRO terminal access

### Auto-API Subscription
- User picks desired API (Claude, ChatGPT, etc.)
- Stratofly provisions & bills automatically
- Transparent pricing passthrough

### Agent Khusus (MCP-like, computer-control)
**Flow:**
0. User provides API
1. User enables Agent Khusus feature
2. System requests permissions (accessibility, overlay, input)
3. Small circular floating button appears (pause button)
4. User gives commands via dedicated in-feature chat (NOT the floating button)
5. User runs agent → agent takes over the computer
6. Floating pause button stays visible at all times for instant stop

**Safety:**
- Pause button ALWAYS on top, ALWAYS reachable
- Every action logged on-chain
- User confirmation for destructive actions
- Auto-pause on unknown UI state

---

## Blockchain & Privacy

- All user data hashed & recorded on ZCP2O blockchain
- Encrypted at rest
- Zero-knowledge where possible
- User owns their data export

---

## Plugin Developer Flow

1. Dev registers
2. Uploads plugin (manifest + persona)
3. AI agent reviews: functionality, safety, license compliance
4. Approved → listed in marketplace
5. Free plugins: gas fee $ZPRO = $0.1 per use
6. Paid plugins: 25% ecosystem tax + gas fee