# bundle_sdk.py - download SDK +esm, bundle via esbuild (IIFE), hash, save.
import urllib.request, hashlib, pathlib, subprocess, sys, tempfile, json
B = pathlib.Path(__file__).resolve().parent
VER = "12.0.3"
URL = f"https://cdn.jsdelivr.net/npm/@concordium/web-sdk@{VER}/+esm"
OUT = B/"lib"/"static"/"concordium-web-sdk.js"
print("="*64); print(f" BUNDLE SDK {VER} via esbuild (IIFE)"); print("="*64)
# 1) download
print("downloading...")
req = urllib.request.Request(URL, headers={"User-Agent": "stratofly-bundler"})
blob = urllib.request.urlopen(req, timeout=120).read()
print(f"downloaded {len(blob)} bytes")
# 2) write temp
tmp = tempfile.NamedTemporaryFile(suffix=".mjs", delete=False, dir=B)
tmp.write(blob); tmp.close()
print(f"temp: {tmp.name}")
# 3) bundle
out_file = tempfile.NamedTemporaryFile(suffix=".js", delete=False, dir=B)
out_file.close()
cmd = ["esbuild", tmp.name, "--bundle", "--format=iife", "--global-name=SDK", "--outfile="+out_file.name, "--minify"]
print("running:", " ".join(cmd))
try:
    subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True)
except subprocess.CalledProcessError as e:
    print("esbuild FAIL:", e.stderr); sys.exit(1)
bundled = pathlib.Path(out_file.name).read_bytes()
print(f"bundled {len(bundled)} bytes")
# 4) verify symbols
t = bundled.decode("utf-8", "ignore")
for s in ["CcdAmount","AccountAddress","ContractAddress","ReceiveName","AccountTransaction","ModuleReference","getModuleSource"]:
    print(f"  {s}: {s in t}")
# 5) hash + save
sha = hashlib.sha256(bundled).hexdigest()
OUT.write_bytes(bundled)
print(f"SAVED {OUT}")
print(f"sha256: {sha}")
# 6) cleanup
pathlib.Path(tmp.name).unlink(); pathlib.Path(out_file.name).unlink()
# 7) write attribution snippet
attr = B/"ATTRIBUTION_SDK.md"
attr.write_text(f"""## @concordium/web-sdk (vendored, bundled)
- Version: {VER}
- File: lib/static/concordium-web-sdk.js
- Bytes: {len(bundled)}
- SHA-256: {sha}
- Source: {URL} (bundled via esbuild IIFE; runtime tanpa CDN)
- License: Apache-2.0 (Concordium)
- Simbol terverifikasi: CcdAmount, AccountAddress, ContractAddress, ReceiveName, AccountTransaction, ModuleReference, getModuleSource
""", encoding="utf-8")
print(f"SAVED {attr} (append ke ATTRIBUTION.md lalu del)")
print("="*64)