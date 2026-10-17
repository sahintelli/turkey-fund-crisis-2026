"""Job 20: PKV weekly portfolio reports (weeks 35 and 39) by send time read from the job 19 bundle. Based on job 19:
PKV (Pardus Portföy Kısa Vadeli Serbest (TL) Fon, not liquidated) — KAP fund page, 2026 notice bundle and the
August 2026 portfolio report located by send time (read from the bundle) and matched on the stockCode field.
Slow, single-threaded; untouched files + sha256 manifest in job_out/job19/."""
import re, json, time, hashlib, subprocess, zipfile, io
from datetime import datetime, timedelta
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
O = Path("job_out/job20"); O.mkdir(parents=True, exist_ok=True); T0 = time.time(); man = []
S = requests.Session(); S.headers.update(H)
def fetch(url, pause=3.0):
    for k in range(4):
        time.sleep(pause + 45 * k * k)
        try: r = S.get(url, timeout=90)
        except requests.RequestException as e: print("ERR", url, e); continue
        man.append({"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest(), "t": round(time.time() - T0)})
        if r.status_code == 429: print("429", url); continue
        return r
    return None
def commit(msg):
    (O / "manifest.json").write_text(json.dumps(man, indent=0, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
    print(msg, round(time.time() - T0), "s")
sent = [("09.09.2026 18:26:47", 1660306, 1661633), ("06.10.2026 11:56:35", 1669389, 1690000)]
cache = {}
def page(i):
    if i in cache: return cache[i]
    r = fetch(f"https://www.kap.org.tr/tr/Bildirim/{i}", pause=2.8)
    if r is None or not r.ok: cache[i] = (None, ""); return cache[i]
    ms = re.findall(r"(\d\d\.\d\d\.\d{4} \d\d:\d\d:\d\d)", r.text)
    cache[i] = (datetime.strptime(ms[0], "%d.%m.%Y %H:%M:%S") if ms else None, r.text); return cache[i]
def find(target, lo, hi):
    while hi - lo > 20:
        mid = (lo + hi) // 2; dt = None
        for j in range(mid, mid + 6):
            dt, _ = page(j)
            if dt: break
        if not dt: lo = mid; continue
        if dt < target: lo = mid
        else: hi = mid
    return lo
found = []
for s, lo, hi in sent:
    t = datetime.strptime(s, "%d.%m.%Y %H:%M:%S")
    a = find(t, lo, hi)
    for j in range(a - 80, a + 40):
        if time.time() - T0 > 3200: break
        dt, txt = page(j)
        if 'stockCode\\":\\"PKV\\"' in txt or 'stockCode":"PKV"' in txt:
            (O / f"KAP{j}.html").write_text(txt)
            for fid in sorted(set(re.findall(r"(4028328[0-9a-f]{25})", txt))):
                rr = fetch(f"https://www.kap.org.tr/tr/api/file/download/{fid}")
                if rr is not None and rr.ok and len(rr.content) > 500: (O / f"KAP{j}_file_{fid}").write_bytes(rr.content)
            found.append([j, str(dt), "Portföy Dağılım Raporu" in txt])
(O / "found.json").write_text(json.dumps(dict(sent=sent, found=found), indent=1)); commit("job20 done"); print(found)
