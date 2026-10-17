import sqlite3, time
from config import DB_PATH

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS seen_issues(
        repo TEXT, number INTEGER, first_seen REAL, last_state TEXT,
        PRIMARY KEY(repo, number))""")
    con.execute("""CREATE TABLE IF NOT EXISTS activity_log(
        ts REAL, agent TEXT, state TEXT, action TEXT, target TEXT,
        bubble TEXT, report_id INTEGER)""")
    con.execute("""CREATE TABLE IF NOT EXISTS agent_state(
        agent TEXT PRIMARY KEY,
        state TEXT,
        action TEXT,
        target TEXT,
        bubble TEXT,
        report_id INTEGER,
        since_ts REAL)""")
    return con

def is_seen(repo: str, number: int) -> bool:
    with _conn() as con:
        row = con.execute("SELECT 1 FROM seen_issues WHERE repo=? AND number=?",
                          (repo, number)).fetchone()
    return row is not None

def mark_seen(repo: str, number: int, state: str):
    with _conn() as con:
        con.execute("INSERT OR REPLACE INTO seen_issues VALUES (?,?,?,?)",
                    (repo, number, time.time(), state))

def log_event(agent, state, action, target, bubble, report_id=-1):
    with _conn() as con:
        con.execute("INSERT INTO activity_log VALUES (?,?,?,?,?,?,?)",
                    (time.time(), agent, state, action, target, bubble, report_id))

def recent_events(limit: int = 50):
    with _conn() as con:
        rows = con.execute(
            "SELECT ts,agent,state,action,target,bubble,report_id FROM activity_log ORDER BY ts DESC LIMIT ?",
            (limit,)).fetchall()
    return [dict(zip(("ts","agent","state","action","target","bubble","report_id"), r)) for r in rows]

def update_agent_state(agent, state, action, target, bubble, report_id=-1):
    with _conn() as con:
        con.execute("INSERT OR REPLACE INTO agent_state VALUES (?,?,?,?,?,?,?)",
                    (agent, state, action, target, bubble, report_id, time.time()))

def get_all_agent_states():
    with _conn() as con:
        rows = con.execute(
            "SELECT agent,state,action,target,bubble,report_id,since_ts FROM agent_state ORDER BY rowid"
        ).fetchall()
    return [dict(zip(("agent","state","action","target","bubble","report_id","since_ts"), r)) for r in rows]