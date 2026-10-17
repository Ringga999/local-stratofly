import random, time
from lib import memory

MOCK_AGENTS = {
    'scout': {'emoji': '🕵️', 'actions': ['triage_issue', 'patrol']},
    'triage': {'emoji': '🔍', 'actions': ['review_pr']},
    'sentinel': {'emoji': '🛡️', 'actions': ['security_scan', 'patrol']},
    'scribe': {'emoji': '📝', 'actions': ['write_docs', 'coffee']},
    'tester': {'emoji': '🧪', 'actions': ['ci_check']},
    'medic': {'emoji': '🚑', 'actions': ['crash_watch']},
    'release': {'emoji': '📦', 'actions': ['release_prep']},
    'bridge': {'emoji': '🔌', 'actions': ['drift_check']},
    'herald': {'emoji': '📣', 'actions': ['draft_post']},
    'diplomat': {'emoji': '🕊️', 'actions': ['mention_sweep']},
}

STATES = ['idle', 'working', 'patrol', 'coffee', 'alert']

def run(interval=3):
    print(f"🎭 Mock mode started. One event every {interval}s. Ctrl+C to stop.")
    while True:
        agent_id = random.choice(list(MOCK_AGENTS.keys()))
        state = random.choice(STATES)
        action = random.choice(MOCK_AGENTS[agent_id]['actions'])
        bubble = f"{MOCK_AGENTS[agent_id]['emoji']} {agent_id} is {action}…"
        memory.update_agent_state(agent_id, state, action, '-', bubble, -1)
        memory.log_event(agent_id, state, action, '-', bubble, -1)
        print(f"  [{agent_id}] {state} · {action}")
        time.sleep(interval)