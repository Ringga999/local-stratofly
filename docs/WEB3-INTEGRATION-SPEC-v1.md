# WEB3-INTEGRATION-SPEC v1 (Product Spec + Post-Demo Blueprint)

Target: Tuesday-Wednesday (post-hackathon). Home: local-stratofly/docs/.
Core Principle: HASH ON-CHAIN, BLOB OFF-CHAIN. ALWAYS.
Status: DESIGN FROZEN. Do not implement before Monday demo is complete.

## 1. The Problem
Users want cryptographic proof that an agent config, memory, or action was not
tampered with after the fact. But storing full JSON on Ethereum is
prohibitively expensive (gas) and slow (about 15s per block), ruining UX.

## 2. The Hybrid Architecture (the honest way)
We do NOT replace the backend with blockchain. We use them together:
1. Source of Truth (fast): settings.json (local) or Supabase (cloud). Instant.
2. Integrity Anchor (trust): Ethereum Sepolia Testnet (later mainnet). Stores
   ONLY the sha256 hash of the data plus a timestamp.
Flow: user clicks Save Agent -> backend saves settings.json (instant) ->
  backend computes sha256(config) -> backend calls contract anchor(hash) ->
  UI shows Anchoring -> contract confirms -> UI shows an ON-CHAIN badge with
  an Etherscan link.

## 3. Smart Contract (Solidity, deploy via Remix to Sepolia)

    // SPDX-License-Identifier: Apache-2.0
    pragma solidity ^0.8.20;

    contract StratoflyAnchor {
        struct Stamp { bytes32 hash; uint256 at; address by; }
        mapping(bytes32 => Stamp) public stamps;

        event Anchored(bytes32 indexed hash, uint256 at, address by);

        function anchor(bytes32 h) external {
            require(h != bytes32(0), "empty hash");
            require(stamps[h].at == 0, "already anchored");
            stamps[h] = Stamp(h, block.timestamp, msg.sender);
            emit Anchored(h, block.timestamp, msg.sender);
        }

        function verify(bytes32 h) external view returns (bool ok, uint256 at) {
            Stamp memory s = stamps[h];
            return (s.at != 0, s.at);
        }
    }

Gas cost: about 45,000 gas per anchor call. Cheap and predictable.

## 4. Backend Integration Points (lib/api_server.py)
Add a non-blocking background task so the UI never freezes.

    import hashlib, threading, json

    def _compute_hash(data_dict):
        canonical = json.dumps(data_dict, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _anchor_to_chain_async(hash_hex, agent_id, action):
        # TODO Tuesday: integrate web3.py or a lightweight relay here.
        print("[ANCHOR] queued: " + agent_id + " " + action + " -> " + hash_hex)
        # 1. connect to Sepolia via Infura or Alchemy
        # 2. build tx: contract.functions.anchor(bytes32(hash_hex))
        # 3. sign with the key from .env (the chain wallet var)
        # 4. send tx, wait for the receipt
        # 5. update memory.sqlite3: tx_hash = receipt transactionHash
        pass

## 5. UI Changes (lib/app.html)
1. New state: anchoring (yellow dot) between idle and on-chain (green check).
2. Badge: replace LOCAL with ON-CHAIN plus an Etherscan tx link.
3. On Save in Add Agent: the button shows Saving and Anchoring for about 15s.

## 6. Execution Milestones (Tuesday onwards)
M1: deploy StratoflyAnchor to Sepolia via Remix, save ABI and address (1h)
M2: write lib/chain_relay.py with web3.py for signing and sending (2h)
M3: hook _anchor_to_chain_async into /api/agent/add and /api/onboard (1h)
M4: update app.html to poll tx_hash and show the badge (1.5h)
M5: test the full flow: add agent, wait 15s, open Etherscan, verify (1h)

## 7. Guardrails (non-negotiable)
1. NEVER store private keys in settings.json. Use .env (the chain wallet var).
2. NEVER store raw config or memory text on-chain. Only the sha256 hash.
3. NEVER block the HTTP thread waiting for the chain. Use background threads.
4. Fallback: if the RPC is down, the backend save MUST still succeed. The
   anchor is a bonus, never a hard dependency.

## 8. Security Check
This spec contains NO real API keys, NO wallet addresses, and NO literal names
of private ecosystem repos. Safe to commit to the public engine docs/.
