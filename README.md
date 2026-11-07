# Stratofly

**Open-source multi-agent orchestration engine with $0 modality - all agents run on free-tier LLM APIs.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/Ringga999/local-stratofly)

---

## What is Stratofly?

Stratofly is a **local-first multi-agent platform** where 7 specialized AI agents collaborate to solve complex problems. Unlike expensive cloud-based AI services, Stratofly runs entirely on **free-tier LLM APIs** (NVIDIA NIM, Groq, OpenRouter) with zero subscription cost.

**Think of it as:** Your personal AI crew - a Solver who breaks down problems, an Architect who designs solutions, a Crafter who writes code, an Analyst who researches data, a Communicator who drafts content, a Sentinel who guards security, and an Operator who runs routines - all working together on your local machine.

---

## Quick Start (30 seconds)

```bash
# Clone the repo
git clone https://github.com/Ringga999/local-stratofly.git
cd local-stratofly

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py serve
```

**Open browser:** http://localhost:8765/

**That's it.** No API keys required to explore. To connect real LLMs, add your free NVIDIA NIM key via the web UI.

---

## Architecture Overview

```
Web UI (app.html)
   | Live Crew | Add Agent | Command Crew | Brains | Activity |
        |
        v
api_server.py (HTTP)
   /api/state | /api/ask | /api/solve | /api/delegate
        |
        +-- settings.py, memory.py, scheduler.py, persona.py, provider_hub.py
              |
              v
        LLM Providers (NVIDIA | Groq | OpenRouter)
```

**Key Components:**
- **settings.py** - Configuration management (agents, brains, limits)
- **memory.py** - SQLite-based event logging + agent state tracking
- **scheduler.py** - Autonomous agent patrol system (scheduled tasks)
- **persona.py** - Role-specific system prompts (Solver, Architect, etc.)
- **provider_hub.py** - Unified interface to 3-tier brain chains

---

## Features

### 7 Specialized Agent Roles

| Role | Expertise | Tools |
|------|-----------|-------|
| **Solver** | Problem decomposition, orchestration | Task-solving, supervise, simulate |
| **Architect** | System design, restructuring | Read-structure, propose-change |
| **Crafter** | Code generation, testing | Write-code, run-tests |
| **Analyst** | Research, data synthesis | Read-web, read-file, produce-report |
| **Communicator** | Content drafting, engagement | Draft, send-for-approval |
| **Sentinel** | Security, dependency audit | Read-security, flag-change |
| **Operator** | Routines, handoffs | Run-routine, hand-off |

### 3-Tier Brain Chains

Each agent uses a **brain chain** - a sequence of LLM models optimized for different task complexities:

- **WORKHORSE** - Fast, cheap models for routine tasks (e.g., deepseek-coder-6.7b)
- **SPECIALIST** - Mid-tier models for complex reasoning (e.g., nemotron-3.5-lightning)
- **LIFELINE** - Premium models for critical decisions (fallback)

### Solver Orchestration

The **Solver** role can now:
1. Receive complex problems via the web UI
2. Decompose them into 3-5 concrete phases
3. **Delegate sub-tasks** to other agents via the Delegation Board
4. Each delegated agent responds in their own persona

### Free-Tier Safety Limits

Stratofly enforces **hard limits** to prevent accidental API overuse:
- **Max 10 agents per provider** (e.g., NVIDIA NIM free tier)
- **Max 30 agents total**
- Graceful error messages when limits are reached

---

## Web UI Features

- **Live Crew** - Real-time agent states (working, idle, alert, coffee break)
- **Agent Detail Modal** - Brain chain, role-specific modules, recent events
- **Free APIs Menu** - Quick links to get API keys
- **Add Agent Form** - Create new agents with role, brain, cadence
- **Command Crew** - Send free prompts to any agent
- **Activity Feed** - Real-time event logging
- **Mock Mode** - Simulate agent behavior for demos (no API calls)

---

## Documentation

Detailed specs are available in `docs/`:

- **ROLE-BLUEPRINT-SPEC-v1.md** - 7 roles, capabilities, tools, privileges
- **MEMORY-SPEC-v1.md** - SQLite schema, state tracking
- **SETTINGS-SPEC-v1.2.md** - Configuration structure
- **WEB3-INTEGRATION-SPEC-v1.md** - Blockchain anchoring roadmap

---

## Contributing

**We welcome contributions from developers of all skill levels!**

### How to Contribute

1. **Fork the repo** and clone it locally
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Run the server:** `python main.py serve`
5. **Make your changes** and test locally
6. **Commit with clear messages:** `feat: add new agent role`
7. **Push and open a Pull Request**

### Adding a New Agent Role

Want to add a new role (e.g., VideoEditor, SocialMedia)? Here's how:

1. **Edit `lib/settings.py`** - Add role definition to `defaults()["roles"]`
2. **Edit `lib/persona.py`** - Add system prompt for the role
3. **Edit `lib/app.html`** - Add role to dropdown menu
4. **Test locally** and submit PR

### Plugin System (Coming Soon)

We're building a plugin system where developers can:
- Create skills (e.g., `ponytail` for smart coding, `MoneyPrinterTurbo` for video)
- Register plugins in `plugins.json`
- Install/uninstall via web UI

---

## Roadmap

### Phase 1: Core Engine (Complete)
- [x] 7 agent roles with specialized personas
- [x] 3-tier brain chains (WORKHORSE/SPECIALIST/LIFELINE)
- [x] SQLite memory system
- [x] Web UI with live crew management
- [x] Free-tier safety limits

### Phase 2: Solver Orchestration (Complete)
- [x] Solver role with delegation capabilities
- [x] Delegation Board in web UI
- [x] Agent-to-agent handoff via /api/delegate
- [x] Role-aware system prompts

### Phase 3: Web3 Anchoring (In Progress)
- [ ] Deploy StratoflyAnchor contract to Sepolia testnet
- [ ] Integrate lib/chain_relay.py with web3.py
- [ ] Badge [ON-CHAIN] + Etherscan link in UI
- [ ] Hybrid architecture: data in SQLite, hash on blockchain

### Phase 4: Plugin Ecosystem (Planned)
- [ ] Plugin system (lib/plugins/ folder)
- [ ] Plugin registry (plugins.json)
- [ ] Web UI plugin manager
- [ ] Example plugins: ponytail, MoneyPrinterTurbo, SecurityAuditSkill

### Phase 5: Role Expansion (Planned)
- [ ] VideoEditor role
- [ ] SocialMedia role
- [ ] DataScientist role
- [ ] Community-contributed roles

---

## Use Cases

### For Developers
- **Code review assistant** - Sentinel scans PRs for security issues
- **Documentation generator** - Communicator drafts README from code
- **Test generator** - Crafter writes unit tests from specs

### For Content Creators
- **Blog post pipeline** - Analyst researches, Communicator drafts
- **Social media scheduler** - Operator schedules posts

### For Teams
- **Project planning** - Solver breaks down project, delegates to team
- **Knowledge base** - All agents share memory.sqlite3

---

## Privacy & Security

- **Local-first** - All data stays on your machine
- **API keys in .env** - Never committed to git
- **Free-tier limits** - Prevents accidental API overuse
- **No telemetry** - Stratofly does not phone home

---

## License

**Apache License 2.0** - See LICENSE for details.

You're free to use, modify, and distribute Stratofly for commercial or non-commercial purposes.

---

## Contact

**Author:** Ringga Putra
**GitHub:** @Ringga999
**Project:** https://github.com/Ringga999/local-stratofly

---

**Star this repo if you find it useful!**

*Built with love for the open-source community.*