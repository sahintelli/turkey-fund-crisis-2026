"""Probe: can this machine reach the TEFAS JSON API, and what does a response look like?
Writes a human-readable report to the path given as argv[1]. Exit code 0 = API usable."""
import json, sys, time
import requests
API = "https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetirDosya"
H = {"Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/json",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
     "Referer": "https://www.tefas.gov.tr/"}
def body(code, a, b):
    return {"dil": "TR", "fonTipi": "YAT", "sfonTurKod": None, "fonKod": code, "fonGrup": None,
            "basTarih": a, "bitTarih": b, "fonTurKod": None, "fonUnvanTip": None, "kurucuKod": None,
            "fonTurAciklama": None}
out, ok = [], False
for label, code, a, b in [("TLY one month", "TLY", "20260801", "20260830"),
                          ("ALL funds 5 days", None, "20260803", "20260807")]:
    time.sleep(2)
    out.append(f"== {label} ==")
    try:
        r = requests.post(API, json=body(code, a, b), headers=H, timeout=120)
        out.append(f"HTTP {r.status_code}, {len(r.content)} bytes, content-type {r.headers.get('content-type')}")
        try:
            p = r.json()
            rl = p.get("resultList") or []
            out.append(f"keys: {list(p)[:20]}; errorCode={p.get('errorCode')}; rows={len(rl)}")
            if rl:
                out.append("first row: " + json.dumps(rl[0], ensure_ascii=False)[:1500])
                out.append(f"distinct funds: {len({x.get('fonKodu') for x in rl})}")
                if code == "TLY": ok = True
        except ValueError:
            out.append("not JSON; first 800 chars: " + r.text[:800])
    except requests.RequestException as e:
        out.append(f"request failed: {e!r}")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(0 if ok else 1)
