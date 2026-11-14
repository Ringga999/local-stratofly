# Role Modules Blueprint

Peta kontribusi Stratofly: 10 role x modul yang perlu dibangun. Satu sel = satu unit kerja yang bisa diambil satu developer. Ambil sel berstatus `planned`, bangun, tandai `done` di PR yang sama.

**Status:** `done` = hidup di UI + endpoint | `partial` = backend ada, UI belum | `planned` = belum ada apa-apa.

## Aturan Main

1. Pilih satu sel `planned` di bawah; komentari issue/PR supaya tidak dobrol.
2. Branch: `feature/<role>-<modul>` (contoh: `feature/crafter-code-diff`).
3. Backend bersifat aditif: endpoint baru di `lib/api_server.py` atau modul baru di `lib/`; jangan memindahkan file engine.
4. UI: render modul di seksi modal agen (`lib/app.html`), daftarkan label di `moduleLabels`.
5. Gerbang wajib: `python main.py serve` + verifikasi mata sendiri + clean-clone test untuk perubahan engine.
6. Commit: `feat(<role>): <modul> ...`; PR menyebut sel blueprint; update status sel di dokumen ini dalam PR yang sama.
7. Jangan pernah commit `.env`, `settings.json`, `memory.sqlite3`.

## Solver

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| delegation | Papan sub-tugas hasil dekomposisi Solver | `/api/solve`, `/api/delegate` (ada) | board + tombol run | done |
| upload | Input multi-modal (PDF/gambar/link) sebagai konteks | baru: `/api/upload` | dropzone + pratinjau | planned |
| simulation | Jalankan rencana dalam mode simulasi tanpa efek nyata | baru: `/api/simulate` | timeline + hasil dry-run | planned |
| draft_queue | Antrean draf keputusan menunggu approval manusia | baru: `/api/drafts` | daftar + approve/reject | planned |

## Architect

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| audit_viewer | Penampil laporan audit struktur repo | baru: `/api/audit/<id>` | laporan ber-seksi | planned |
| dependency_graph | Graf dependensi antar modul (teks) | baru: `/api/graph` | tree/adjacency list | planned |
| redesign_editor | Editor proposal redesign struktur | baru: `/api/redesign` | diff proposal | planned |

## Crafter

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| spec_input | Form spesifikasi tugas kode terstruktur | baru: `/api/spec` | form + validasi | planned |
| code_diff | Penampil diff kode hasil kerja agen | baru: `/api/diff/<id>` | diff ber-warna | planned |
| test_runner | Jalankan tes dan tampilkan hasil | baru: `/api/test/run` | log + ringkasan pass/fail | planned |
| pr_creator | Buat PR dari perubahan ter-approve | pakai `lib/gh.py` + baru: `/api/pr` | tombol + link PR | planned |

## Analyst

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| research_input | Form topik + sumber riset | baru: `/api/research` | form + sumber | planned |
| source_list | Daftar sumber dengan sitasi | baru: `/api/sources/<id>` | daftar ber-link | planned |
| trend_chart | Grafik tren (render teks) | baru: `/api/trend` | chart teks/ascii | planned |
| report_gen | Generator laporan markdown + daftar | `/api/report/<id>` + `/api/reports` | viewer laporan di modal | done |

## Communicator

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| platform_selector | Pilih platform tujuan (X/LinkedIn/devlog) | baru: `/api/comms/draft` | dropdown platform | planned |
| tone_selector | Pilih nada suara draf | sama di atas | dropdown tone | planned |
| draft_composer | Penyusun draf konten | sama di atas | editor draf | planned |
| approval_queue | Antrean approval sebelum kirim | pakai `lib/telegram_gateway.py` + baru: `/api/approvals` | daftar + approve | partial |
| mention_monitor | Pantau mention & ringkas sentimen | baru: `/api/mentions` | feed mention | planned |

## Sentinel

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| scope_selector | Pilih scope audit (repo/PR/dependensi) | baru: `/api/security/scan` | dropdown scope | planned |
| cve_dashboard | Dasbor CVE dependensi | sama di atas | tabel severity | planned |
| breaking_flags | Penanda perubahan breaking | baru: `/api/security/flags` | daftar flag | planned |
| compliance_checklist | Checklist kepatuhan lisensi/kebijakan | baru: `/api/security/compliance` | checklist | planned |

## Operator

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| routine_list | Daftar rutinitas + tombol jalankan | pakai `lib/scheduler.py` + baru: `/api/routines` | daftar + run | partial |
| handoff_timeline | Linimasa serah terima antar agen | `/api/activity` (ada) | timeline | planned |
| pipeline_health | Kesehatan pipeline patroli | baru: `/api/health/pipeline` | indikator | planned |
| ops_summary | Ringkasan operasional periodik | baru: `/api/ops/summary` | kartu ringkasan | planned |
| alert_log | Log alert kronologis | baru: `/api/alerts` | feed alert | planned |

## VideoEditor

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| script_editor | Editor naskah + voiceover text | baru: `/api/video/script` | editor teks | planned |
| shot_list | Daftar shot terstruktur | baru: `/api/video/shots` | tabel shot | planned |
| render_queue | Antrean job render + status | baru: `/api/video/render` | antrean + retry | planned |
| asset_library | Pustaka aset (clip/audio/subtitle) | baru: `/api/video/assets` | grid aset | planned |
| publish_approval | Gerbang approval sebelum publish | baru: `/api/video/approve` | tombol approve | planned |

## SocialMedia

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| platform_selector | Pilih platform (X/IG/TikTok/LinkedIn) | pakai ulang komponen Communicator | dropdown | planned |
| tone_selector | Nada per platform | pakai ulang komponen Communicator | dropdown | planned |
| draft_composer | Penyusun draf posting | pakai ulang komponen Communicator | editor | planned |
| approval_queue | Antrean approval draft-first | pakai ulang komponen Communicator | daftar + approve | planned |
| schedule_calendar | Kalender jadwal posting | baru: `/api/social/schedule` | kalender sederhana | planned |

## DataScientist

| Modul | Definisi | Endpoint | State UI | Status |
|---|---|---|---|---|
| dataset_input | Unggah/tunjuk dataset (csv/json) | baru: `/api/data/upload` | dropzone + profil kolom | planned |
| notebook_runner | Jalankan langkah analisis reproducible | baru: `/api/data/run` | log langkah | planned |
| chart_gallery | Galeri chart (render teks/markdown) | baru: `/api/data/charts` | galeri | planned |
| model_card | Kartu model: metrik + asumsi | baru: `/api/data/modelcard` | kartu | planned |
| report_gen | Laporan analisis markdown | pakai ulang Analyst report_gen (viewer role-agnostic) | viewer di modal | done |

## Engine cells (cross-cutting)

| Cell | Definition | Endpoint | UI state | Status |
|---|---|---|---|---|
| role-consolidation | Unify the persona houses: one data scheme for per-agent `.md` and role JSON, precedence preserved and tested | refactor `lib/persona.py` + `lib/role_registry.py` | none | planned |
| telegram_listener | Inbound Telegram handler (`/start`, draft approval) so the bot can reply, not only send | polling loop or webhook in `lib/telegram_gateway.py` | approval buttons | planned |
| contract-reconciliation | Redeploy StratoflyAnchor from repo source with verified compiler (v0.8.34 + Optimization 200 runs); Etherscan verified; update docs with new address | redeploy + verify | Read Contract tab | done |