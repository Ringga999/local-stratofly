import time
from config import REPOS, REPORTS_DIR, brain_for
from lib import gh, memory, provider_hub
from lib.persona import system_prompt

EXTRA = """
You operate inside the zcp2o-maintainer system.
- Analyze ONLY the issues listed in the user message.
- Output ONLY a markdown table with columns:
  | Repo | # | Type | Priority | Summary | Action |
- Summary: max 2 sentences, clear English.
- Action: one concrete recommendation (add label / request info / good first issue / close duplicate / escalate to owner).
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
        memory.log_event("scout", "idle", "patrol", "-", "No new issues")
        return "🕵️ Patrol complete: no new issues since last run."
    table = provider_hub.think(brain_for("scout"), system_prompt("scout", EXTRA),
                               _brief(fresh), agent_id="scout")
    rid = _save_report(table)
    memory.log_event("scout", "alert", "triage_issue", f"{len(fresh)} issues",
                     f"{len(fresh)} new issues triaged", rid)
    return table