# Installation & Configuration

This guide complements the README. If the README answers "what is this", this document answers "how do I run it on my machine, and how do I configure it".

## 1. Prerequisites

- **Python 3.11 or newer.** Check with `python --version`.
- **Git.** Check with `git --version`.
- **A free LLM API key** (optional). The engine runs without one — you can explore the control room and use mock mode. Real agent thinking needs a key; grab one from the *Free APIs* menu inside the control room (NVIDIA NIM, Groq, OpenRouter).

## 2. Install

```bash
git clone https://github.com/Ringga999/local-stratofly.git
cd local-stratofly
python -m venv venv
```

Activate the isolated environment:

```bash
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Why a virtual environment? It keeps this project's dependencies separate from everything else on your machine, and makes `requirements.txt` reproducible for anyone who clones the repo. Do not skip it.

Note: `web3` is optional at runtime. If it is not installed, the on-chain anchoring layer disables itself and local memory keeps working exactly as before.

## 3. Run

```bash
python main.py serve
```

Open `http://localhost:8765`. Stop with `Ctrl+C`.

## 4. First run without keys

The control room loads with a default crew. Agents show `ready - waiting for task`. You can:

- Browse Live Crew, agent details, brains, and limits.
- Toggle **Mock** to simulate agent activity for demos without any API calls.
- Paste a free API key in the **Onboard** panel when you want real answers. The key is written to a local `.env` and never sent anywhere else.

## 5. Configuration

Everything you can tune lives in two files that never enter git:

| File | Holds | Edited via |
|---|---|---|
| `.env` | Secrets: API keys, chain key, RPC URL | Onboard panel, or manually |
| `settings.json` | Crew shape: agents, brains, limits, watched repos, memory mode, per-agent plugins | Control room, or manually |

`.env` variables:

| Variable | Purpose |
|---|---|
| `NVIDIA_API_KEY` | NVIDIA NIM access (primary free provider) |
| `GITHUB_TOKEN` | Optional; public repos work tokenless |
| `SEPOLIA_RPC_URL` | Optional; Sepolia RPC endpoint for anchoring |
| `STRATOFLY_CONTRACT_ADDRESS` | Optional; deployed StratoflyAnchor address |
| `STRATOFLY_CHAIN_KEY` | Optional; **testnet-only** wallet key for anchoring |

`settings.json` keys: `agents`, `brains`, `limits`, `repos`, `memory_mode`, `agent_plugins`.

Both files are gitignored. After editing either, run `git status` — it must stay clean. If a secret ever shows up as a change, stop and fix `.gitignore` before committing anything.

## 6. Memory modes

Agent memory lives in SQLite (`memory.sqlite3`) on your machine. On top of that sits an optional anchoring layer.

| Mode | Behavior |
|---|---|
| `local` | SQLite only. Fast, free, no external network. |
| `hybrid` (default) | SQLite as the source of truth, plus a SHA-256 hash of each memory payload anchored to Sepolia as proof of integrity and time. |

Check the current state at `http://localhost:8765/api/memory/status`.

The engine never depends on the chain to keep working. If anchoring is off, unconfigured, or the network is unreachable, memory stays local and the crew keeps running. You will see a log line such as `[chain] anchor failed (local copy kept)` — that is the safety net doing its job, not a crash.

## 7. On-chain anchoring (optional)

What it does: for each anchored event, the engine computes a SHA-256 hash of the local payload and submits it to a `StratoflyAnchor` contract on Sepolia. The original data never leaves your machine; the chain stores only the hash, a timestamp, and the submitting address.

Reference deployment (public, Sepolia): `0x1f2d2144D246e1EFcf070cD7d58f7067DEeF0Db3`. You may point at it, or deploy your own copy (Appendix A) via Remix.

To enable, set three variables in `.env`:

```
SEPOLIA_RPC_URL=<your Sepolia RPC endpoint>
STRATOFLY_CONTRACT_ADDRESS=<deployed StratoflyAnchor address>
STRATOFLY_CHAIN_KEY=<private key of a TESTNET account>
```

Rules that matter:

- Use a **Sepolia testnet account** holding no real value. Never put a mainnet private key on this machine.
- MetaMask exports keys without the `0x` prefix; add it so the value is 66 characters.
- Public anonymous RPC endpoints are sometimes rate-limited or blocked on certain networks. If anchoring logs `rpc unreachable`, switch to a keyed endpoint from Infura or Alchemy (free tier). This is the single most common anchoring issue.
- The key lives only in `.env`. Logs and the UI show a masked wallet address, never the key.

Verify it works: send a prompt through **Command the Crew**, watch the server terminal for `[chain] anchored <agent> tx=0x...`, then open `https://sepolia.etherscan.io/tx/<that hash>`. A `Success` status is your proof.

## 8. Troubleshooting

**OneDrive locks files (Windows).** If the project lives under OneDrive and you see `Permission denied` or deletions that never finish, pause OneDrive syncing (tray icon → Pause syncing), do the operation, then resume. Avoid `git clean` for removing folders inside a synced tree; remove them manually instead.

**`Unable to copy venvlauncher.exe` when creating a venv.** A previous venv in that folder is still locked. Leave the folder (`cd /d C:\`), delete it entirely (`rd /s /q <folder>`), close any terminal standing inside it, then recreate.

**`ImportError` after cloning.** Make sure you cloned the latest `main`. If a module seems missing, check whether it is tracked: `git ls-files lib` — a file that exists locally but is gitignored will never reach a clone.

**`ConnectionAbortedError: [WinError 10053]` in the server log.** The browser closed a connection mid-response (tab refresh or polling). Harmless noise; ignore it.

**Agent creation refused with a limit message.** The free-tier ceilings are working as designed. Remove an unused agent, or raise `limits.max_per_provider` / `limits.max_total_agents` in `settings.json` temporarily.

**`rpc unreachable` while anchoring.** See section 7: use a keyed RPC endpoint. Local memory is unaffected meanwhile.

## 9. Clean-clone verification

To prove the repo runs for a stranger with none of your data:

```bash
git clone https://github.com/Ringga999/local-stratofly.git C:\temp\stratofly-clean
cd /d C:\temp\stratofly-clean
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py serve
```

The server must start **without** any `.env`. `/api/memory/status` should report `configured: false`. If that holds, no secret is required to run the engine — and no secret has leaked.

## 10. Contributing

Start from `docs/ROLE-MODULES-BLUEPRINT.md`: pick one `planned` cell, branch as `feature/<role>-<module>`, build additively, verify with your own eyes plus a clean-clone test, and open a PR that also flips the cell to `done`. Never commit `.env`, `settings.json`, or `memory.sqlite3`.

## Appendix A — StratoflyAnchor.sol

The anchor contract source lives at [`contracts/StratoflyAnchor.sol`](../contracts/StratoflyAnchor.sol). To deploy your own copy: open Remix, compile with Solidity 0.8.x, and deploy to Sepolia via Injected Provider (MetaMask). The reference deployment used by this project: `0x1f2d2144D246e1EFcf070cD7d58f7067DEeF0Db3`.