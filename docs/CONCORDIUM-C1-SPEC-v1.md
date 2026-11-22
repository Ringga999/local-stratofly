# CONCORDIUM-C1-SPEC v1.1 — Register Agent + Badge (User-Owned)



**Status:** DESIGN terkunci-menunggu-review. Belum ada kode engine. Implementasi = "gas adapter" setelah review; submit pertama = uji terawasi 23 Nov (build window).

**Menggantikan:** v1 (22 Nov siang). Delta v1.1: jalur submit diputuskan dari fakta probe (SDK primary), fakta testnet lengkap, aturan network-eksplisit, Plan C hash-verified module, sponsor turun jadi stretch.

**Scope:** C1 (register CIS-8004 + badge) + fondasi C3 (card ter-host + pin hash). C2 = spec terpisah. Track produk (sesi 2) TIDAK disentuh.

**Doktrin:** kode pendek/efisien; doc panjang/detail; jelaskan→"gas"→kode; anchor terverifikasi; gerbang mata; fail-closed; user-owned signing; \[PROBE] di luar repo; pakta 3–4 percobaan.



\---



## 1. Fakta Terverifikasi (probe 21–22 Nov + sumber resmi)



| # | Fakta | Sumber |

|---|---|---|

| F1 | Wallet inject 17 method; `sendTransaction(acc, type, payload, parameters, schema, schemaVersion)`; parameters diteruskan sebagai JSON bigint-safe; payload dinormalisasi `wo()`; schema ditangani normalizer internal | probe P1b/P10 + README api-helpers |

| F2 | `sendSponsoredTransaction(acc, transaction, schema)` menuntut instance Transaction (`ei.toJSON`) → butuh SDK; sponsor = stretch (kita punya 20.000 CCD testnet) | probe P10 + tutorial sponsored |

| F3 | `getSelectedChain` = genesis hash hex / undefined bila locked; getter akun bisa undefined walau connected → bukan penentu chain | README api-helpers + probe 21 Nov |

| F4 | Chain assert halaman: gRPC `getCryptographicParameters().genesisString` = "Concordium Testnet Version 5"; height 51.100.862n (BigInt) | probe P7/P9 |

| F5 | Builder MCP mengembalikan `{parameter_json, parameter_hex, receive_name, contract_address, suggested_energy, sender, network}` — **TIDAK ada schema_json** (docs lama ≠ realita versi ini) | probe v1/v2 |

| F6 | Testnet: CIS-8004 = **12802,0**, CIS-8 = **12801,0**, module_ref `0e574737…7d3eb`, admin `3whdieGHx…vajR8`, explorer `https://testnet.ccdscan.io`, node `grpc.testnet.concordium.com:20000` | probe v2 contract_info |

| F7 | Encoding parameter: Option = `{"None":\[]}` / `{"Some":\[nilai]}`; `metadata_hash` Some = **array 32 byte angka** (bentuk hex string = kandidat kedua); `token_id` setAgentURI = string hex 16 char (CIS-2 TokenIdU64); energy 30000 | probe v2 build_register/build_set_agent_uri |

| F8 | receiveName: `CIS-8004.register` dan `CIS-8004.setAgentURI` | probe v2 |

| F9 | Transport wallet **menolak byte mentah dari luar SDK**: 4 varian request getModuleSource (snake/bytes/array/base64) → INVALID_ARGUMENT/Error; wrapper menelan pesan jadi `Error('')` | probe P11/P11b/P11c |

| F10 | Registry row TANPA field name; testnet punya 5 agent, semua milik satu deployer, semua card 404 → nama hanya dari card; card wajib dibangun sendiri | probe v1/v2 card hunt |

| F11 | Baseline confirm: `agents_by_owner(4NYP…) = {count:0,total:0,agents:\[]}` | probe v2 |

| F12 | `build_agent_card` menghasilkan card gabungan ERC-8004+A2A: field `url`, modes, `capabilities.extensions` badge (pre-mint `tokenAddress:null`), owner CAIP-10 `ccd:4221332d34e1694168c2a0c0b3fd0f27:…`; `build_agent_badge` wajib card_json/card_url | probe v2 + docs Agent Card |

| F13 | **Module ref = SHA-256 module source** → bytes dari sumber mana pun dapat dibuktikan identik on-chain via hash, tanpa wallet | CIS-8004/spec Concordium |

| F14 | Default server MCP = **mainnet**; semua tool menerima `network` optional → wajib eksplisit testnet | probe v1 (insiden mainnet) + openapi |



## 2. Keputusan Jalur Submit (inti v1.1)



| Jalur | Status | Alasan |

|---|---|---|

| **PRIMARY: web-sdk vendored** | dipilih | SDK mengetahui serialisasi transport wallet (F9), menyediakan schema via getModuleSource, typed payload (GtuAmount/ContractAddress/ReceiveName), dan Transaction untuk sponsored kelak |

| Vanilla (parameters JSON + schema base64 manual) | stretch | schema tak bisa diambil lewat transport wallet (F9); hanya hidup bila schema diperoleh dari Plan C DAN payload polos diterima (uji 23 Nov) |

| Sponsored/gasless | stretch (C5) | butuh SDK + endpoint sponsor (OQ-2); tidak diperlukan karena saldo testnet kita cukup |



**Vendoring SDK (aturan):** unduh SEKALI via skrip `\[PROBE]` (python urllib): versi dari `https://registry.npmjs.org/@concordium/web-sdk/latest`, bundle ESM dari `https://cdn.jsdelivr.net/npm/@concordium/web-sdk@<ver>/+esm`; hitung sha256; simpan `lib/static/concordium-web-sdk.js`; catat versi+sha256 di jurnal & ATTRIBUTION.md (lisensi Apache-2.0); app.html memuat via `<script type="module">` lokal + atribut integrity. Runtime TIDAK menyentuh CDN → local-first & offline terjaga; CDN hanya sumber unduhan satu kali.



**Plan C (fallback schema, ber-anchor hash):** bila SDK getModuleSource gagal: unduh bytes module dari sumber publik mana pun, hitung sha256, **wajib sama dengan `0e574737…7d3eb`** (F13) sebelum dipakai; parse custom section `concordium-schema*` (parser wasm yang sudah teruji di probe); base64 → schema. Hash cocok = bukti on-chain; hash beda = buang.



## 3. Alur C1 (tujuh langkah, fail-closed)



1\. **Connect + assert chain.** `requestAccounts()` → akun. Assert: genesisString mengandung "Testnet" (F4) + semua panggilan MCP bawa `network:"testnet"` (F14). Gagal → tolak, pesan manusiawi.

2\. **Card dulu.** Backend panggil `build_agent_card` (name/description/skills dari config agen, owner, agent_uri publik) → card JSON + sha256. Host di URL publik pilihan penulis (OQ-4; default: raw GitHub/gist publik) + mirror lokal `/.well-known/agent-card.json`. Tanpa URL publik → verify match mustahil → chip jujur "unpinned".

3\. **Prepare register.** Backend `build_register(network=testnet, sender, agent_uri, metadata_hash_hex)` → parameter_json/parameter_hex/receive_name/contract/energy (F5–F8). Konversi bytes32: sediakan KEDUA bentuk (array byte & hex string) untuk uji SDK (OQ-8).

4\. **Submit (SDK, popup consent user).** `sendTransaction(acc, UpdateSmartContractInstance, {amount:GtuAmount(0n), contractAddress:ContractAddress(12802n,0n), receiveName:"CIS-8004.register", maxContractExecutionEnergy:30000n}, parameters, schema, schemaVersion)`. Reject/timeout → status rejected/unknown, retry boleh; tidak ada silent submit.

5\. **Confirm tanpa node sendiri.** Backend poll `agents_by_owner(4NYP…)` diff vs baseline (F11) → token_id baru → `token_address(12802,0,token_id)` → `get_badge_json` → persist mapping. Latency indexer = OQ-6; status `pending` jujur sampai record terbaca; tx_hash = bukti submit, bukan bukti final.

6\. **Badge + pin.** `build_agent_badge(card_json, owner, token_id)` → card merged + sha256 baru → re-host → `build_set_agent_uri(token_id, metadata_hash_hex=baru, sender)` → submit SDK → `verify_agent_card.match == true` wajib sebelum chip hijau.

7\. **UI + audit.** Kartu `CONCORDIUM · IDENTITY (C1)` additive: chips session/card/registered/badge/match, link testnet.ccdscan.io tx+token, tombol verify ulang, kill-switch sesi. Semua langkah `memory.log_event(agent,"ccd",action,target,reason)` dengan status approved/pending/rejected/failed.



## 4. Endpoint & Model Data



Mapping kv `ccd_agent_<id>`: `{agent_id, owner, token_id, token_address, network:"testnet", tx_register, tx_pin, card_uri, card_hash, badge_valid, card_match, registered_at, status}`. BigInt → string sebelum JSON.



| Endpoint | Method | Isi |

|---|---|---|

| /api/ccd/session | POST | {account, genesis_string} → assert testnet, simpan sesi |

| /api/ccd/card | POST | {agent_id, owner, public_base_url} → card_json, card_hash, card_uri |

| /api/ccd/prepare | POST | {agent_id, owner, agent_uri, metadata_hash} → payload prepare (F5) + dua bentuk bytes32 |

| /api/ccd/confirm | POST | {agent_id, account, tx_hash} → pending/registered/failed + token_id + badge_json |

| /api/ccd/pin | POST | {agent_id, token_id, card_hash, sender} → payload setAgentURI |

| /api/ccd/status | GET | mapping + badge_valid + card_match + links |



Config ccd TIDAK lewat `_apply_patch` (allowlist menolak key asing — pola M26); endpoint sendiri.



## 5. Aturan Keselamatan



1\. Testnet-only triple assert: genesisString wallet + `network:"testnet"` eksplisit di SEMUA panggilan MCP/REST + index 12802 dari contract_info(testnet). Mainnet = tolak keras.

2\. User-owned signing saja; engine/frontend tidak memegang key Concordium; tidak ada seed.

3\. Fail-closed: chain/health/quota/card-uri tidak terassert → tolak aksi, pesan manusiawi.

4\. BigInt → string; JSON tanpa BigInt mentah.

5\. Card hanya data publik; tanpa PII pihak ketiga; tanpa secret.

6\. Rate limit MCP: hormati 429 + Retry-After, backoff.

7\. Kill-switch sesi CCD membatalkan poll & menolak submit baru.

8\. Tidak ada klaim hijau tanpa bukti: badge dari check_badge, match dari verify_agent_card, final dari record on-chain.

9\. SDK vendored ber-hash tercatat; runtime tanpa CDN; ATTRIBUTION diperbarui.

10\. Pakta 3–4 percobaan berlaku untuk uji bentuk payload 23 Nov; lewat budget → tunda tanpa malu, fallback Plan C/SDK.



## 6. Mode Kegagalan



| Kegagalan | Perilaku |

|---|---|

| Wallet locked / popup bisu / reject | status rejected/unknown + panduan unlock; retry boleh |

| SDK getModuleSource gagal | Plan C hash-verified module (F13); hash beda = buang |

| Payload bytes32 ditolak SDK | coba bentuk kedua (hex↔array); budget pakta; catat pemenang |

| MCP down/429 | antre + backoff; memory lokal tetap hidup |

| Indexer lag | status pending + poll terbatas; jangan klaim registered |

| Card tidak publik / match null | chip abu + instruksi hosting; register boleh lanjut dengan label jujur |

| Energi kurang / reject contract | terjemahkan kode -7200…-7213 manusiawi; status failed |



## 7. Open Questions (sisa)



| OQ | Isi | Resolusi | Kapan |

|---|---|---|---|

| OQ-2 | Endpoint sponsor (gasless) untuk register | docs/search; stretch C5 | Sprint-2 |

| OQ-4 | Pilihan hosting card publik (default raw GitHub/gist) | keputusan penulis | 22 Nov malam |

| OQ-6 | Latency indexer untuk confirm; batas poll | uji 23 Nov | 23 Nov |

| OQ-7 | Versi + sha256 SDK vendored | skrip probe unduh | 22 Nov malam / 23 Nov pagi |

| OQ-8 | Bentuk bytes32 yang diterima serializer SDK (hex vs array) | uji terawasi 23 Nov | 23 Nov |



## 8. Gerbang & Milestone



\- Clean-clone invariant: tanpa wallet/SDK/MCP server tetap hidup; kartu CCD jujur "not connected".

\- Mock mode tidak terpengaruh; kartu CCD additive tanpa merombak control room.

\- Uji integrasi pertama = register testnet terawasi 23 Nov dengan audit penuh.

\- 22 Nov malam: review spec ini + keputusan OQ-4. 23 Nov: probe unduh SDK (OQ-7) → "gas adapter" → prep → submit terawasi. 24–29 Nov: C3 pin stabil + office hours. 30 Nov–5 Des: demo + A1/A2. 9 Des: submit A3.



## 9. Cross-Reference & Doktrin



Jurnal 21 Nov (probe signer/chain, aturan BigInt & fail-closed), jurnal 22 Nov (probe v1/v2/P10/P11), 19 Nov (C0/D1/no-KYC), 18 Nov roadmaping (sprint), engine docs INSTALL §7, blueprint engine cells. Track produk sesi 2 tidak disentuh. Prinsip §12 jurnal berlaku penuh, ditambah: network-eksplisit, typeof-gate sebelum probe wallet, dan hash-module sebagai anchor Plan C.

