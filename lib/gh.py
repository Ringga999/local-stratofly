import shutil, subprocess
from github import Github, Auth
from config import GITHUB_TOKEN

def token_mode() -> str:
    if GITHUB_TOKEN:
        return "pat"
    if shutil.which("gh"):
        try:
            out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                return "gh-cli"
        except Exception:
            pass
    return "anon"

def _client():
    mode = token_mode()
    if mode == "pat":
        return Github(auth=Auth.Token(GITHUB_TOKEN))
    if mode == "gh-cli":
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        return Github(auth=Auth.Token(out.stdout.strip()))
    return Github()

def open_issues(repo_name: str, limit: int = 15):
    try:
        repo = _client().get_repo(repo_name)
        out = []
        for issue in repo.get_issues(state="open"):
            if issue.pull_request:
                continue
            out.append({
                "repo": repo_name,
                "number": issue.number,
                "title": issue.title,
                "labels": [l.name for l in issue.labels],
            })
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []