# check_anchor_abi.py - diagnose deployed getAnchor arity via raw eth_call return length.
from lib import onboard
from web3 import Web3

e = onboard._read_env()
w3 = Web3(Web3.HTTPProvider(e["SEPOLIA_RPC_URL"]))
addr = e["STRATOFLY_CONTRACT_ADDRESS"]
sel = w3.keccak(text="getAnchor(string)")[:4].hex()
arg = "0"*62+"20" + "0"*62+"05" + "73636f7574".ljust(64, "0")  # offset=32, len("scout")=5, data
res = w3.eth.call({"to": Web3.to_checksum_address(addr), "data": "0x"+sel+arg})
print("return bytes:", len(res))
print("=> deployed getAnchor returns:", 2 if len(res) == 192 else (3 if len(res) == 224 else "?"), "values")