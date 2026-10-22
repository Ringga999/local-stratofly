# TEAM ROSTER v2 — 10 Agen, Tiga Sayap

> Versi: 2.0 · 11 Oktober 2026 · Menggantikan roster 5 agen awal
> Sumber kebenaran persona: folder `agents/personas/`

## Sayap A — Protokol & Repo (kadens: patroli tiap 6 jam)

| id | Nama | Emoji | Warna | Persona | Tugas |
|---|---|---|---|---|---|
| scout | Scout | 🕵️ | #4FC3F7 | scout.md | Triage issue lintas repo |
| triage | Triage | 🔍 | #BA68C8 | triage.md | Review PR |
| sentinel | Sentinel | 🛡️ | #FFB74D | sentinel.md | Audit keamanan & dependensi |
| scribe | Scribe | 📝 | #AED581 | scribe.md | Dokumentasi & changelog |
| tester | Tester | 🧪 | #F06292 | tester.md | Analisis hasil CI/test |

## Sayap B — Stratofly Applications (kadens: patroli tiap 12 jam + event release)

Scope: semua app yang berdiri di atas protokol — contoh aplikasi ekosistem,


| id | Nama | Emoji | Warna | Persona | Tugas |
|---|---|---|---|---|---|
| medic | Medic | 🚑 | #EF5350 | medic.md | Insiden & bug app: pantau issue bug/crash, kesehatan release, alert regresi |
| release | Release | 📦 | #4DB6AC | release.md | Release engineer: versioning, draft changelog, checklist build/Play Store, sanity manifest & aset |
| bridge | Bridge | 🔌 | #90A4AE | bridge.md | Kompatibilitas protokol↔app: pantau drift API/SDK (versi embed captcha, ZWS handshake, kontrak registry), tandai breaking change |

## Sayap C — Sosmed & Komunitas (kadens: sweep mention tiap 4 jam, digest harian 08:00)

Scope: X/Twitter, GitHub Discussions, devlog bulanan.

| id | Nama | Emoji | Warna | Persona | Tugas |
|---|---|---|---|---|---|
| herald | Herald | 📣 | #FFD54F | herald.md | Menyusun draft postingan/thread/devlog dari aktivitas mingguan ekosistem |
| diplomat | Diplomat | 🕊️ | #80DEEA | diplomat.md | Memantau mention & pertanyaan komunitas, menyusun draft balasan, eskalasi isu sensitif |

## DOKTRIN SAYAP C (WAJIB)

1. **Draft-first:** semua keluaran Sayap C berupa draft di `reports/drafts/`
   + notifikasi Telegram. TIDAK ADA posting otomatis pada v1.
2. Persetujuan hanya dari Mr Visioner via Telegram (`/approve <id>` — Fase 9+).
3. Draft kadaluarsa 7 hari bila tidak disetujui.

## Urutan tetap array `agents` (kontrak API & game)

scout, triage, sentinel, scribe, tester, medic, release, bridge, herald, diplomat
