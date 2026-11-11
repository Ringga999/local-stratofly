\# Role Modules Blueprint



Peta kontribusi Stratofly: 10 role x modul yang perlu dibangun. Satu sel = satu unit kerja yang bisa diambil satu developer. Ambil sel berstatus `planned`, bangun, tandai `done` di PR yang sama.



\*\*Status:\*\* `done` = hidup di UI + endpoint | `partial` = backend ada, UI belum | `planned` = belum ada apa-apa.



\## Aturan Main



1\. Pilih satu sel `planned` di bawah; komentari issue/PR supaya tidak dobrol.

2\. Branch: `feature/<role>-<modul>` (contoh: `feature/crafter-code-diff`).

3\. Backend bersifat aditif: endpoint baru di `lib/api\_server.py` atau modul baru di `lib/`; jangan memindahkan file engine.

4\. UI: render modul di seksi modal agen (`lib/app.html`), daftarkan label di `moduleLabels`.

5\. Gerbang wajib: `python main.py serve` + verifikasi mata sendiri + clean-clone test untuk perubahan engine.

6\. Commit: `feat(<role>): <modul> ...`; PR menyebut sel blueprint; update status sel di dokumen ini dalam PR yang sama.

7\. Jangan pernah commit `.env`, `settings.json`, `memory.sqlite3`.



\## Solver



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| delegation | Papan sub-tugas hasil dekomposisi Solver | `/api/solve`, `/api/delegate` (ada) | board + tombol run | done |

| upload | Input multi-modal (PDF/gambar/link) sebagai konteks | baru: `/api/upload` | dropzone + pratinjau | planned |

| simulation | Jalankan rencana dalam mode simulasi tanpa efek nyata | baru: `/api/simulate` | timeline + hasil dry-run | planned |

| draft\_queue | Antrean draf keputusan menunggu approval manusia | baru: `/api/drafts` | daftar + approve/reject | planned |



\## Architect



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| audit\_viewer | Penampil laporan audit struktur repo | baru: `/api/audit/<id>` | laporan ber-seksi | planned |

| dependency\_graph | Graf dependensi antar modul (teks) | baru: `/api/graph` | tree/adjacency list | planned |

| redesign\_editor | Editor proposal redesign struktur | baru: `/api/redesign` | diff proposal | planned |



\## Crafter



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| spec\_input | Form spesifikasi tugas kode terstruktur | baru: `/api/spec` | form + validasi | planned |

| code\_diff | Penampil diff kode hasil kerja agen | baru: `/api/diff/<id>` | diff ber-warna | planned |

| test\_runner | Jalankan tes dan tampilkan hasil | baru: `/api/test/run` | log + ringkasan pass/fail | planned |

| pr\_creator | Buat PR dari perubahan ter-approve | pakai `lib/gh.py` + baru: `/api/pr` | tombol + link PR | planned |



\## Analyst



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| research\_input | Form topik + sumber riset | baru: `/api/research` | form + sumber | planned |

| source\_list | Daftar sumber dengan sitasi | baru: `/api/sources/<id>` | daftar ber-link | planned |

| trend\_chart | Grafik tren (render teks) | baru: `/api/trend` | chart teks/ascii | planned |

| report\_gen | Generator laporan markdown | `/api/report/<id>` (ada) | viewer laporan | partial |



\## Communicator



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| platform\_selector | Pilih platform tujuan (X/LinkedIn/devlog) | baru: `/api/comms/draft` | dropdown platform | planned |

| tone\_selector | Pilih nada suara draf | sama di atas | dropdown tone | planned |

| draft\_composer | Penyusun draf konten | sama di atas | editor draf | planned |

| approval\_queue | Antrean approval sebelum kirim | pakai `lib/telegram\_gateway.py` + baru: `/api/approvals` | daftar + approve | partial |

| mention\_monitor | Pantau mention \& ringkas sentimen | baru: `/api/mentions` | feed mention | planned |



\## Sentinel



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| scope\_selector | Pilih scope audit (repo/PR/dependensi) | baru: `/api/security/scan` | dropdown scope | planned |

| cve\_dashboard | Dasbor CVE dependensi | sama di atas | tabel severity | planned |

| breaking\_flags | Penanda perubahan breaking | baru: `/api/security/flags` | daftar flag | planned |

| compliance\_checklist | Checklist kepatuhan lisensi/kebijakan | baru: `/api/security/compliance` | checklist | planned |



\## Operator



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| routine\_list | Daftar rutinitas + tombol jalankan | pakai `lib/scheduler.py` + baru: `/api/routines` | daftar + run | partial |

| handoff\_timeline | Linimasa serah terima antar agen | `/api/activity` (ada) | timeline | planned |

| pipeline\_health | Kesehatan pipeline patroli | baru: `/api/health/pipeline` | indikator | planned |

| ops\_summary | Ringkasan operasional periodik | baru: `/api/ops/summary` | kartu ringkasan | planned |

| alert\_log | Log alert kronologis | baru: `/api/alerts` | feed alert | planned |



\## VideoEditor



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| script\_editor | Editor naskah + voiceover text | baru: `/api/video/script` | editor teks | planned |

| shot\_list | Daftar shot terstruktur | baru: `/api/video/shots` | tabel shot | planned |

| render\_queue | Antrean job render + status | baru: `/api/video/render` | antrean + retry | planned |

| asset\_library | Pustaka aset (clip/audio/subtitle) | baru: `/api/video/assets` | grid aset | planned |

| publish\_approval | Gerbang approval sebelum publish | baru: `/api/video/approve` | tombol approve | planned |



\## SocialMedia



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| platform\_selector | Pilih platform (X/IG/TikTok/LinkedIn) | pakai ulang komponen Communicator | dropdown | planned |

| tone\_selector | Nada per platform | pakai ulang komponen Communicator | dropdown | planned |

| draft\_composer | Penyusun draf posting | pakai ulang komponen Communicator | editor | planned |

| approval\_queue | Antrean approval draft-first | pakai ulang komponen Communicator | daftar + approve | planned |

| schedule\_calendar | Kalender jadwal posting | baru: `/api/social/schedule` | kalender sederhana | planned |



\## DataScientist



| Modul | Definisi | Endpoint | State UI | Status |

|---|---|---|---|---|

| dataset\_input | Unggah/tunjuk dataset (csv/json) | baru: `/api/data/upload` | dropzone + profil kolom | planned |

| notebook\_runner | Jalankan langkah analisis reproducible | baru: `/api/data/run` | log langkah | planned |

| chart\_gallery | Galeri chart (render teks/markdown) | baru: `/api/data/charts` | galeri | planned |

| model\_card | Kartu model: metrik + asumsi | baru: `/api/data/modelcard` | kartu | planned |

| report\_gen | Laporan analisis markdown | pakai ulang Analyst report\_gen | viewer | partial |

