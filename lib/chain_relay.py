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
                 {"internalType": "uint256", "name": "", "type": "uint256"},
                 {"internalType": "address", "name": "", "type": "address"}],
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
        from eth_account import Account
        return Account.from_key(k).address
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
        "signer": get_signer(),
        "last_user_tx": _STATE.get("last_user_tx"),
        "last_user_wallet": _STATE.get("last_user_wallet"),
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
        try:
            est = c.functions.anchor(agent_id, mem_hash).estimate_gas({"from": acct.address})
            gas_limit = int(est * 1.3) + 10000
        except Exception:
            gas_limit = 300000
        tx = c.functions.anchor(agent_id, mem_hash).build_transaction({
            "from": acct.address, "nonce": nonce, "chainId": 11155111,
            "gas": gas_limit, "gasPrice": w3.eth.gas_price,
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


def read_anchor(agent_id):
    """Read latest on-chain anchor for an agent (hash, timestamp, owner)."""
    if not WEB3_OK:
        return {"ok": False, "error": "web3 not installed"}
    try:
        e = _env()
        rpc = e.get("SEPOLIA_RPC_URL") or "https://rpc.sepolia.org"
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
        if not w3.is_connected():
            return {"ok": False, "error": "rpc unreachable"}
        addr = Web3.to_checksum_address((e.get("STRATOFLY_CONTRACT_ADDRESS") or "").strip())
        c = w3.eth.contract(address=addr, abi=ABI)
        h, ts, owner = c.functions.getAnchor(agent_id).call()
        return {"ok": True, "agent": agent_id, "memory_hash": h,
                "timestamp": int(ts), "owner": owner}
    except Exception as ex:
        return {"ok": False, "error": str(ex)}

def prepare_anchor_payload(agent_id, payload, user_address):
    """Build unsigned tx payload for frontend wallet signing (User-Owned)."""
    if not WEB3_OK:
        return {"ok": False, "error": "web3 not installed"}
    try:
        e = _env()
        rpc = e.get("SEPOLIA_RPC_URL") or "https://rpc.sepolia.org"
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 10}))
        if not w3.is_connected():
            return {"ok": False, "error": "rpc unreachable"}
        
        addr = Web3.to_checksum_address((e.get("STRATOFLY_CONTRACT_ADDRESS") or "").strip())
        c = w3.eth.contract(address=addr, abi=ABI)
        mem_hash = "0x" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        # Normalize user address to EIP-55 checksum (wallets may send lowercase)
        if not Web3.is_address(user_address):
            return {"ok": False, "error": "invalid user address"}
        user_address = Web3.to_checksum_address(user_address)
        # Get nonce for the USER'S wallet, not admin
        nonce = w3.eth.get_transaction_count(user_address)
        
        tx = c.functions.anchor(agent_id, mem_hash).build_transaction({
            "from": user_address,
            "nonce": nonce,
            "chainId": 11155111,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "value": 0
        })
        # MetaMask requires every numeric field as a 0x-hex STRING, not int/bytes.
        def _hx(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, int):
                return hex(v)
            if isinstance(v, (bytes, bytearray)):
                return "0x" + bytes(v).hex()
            s = str(v)
            if s.startswith("0x"):
                return s
            if s.isdigit():
                return hex(int(s))
            return s
        payload = {
            "from": tx["from"],
            "to": tx["to"],
            "nonce": _hx(tx["nonce"]),
            "gas": _hx(tx["gas"]),
            "gasPrice": _hx(tx["gasPrice"]),
            "value": _hx(tx.get("value", 0)),
            "data": _hx(tx.get("data", "0x")),
            "chainId": _hx(tx["chainId"]),
        }
        return {"ok": True, "payload": payload}
    except Exception as ex:
        return {"ok": False, "error": str(ex)}

def get_signer():
    try:
        return (settings.load().get("memory_signer") or "admin")
    except Exception:
        return "admin"

def set_signer(mode):
    mode = "user" if str(mode).strip() == "user" else "admin"
    d = settings.load(); d["memory_signer"] = mode; settings.save(d); return mode

def confirm_user_anchor(agent_id, tx_hash, user_address):
    try:
        memory.log_event(agent_id, "chain", "anchor", "-", tx_hash, -1)
    except Exception:
        pass
    with _LOCK:
        _STATE["last_tx"] = tx_hash
        _STATE["last_user_tx"] = tx_hash
        _STATE["last_user_wallet"] = user_address
        _STATE["last_error"] = None
        _STATE["last_ts"] = time.time()
    return {"ok": True}

def anchor_memory_async(agent_id, payload):
    if get_mode() != "hybrid":
        return
    if get_signer() == "user":
        return
    threading.Thread(target=_anchor_job, args=(agent_id, payload), daemon=True).start()
