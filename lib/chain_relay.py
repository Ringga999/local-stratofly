# lib/chain_relay.py - Web3 memory anchoring (Sepolia). Optional by design.
# Modes: "local" or "hybrid" (local + on-chain hash anchor). Default hybrid.
# Credentials ONLY from .env (gitignored). Never hardcoded, never logged raw.
import os, hashlib, threading, time

try:
    from web3 import Web3
    WEB3_OK = True
except Exception:
    Web3 = None
    WEB3_OK = False

from lib import settings, memory, onboard

_STATE = {"last_tx": None, "last_error": None, "last_ts": 0}
_LOCK = threading.Lock()

ABI = [
    {"inputs": [{"internalType": "string", "name": "agentId", "type": "string"},
                {"internalType": "string", "name": "memoryHash", "type": "string"}],
     "name": "anchor", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "agentId", "type": "string"}],
     "name": "getAnchor",
     "outputs": [{"internalType": "string", "name": "", "type": "string"},
                 {"internalType": "uint256", "name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"}
]

def _env():
    try:
        return onboard._read_env()
    except Exception:
        return {}

def get_mode():
    try:
        return (settings.load().get("memory_mode") or "hybrid")
    except Exception:
        return "hybrid"

def set_mode(mode):
    mode = "hybrid" if str(mode).strip() == "hybrid" else "local"
    d = settings.load()
    d["memory_mode"] = mode
    settings.save(d)
    return mode

def _wallet_address():
    try:
        if not WEB3_OK:
            return None
        k = (_env().get("STRATOFLY_CHAIN_KEY") or "").strip()
        if not k:
            return None
        return Web3.eth.account.from_key(k).address
    except Exception:
        return None

def _mask(addr):
    if not addr or len(addr) < 12:
        return "not-set"
    return addr[:6] + "..." + addr[-4:]

def is_configured():
    if not WEB3_OK:
        return False, "web3 not installed (local-only mode active)"
    if get_mode() != "hybrid":
        return False, "memory_mode is local"
    e = _env()
    if not (e.get("STRATOFLY_CHAIN_KEY") or "").strip():
        return False, "STRATOFLY_CHAIN_KEY missing in .env (local-only mode active)"
    if not (e.get("STRATOFLY_CONTRACT_ADDRESS") or "").strip():
        return False, "STRATOFLY_CONTRACT_ADDRESS missing in .env (local-only mode active)"
    return True, "ok"

def get_status():
    ok, why = is_configured()
    return {
        "mode": get_mode(),
        "web3_installed": WEB3_OK,
        "configured": ok,
        "reason": why,
        "rpc": (_env().get("SEPOLIA_RPC_URL") or "https://rpc.sepolia.org"),
        "wallet": _mask(_wallet_address()),
        "last_tx": _STATE["last_tx"],
        "last_error": _STATE["last_error"],
    }

def _anchor_job(agent_id, payload):
    try:
        ok, why = is_configured()
        if not ok:
            with _LOCK:
                _STATE["last_error"] = why
            return
        e = _env()
        rpc = e.get("SEPOLIA_RPC_URL") or "https://rpc.sepolia.org"
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
        if not w3.is_connected():
            raise RuntimeError("rpc unreachable - local copy kept, retry later")
        addr = Web3.to_checksum_address((e.get("STRATOFLY_CONTRACT_ADDRESS") or "").strip())
        c = w3.eth.contract(address=addr, abi=ABI)
        mem_hash = "0x" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
        key = (e.get("STRATOFLY_CHAIN_KEY") or "").strip()
        acct = w3.eth.account.from_key(key)
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = c.functions.anchor(agent_id, mem_hash).build_transaction({
            "from": acct.address, "nonce": nonce, "chainId": 11155111,
            "gas": 120000, "gasPrice": w3.eth.gas_price,
        })
        signed = w3.eth.account.sign_transaction(tx, key)
        raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction")
        hx = w3.eth.send_raw_transaction(raw).hex()
        with _LOCK:
            _STATE["last_tx"] = hx
            _STATE["last_error"] = None
            _STATE["last_ts"] = time.time()
        try:
            memory.log_event(agent_id, "chain", "anchor", "-", hx, -1)
        except Exception:
            pass
        print("[chain] anchored " + agent_id + " tx=" + hx)
    except Exception as ex:
        with _LOCK:
            _STATE["last_error"] = str(ex)
        print("[chain] anchor failed (local copy kept): " + str(ex))

def anchor_memory_async(agent_id, payload):
    if get_mode() != "hybrid":
        return
    threading.Thread(target=_anchor_job, args=(agent_id, payload), daemon=True).start()
