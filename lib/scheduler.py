import time, threading
from lib import memory
from agents import scout

AGENT_ORDER = [
    'scout', 'triage', 'sentinel', 'scribe', 'tester',
    'medic', 'release', 'bridge', 'herald', 'diplomat'
]

CADENCE = {
    'scout': 6*3600, 'triage': 6*3600, 'sentinel': 6*3600,
    'scribe': 12*3600, 'tester': 6*3600,
    'medic': 12*3600, 'release': 12*3600, 'bridge': 12*3600,
    'herald': 4*3600, 'diplomat': 4*3600,
}

def _set(agent, state, action, target, bubble, report_id=-1):
    memory.update_agent_state(agent, state, action, target, bubble, report_id)
    memory.log_event(agent, state, action, target, bubble, report_id)

def _run_agent(agent_id):
    try:
        if agent_id == 'scout':
            _set('scout', 'working', 'triage_issue', '-', 'Scout sedang patroli…')
            result = scout.patrol()
            _set('scout', 'idle', 'patrol', '-', 'Patroli selesai')
        else:
            _set(agent_id, 'idle', '-', '-', f'{agent_id} belum diimplementasi')
    except Exception as e:
        _set(agent_id, 'alert', 'error', '-', f'Error: {str(e)[:60]}')

def run_once():
    for agent_id in AGENT_ORDER:
        _run_agent(agent_id)

def run_daemon():
    last_run = {a: 0 for a in AGENT_ORDER}
    print("🫀 Scheduler dimulai. Tekan Ctrl+C untuk berhenti.")
    while True:
        now = time.time()
        for agent_id in AGENT_ORDER:
            if now - last_run[agent_id] >= CADENCE[agent_id]:
                print(f"⏰ {agent_id} waktunya patroli")
                threading.Thread(target=_run_agent, args=(agent_id,)).start()
                last_run[agent_id] = now
        time.sleep(60)