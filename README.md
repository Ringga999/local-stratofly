# Stratofly

Many agents. One crew. No subscription.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## What is Stratofly?

Stratofly is a **local-first multi-agent orchestration engine**. Most AI tools hand you a single assistant that waits for the next prompt; Stratofly assembles a crew — distinct agents with distinct personalities, distinct skills, and the ability to pass work to one another — running on your own machine. It draws entirely on free-tier LLM APIs (NVIDIA NIM, Groq, OpenRouter), so you can build, experiment, and break things without ever opening your wallet.

Let us be honest up front: **this is an engine, not a finished product.** It is in alpha. The foundation is alive today — a growing catalog of roles, a three-tier brain chain, local memory, and Solver orchestration. Much of what each role can do is still being built out, and that unfinished space is exactly where the next contributor walks in.

The crew already includes a Solver that tears a problem apart and hands the pieces out, an Architect that designs systems, a Crafter that writes the code, an Analyst that researches and synthesizes, a Communicator that drafts content, a Sentinel that watches for security, and an Operator that keeps routines alive — and nothing in the design treats that list as a ceiling. A role here is declared as *data* (a persona, a capability set, a privilege boundary) rather than compiled into the engine, which is the whole reason the catalog can widen toward hundreds of roles without rebuilding the machine.

---

## Quick Start

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

You can explore the control room without any key. To bring agents to life, paste a free NVIDIA NIM key through the web UI — it is written to a local `.env` and never sent anywhere.

---

## Architecture Overview

**Key Components:**
- **settings.py** — Configuration management (agents, brains, limits)
- **memory.py** — SQLite-based event logging + agent state tracking
- **scheduler.py** — Autonomous agent patrol system (scheduled tasks)
- **persona.py** — Role-specific system prompts
- **provider_hub.py** — Unified interface to the 3-tier brain chains

The web control room talks to a lightweight HTTP server (`ThreadingHTTPServer`, no web framework), which routes to the components above and onward to the LLM providers.

---

## Features

### A role system built to grow, not to a fixed roster

Because a role is data and not code, the engine you run today is already cut to carry far more roles than it currently ships. Adding one means *defining* one, not rebuilding the machine. The roster standing here now is simply the first to arrive.

### 3-Tier Brain Chains

Each agent uses a **brain chain** — a sequence of LLM models matched to the workload:

- **WORKHORSE** — Fast, cheap models for routine tasks
- **SPECIALIST** — Mid-tier models for complex reasoning
- **LIFELINE** — Premium models as the safety net for critical decisions

### Solver Orchestration

The **Solver** is the heart of the engine. Give it a messy, complex problem and it:
1. Receives the problem via the web UI
2. Decomposes it into concrete phases
3. **Delegates sub-tasks** to other agents through the Delegation Board
4. Lets each delegated agent answer in its own persona, with its own context — not as an echo of the Solver

### Free-Tier Safety Limits

Free APIs are generous — until they are not. The engine enforces **configurable hard ceilings** on how many agents each provider may carry (by default, ten per provider and thirty overall), with graceful errors when a limit is reached, so one careless afternoon never becomes a surprise invoice.

---

## Web UI Features

- **Live Crew** — Real-time agent states (working, idle, alert, coffee break)
- **Agent Detail Modal** — Brain chain, role-specific modules, recent events
- **Free APIs Menu** — Quick links to get API keys
- **Add Agent Form** — Create new agents with role, brain, cadence
- **Command Crew** — Send free prompts to any agent
- **Activity Feed** — Real-time event logging
- **Mock Mode** — Simulate agent behavior for demos (no API calls)

---

## Documentation

Detailed specs live in `docs/`:

- **ROLE-BLUEPRINT-SPEC-v1.md** — The role catalog: capabilities, tools, privileges
- **MEMORY-SPEC-v1.md** — SQLite schema, state tracking
- **SETTINGS-SPEC-v1.2.md** — Configuration structure
- **WEB3-INTEGRATION-SPEC-v1.md** — The optional on-chain anchoring layer

---

## Contributing

**We welcome contributions from developers of all skill levels.**

### How to Contribute

1. **Fork the repo** and clone it locally
2. **Create a feature branch:** `git checkout -b feature/your-feature-name`
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Run the server:** `python main.py serve`
5. **Make your changes** and test locally
6. **Commit with clear messages:** `feat: add a new role` or `fix: ...`
7. **Push and open a Pull Request**

### Adding a New Role

Roles are declared as data, so extending the crew is a matter of definition, not surgery. A new role needs a persona, a capability set, and a privilege boundary; the engine picks it up from there. Start from `docs/ROLE-BLUEPRINT-SPEC-v1.md` to see how existing roles are shaped, and follow the contribution flow above.

---

## Privacy & Security

- **Local-first** — All data stays on your machine
- **API keys in .env** — Never committed to git
- **Free-tier limits** — Prevents accidental API overuse
- **No telemetry** — Stratofly does not phone home

---

## License

**Apache License 2.0** — See LICENSE for details.

You're free to use, modify, and distribute Stratofly for commercial or non-commercial purposes.

---

## Contact

**Author:** -
**GitHub:** @Ringga999
**Project:** https://github.com/Ringga999/local-stratofly
**Email (collaboration / help / contribution):** 1045weeks@gmail.com