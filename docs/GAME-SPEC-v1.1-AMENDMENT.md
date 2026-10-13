# GAME-SPEC v1.1 AMENDMENT — Ruangan 10 Agen

> Mengikat bersama GAME-SPEC v1. Amandemen ini MENIMPA bagian:
> §4.1 (jumlah & urutan agents), §4.4 (data canned), §5 (tata ruang & roster visual).
> Bagian lain tidak berubah. Changelog: v1.1 (11 Okt 2026).

## A. §4.1 diganti — array agents berisi 10 entri

Urutan tetap:
scout, triage, sentinel, scribe, tester, medic, release, bridge, herald, diplomat

Skema tiap entri tidak berubah (id, state, action, target, bubble,
report_id, since_ts). Tujuh state tetap berlaku untuk semua sayap.

## B. §5 diganti — tata ruang 3 sayap

Room grid: 32 × 18 tile, tile 32 px → dunia 1024 × 576 px,
viewport 1280 × 720 (stretch keep aspect, pixel snap ON, kamera statis).

| id | Emoji | Warna tag | Posisi meja (tile x,y) |
|---|---|---|---|
| scout | 🕵️ | #4FC3F7 | (5,4) |
| triage | 🔍 | #BA68C8 | (11,4) |
| sentinel | 🛡️ | #FFB74D | patroli (waypoint bawah) |
| scribe | 📝 | #AED581 | (5,12) |
| tester | 🧪 | #F06292 | (11,12) |
| medic | 🚑 | #EF5350 | (21,4) |
| release | 📦 | #4DB6AC | (27,4) |
| bridge | 🔌 | #90A4AE | (24,8) |
| herald | 📣 | #FFD54F | (21,13) |
| diplomat | 🕊️ | #80DEEA | (27,13) |

Waypoint patroli sentinel (loop): (8,8) → (3,8) → (3,15) → (13,15) → (13,8) → (8,8)
Prop wajib tambahan: papan pengumuman Sayap C (dinding kanan bawah),
rak draft (dekat meja herald), kotak P3K (dekat meja medic).
Zona visual: Sayap A = karpet biru (kiri), Sayap B = karpet hijau (kanan atas),
Sayap C = karpet kuning (kanan bawah).

## C. §4.4 diganti — data canned 10 agen

```json
{ "schema":1, "online":true, "ts":0,
  "agents":[
   {"id":"scout","state":"working","action":"triage_issue","target":"zcp2o-protocol#42","bubble":"Issue #42: bug · prioritas high","report_id":17,"since_ts":0},
   {"id":"triage","state":"working","action":"review_pr","target":"notapeer-app#7","bubble":"PR #7: minta perubahan","report_id":18,"since_ts":0},
   {"id":"sentinel","state":"patrol","action":"security_scan","target":"-","bubble":"Scan: 0 celah baru","report_id":-1,"since_ts":0},
   {"id":"scribe","state":"coffee","action":"-","target":"-","bubble":"menunggu tugas…","report_id":-1,"since_ts":0},
   {"id":"tester","state":"alert","action":"ci_check","target":"zcp2o-protocol","bubble":"CI merah: 2 test gagal","report_id":19,"since_ts":0},
   {"id":"medic","state":"working","action":"crash_watch","target":"notapeer-app","bubble":"Crash rate naik 0.4%","report_id":20,"since_ts":0},
   {"id":"release","state":"walking","action":"release_prep","target":"zproai v0.1","bubble":"Siapkan checklist build","report_id":-1,"since_ts":0},
   {"id":"bridge","state":"working","action":"drift_check","target":"captcha embed v1.2","bubble":"Drift terdeteksi: widget v1.3","report_id":21,"since_ts":0},
   {"id":"herald","state":"working","action":"draft_post","target":"devlog okt","bubble":"Draft thread minggu ini","report_id":22,"since_ts":0},
   {"id":"diplomat","state":"idle","action":"mention_sweep","target":"-","bubble":"3 mention menunggu balasan","report_id":-1,"since_ts":0}
  ]}
```

## D. Catatan milestone

M1–M4 tidak berubah, kecuali DoD M1: "10 agen tampil dengan bubble".
Perilaku offline/reconnect (§8) berlaku untuk seluruh ruangan.