#!/usr/bin/env python3
"""
sniper_run_all.py

1) Auth & inject kite into utils
2) Run engine → trades.json
3) Append to trade_history.json
4) Push both to GitHub
5) Self‑tune params
"""
import os, json, base64, requests, pathlib
from datetime import date
import kite_patch
from token_manager import refresh_if_needed
import utils
from config import PARAMS_FILE

kite=refresh_if_needed()
utils.set_kite(kite)

from sniper_engine import generate_sniper_trades

trades=generate_sniper_trades()
with open("trades.json","w") as f: json.dump(trades,f,indent=2)
print(f"💾 trades.json ({len(trades)})")

H=pathlib.Path("trade_history.json")
hist=json.loads(H.read_text()) if H.exists() else []
hist.append({"run_date":date.today().isoformat(),"trades":trades})
H.write_text(json.dumps(hist,indent=2))
print(f"🗄 trade_history.json ({len(hist)} runs)")

def push(path):
    token=os.getenv("GITHUB_TOKEN")
    if not token: return
    repo="balakumar75/sniper-p2-dashboard"
    api=f"https://api.github.com/repos/{repo}/contents/{path}"
    hdr={"Authorization":f"token {token}","Accept":"application/vnd.github.v3+json"}
    b64=base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    r=requests.get(api,headers=hdr)
    sh=r.json().get("sha") if r.status_code==200 else None
    payload={"message":f"Auto-update {path}","content":b64,"branch":"main"}
    if sh: payload["sha"]=sh
    ok=requests.put(api,headers=hdr,data=json.dumps(payload))
    print(f"{'✅' if ok.status_code<300 else '❌'} push {path}")

push("trades.json")
push("trade_history.json")

PERF=pathlib.Path("performance.json")
try: rec=json.loads(PERF.read_text()) if PERF.exists() else []
except: rec=[]
if rec:
    adx_tr=[r for r in rec if r.get("adx",0)<ADX_MIN]
    sl=[r for r in adx_tr if r.get("result")=="SL"]
    if adx_tr and len(sl)/len(adx_tr)>0.6:
        np={"RSI_MIN":55,"ADX_MIN":22,"VOL_MULTIPLIER":1.5}
        PARAMS_FILE.write_text(json.dumps(np,indent=2))
        print("🔧 tuned ADX_MIN")
    else: print("ℹ no tune")
else: print("ℹ no perf")
print("✅ done")
