import time
from config import SCOUT_MODEL, REPOS, REPORTS_DIR
from lib import nim, gh, memory
from lib.persona import system_prompt

EXTRA = """
You operate inside the zcp2o-maintainer system.
- Analyze ONLY the issues listed in the user message.
- Output ONLY a markdown table with columns:
  | Repo | # | Type | Priority | Ringkasan (ID) | Aksi |
- Ringkasan: max 2 kalimat, Bahasa Indonesia.
- Aksi: satu rekomendasi konkret (add label / request info / good first issue / close duplicate / escalate to owner).
"""

def _brief(issues) -> str:
    lines = [f"- {i['repo']} #{i['number']} | {i['title']} | labels: {', '.join(i['labels']) or '-'}"
             for i in issues]
    return "Issues to triage:\n" + "\n".join(lines)

def _save_report(table: str) -> int:
    rid = int(time.time())
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / f"report_{rid}.md").write_text(table, encoding="utf-8")
    return rid

def patrol() -> str:
    fresh = []
    for repo in REPOS:
        for iss in gh.open_issues(repo, limit=15):
            if not memory.is_seen(iss["repo"], iss["number"]):
                fresh.append(iss)
                memory.mark_seen(iss["repo"], iss["number"], "new")
    if not fresh:
        memory.log_event("scout", "idle", "patrol", "-", "Tidak ada issue baru")
        return "🕵️ Patroli selesai: tidak ada issue baru sejak terakhir kali."
    table = nim.ask(SCOUT_MODEL, system_prompt("scout", EXTRA), _brief(fresh))
    rid = _save_report(table)
    memory.log_event("scout", "alert", "triage_issue", f"{len(fresh)} issue",
                     f"{len(fresh)} issue baru tertriase", rid)
    return table