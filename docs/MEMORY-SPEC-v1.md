# MEMORY-SPEC v1 - Stratofly Agent Memory (division-scoped recollection)

Version: 1.0 | Date: 24 October 2026 | Status: DESIGN FROZEN (implementation scheduled)
Owners: Mr Architect & Mr Visioner
Source of truth: this document. Implementation must NOT ship before this
contract is signed off.

## 0. Summary and the one hard rule

Memory lets each division of a crew remember decisions, facts, and work
products, and recall them later. The hard architectural rule, born from a
real failure we already lived through (a vision model chosen for a text
agent, producing no table):

    HASH ON-CHAIN. BLOB OFF-CHAIN. ALWAYS.

The heavy text of a memory (the blob) never goes to the blockchain. Only a
32-byte fingerprint (sha256) plus a timestamp is anchored on-chain, which is
enough to prove "this memory has not been altered since time T" at near-zero
cost. This keeps the blockchain-trust pillar of PLATFORM-ARCHITECTURE true
without turning the chain into a storage bill or a demo-time single point of
failure.

## 1. Scope

IN scope v1:
- Memory data model (entries, scoped per division)
- Two operating modes: local (default) and chain (experimental switch)
- The anchor contract shape (for chain mode / the commercial app)
- The three UI views and the Agent-Verse metaphor
- Pricing doctrine (local free forever; chain = subscription)
- settings.json integration (memory block; schema target 3)

OUT of scope v1 (later):
- Vector/RAG semantic recall (Phase 12; v1 uses keyword + tag search)
- Cross-division memory sharing without explicit grant (privacy boundary)
- Any blob written to a chain (forbidden by section 0)

## 2. Storage architecture (three layers, one truth)

    Layer        Local engine (local-stratofly)     Commercial app (stratofly)
    -----------  ---------------------------------  --------------------------
    Blob (text)  SQLite table memory_entries        Supabase row + IPFS pin
    Hash         sha256 of blob, stored in row      same
    Anchor       none by default (mode=local)       testnet then mainnet (mode=chain)
    Proof URI    null                               Etherscan tx link

The blob location differs by product, but the SHAPE of an entry is identical,
so the engine and the app speak the same memory language.

## 3. Entry data model (one row = one memory)

    id              uuid / int, unique
    division        string  (memory is scoped per division, not per agent)
    agent_id        string  (who wrote it)
    kind            enum    decision | fact | artifact | instruction | note
    content_ref     string  pointer to blob (db row id / supabase key / ipfs cid)
    content_hash    bytes32 sha256 of the blob (the on-chain anchor payload)
    tx_hash         string|null  null in local mode; set once anchored
    anchored_at     int|null     unix ts of anchor; null in local mode
    created_at      int          unix ts of write
    tags            string[]     free labels for recall
    size_bytes      int          blob size (for quota)

Rules: content_hash is computed at write time and is immutable. If the blob
is ever edited, a NEW entry is created (append-only memory); the old hash
stays as history. This is what makes the on-chain proof meaningful.

## 4. Operating modes (the switch that protects the demo)

    memory.mode = "local"   (DEFAULT)
      - blob -> SQLite/Supabase; tx_hash = null; UI badge [LOCAL]
      - zero network, zero gas, zero faucet dependency
      - FREE FOREVER, even inside the paid app (the $0-modality promise)

    memory.mode = "chain"   (EXPERIMENTAL / PREMIUM)
      - same blob storage, PLUS anchor(content_hash) to the contract
      - tx_hash + anchored_at filled; UI badge [ON-CHAIN] + Etherscan link
      - requires a wallet + funded testnet account (or paid mainnet gas)

Hackathon doctrine: the demo runs in LOCAL mode. Chain mode is shown as a
mechanism (one click "anchor this memory") only if the faucet is willing,
and is NEVER a dependency of the core demo. If anchoring fails, the memory
still exists locally and the crew still works. Failure of the fancy layer
must never look like failure of the product.

## 5. The anchor contract (chain mode / commercial app only)

Deliberately tiny. It stores hashes, never blobs. Deploy via Remix to an ETH
testnet (Sepolia) for demos; mainnet later for production. This contract is
NOT imported by the engine in local mode, so it cannot break the demo.

    // SPDX-License-Identifier: Apache-2.0
    pragma solidity ^0.8.20;

    contract StratoflyMemoryAnchor {
        struct Stamp { bytes32 hash; uint256 at; address by; }
        mapping(bytes32 => Stamp) public stamps;     // hash -> proof
        mapping(address => uint256) public count;    // per-writer tally
        uint256 public total;

        event Anchored(bytes32 indexed hash, uint256 at, address by);

        function anchor(bytes32 h) external {
            require(h != bytes32(0), "empty hash");
            if (stamps[h].at == 0) {                 // first write wins
                stamps[h] = Stamp(h, block.timestamp, msg.sender);
                count[msg.sender] += 1;
                total += 1;
                emit Anchored(h, block.timestamp, msg.sender);
            }
        }

        function verify(bytes32 h) external view returns (bool ok, uint256 at) {
            Stamp memory s = stamps[h];
            return (s.at != 0, s.at);
        }
    }

Cost note: anchor() writes ~3 storage slots => cheap; verify() is a free
read. Because we anchor a 32-byte hash (not text), cost is bounded and
predictable regardless of how large the memory blob is. This is the entire
reason for the hash/blob split in section 0.

## 6. UI views (three surfaces + one metaphor)

    1. Memory Vault (per division)
       A digital archive shelf. List of entries: one-line preview, kind icon,
       tags, timestamp, and the mode badge [LOCAL] / [ON-CHAIN]. Filters by
       agent, date range, tag, kind. This is where a user browses what the
       division remembers.

    2. Recall
       A question box. User types "what did we decide about auth last week?"
       and the division's agents pull matching entries. v1 = keyword + tag
       match (deterministic, offline-friendly). Phase 12 upgrades to vector
       RAG. Recall is what makes a crew feel like it has long-term memory.

    3. Integrity Ledger
       The list of anchored hashes, each with a "verify on explorer" button.
       THIS is the jury wow-moment: they click, a browser opens the testnet,
       and the record is provably untouched. Trust made visible.

    Agent-Verse metaphor
       Each division's room gets a glass cabinet. Agents "file a note" into
       their division's cabinet. Anchored notes glow green (on-chain); local
       notes stay grey. Consistent with the product soul: you can SEE the
       crew work AND remember.

## 7. Pricing and the two-freedoms doctrine

    - local mode: FREE, forever, in BOTH products. A student with $0 must
      still have memory. This is non-negotiable (PLATFORM-ARCHITECTURE:
      free-tier first; $0 modality).
    - chain mode + large quotas: part of the Pro subscription ($5/mo, $35/yr)
      in the commercial app, because it carries real gas/infra cost.
    - in local-stratofly (this repo): everything is free, because this is the
      test bed before the stratofly app launches, and the hackathon venue.

So "Memory is a paid feature" is true only for the chain-backed premium tier
of the app. The capability itself is never paywalled at the floor.

## 8. settings.json integration (schema target 3)

A new top-level block (full schema in SETTINGS-SPEC v1.2):

    "memory": {
      "mode": "local",
      "per_division_quota_mb": 64,
      "retain_days": 0,                 // 0 = keep forever
      "chain": {
        "enabled": false,
        "network": "sepolia",
        "contract": "0x0000000000000000000000000000000000000000",
        "rpc": "",
        "wallet_env": "STRATOFLY_CHAIN_KEY"   // secret stays in .env, never here
      }
    }

The wallet PRIVATE KEY is referenced by env-var NAME only (wallet_env). The
key itself lives in .env. settings.json never holds a secret (global rule).

## 9. Non-negotiable constraints

- NEVER write a blob to a chain (section 0).
- NEVER store secrets in settings.json or in a memory blob by default; memory
  content is user data and must respect the same allow-list/privacy rules as
  the dashboard.
- Memory is division-scoped: an agent writes to ITS division; reading another
  division requires an explicit grant (privacy boundary, not a bug).
- In local-stratofly, the default mode is local and the default is FREE.
- The chain layer must be optional and must never be a demo dependency.

## 10. Implementation milestones (after this spec is signed)

    M1  engine local memory: SQLite table + lib/memory.py (write/recall/list)
        -> shipped with the S3 dashboard so the UI has real data
    M2  keyword + tag recall (offline)
    M3  chain anchor module lib/chain.py (experimental; app-side; Remix deploy
        guide) -> NOT required for the hackathon demo
    M4  vector RAG recall (Phase 12)

## 11. Changelog
- v1.0 (24 Oct 2026): hash-on-chain / blob-off-chain rule; local+chain modes;
  entry model; anchor contract shape; three UI views + Agent-Verse cabinet;
  pricing doctrine (local free forever); settings integration; milestones.
