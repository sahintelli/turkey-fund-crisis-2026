"""Job 11: TEFAS daily asset allocation via api/funds/dagilimSiraliGetirDosya (endpoint name from the
user's script). Probe first; then collect ALL funds 2025-01-01..2026-09-30 in 30-day windows (empty
windows split 10/5/1 days). Untouched responses + sha256 manifest; every field kept (no column subset)."""
import json, time, hashlib, gzip, subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
import requests, pandas as pd
API = "https://www.tefas.gov.tr/api/funds/dagilimSiraliGetirDosya"
H = {"Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/json", "Referer": "https://www.tefas.gov.tr/",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
O = Path("tefas_alloc"); (O / "raw").mkdir(parents=True, exist_ok=True)
S = requests.Session(); S.headers.update(H); man = []
def commit(msg):
    (O / "manifest.json").write_text(json.dumps(man, indent=1))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add tefas_alloc job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
def body(code, a, b):
    return {"dil": "TR", "fonTipi": "YAT", "sfonTurKod": None, "fonKod": code, "fonGrup": None, "basTarih": a.strftime("%Y%m%d"),
            "bitTarih": b.strftime("%Y%m%d"), "fonTurKod": None, "fonUnvanTip": None, "kurucuKod": None, "fonTurAciklama": None}
def q(code, a, b):
    for k in range(4):
        time.sleep(2 + 8 * k)
        try:
            r = S.post(API, json=body(code, a, b), timeout=180)
            p = r.json()
        except Exception as e:
            print("err", e); continue
        rl = p.get("resultList") if isinstance(p, dict) else None
        if r.ok and isinstance(rl, list) and rl:
            return r.content, rl
        print("empty/err", r.status_code, str(p)[:200])
    return None, []
# probe
raw, rl = q("TLY", date(2026, 8, 1), date(2026, 8, 30))
probe = {"tly_rows": len(rl), "fields": sorted(rl[0].keys()) if rl else None, "first": rl[0] if rl else None}
raw2, rl2 = q(None, date(2026, 8, 3), date(2026, 8, 7))
probe.update({"all_rows": len(rl2), "all_funds": len({x.get("fonKodu") for x in rl2})})
(O / "probe.json").write_text(json.dumps(probe, indent=1, ensure_ascii=False)); print(probe)
commit("job11 probe")
if rl2:
    def chunks(a, b, n):
        while a <= b:
            e = min(a + timedelta(days=n - 1), b); yield a, e; a = e + timedelta(days=1)
    def fetch(a, b):
        tag = f"ALL_{a:%Y%m%d}_{b:%Y%m%d}"
        if (O / "raw" / f"{tag}.json.gz").exists(): return
        raw, res = q(None, a, b)
        print(tag, len(res))
        if raw:
            (O / "raw" / f"{tag}.json.gz").write_bytes(gzip.compress(raw))
            man.append({"request": tag, "rows": len(res), "sha256_uncompressed": hashlib.sha256(raw).hexdigest()})
        elif (b - a).days >= 1:
            n = 10 if (b - a).days >= 10 else (5 if (b - a).days >= 5 else 1)
            for x, y in chunks(a, b, n): fetch(x, y)
    for i, (a, b) in enumerate(chunks(date(2025, 1, 1), date(2026, 9, 30), 30)):
        fetch(a, b)
        if i % 4 == 3: commit(f"job11 alloc {a}")
    rows = []
    for f in sorted((O / "raw").glob("*.json.gz")):
        rows += json.loads(gzip.decompress(f.read_bytes())).get("resultList") or []
    df = pd.json_normalize(rows).drop_duplicates()
    df.to_csv(O / "tefas_alloc_daily.csv.gz", index=False, compression="gzip")
    print("saved", len(df), df.fonKodu.nunique() if "fonKodu" in df else "")
    commit("job11 done")
