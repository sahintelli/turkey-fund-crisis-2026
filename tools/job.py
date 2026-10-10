"""Job 6: locate specific KAP disclosures by send-time (IDs are sequential), then save their
pages and attachments. Targets: DFI and THF monthly portfolio reports (Jul/Aug 2026)."""
import re, json, time, hashlib, subprocess
from datetime import datetime
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
S = requests.Session(); S.headers.update(H)
O = Path("job_out/kap_find"); O.mkdir(parents=True, exist_ok=True)
man, cache = [], {}

def commit(msg):
    (O / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)

def page(i):
    if i in cache: return cache[i]
    for k in range(4):
        time.sleep(1.0 + 3 * k)
        try: r = S.get(f"https://www.kap.org.tr/tr/Bildirim/{i}", timeout=60)
        except requests.RequestException: continue
        if r.status_code == 429: time.sleep(20); continue
        man.append({"url": r.url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest()})
        t = r.text
        ms = re.findall(r"(\d\d\.\d\d\.\d{4} \d\d:\d\d:\d\d)", t)
        dt = datetime.strptime(ms[IDX], "%d.%m.%Y %H:%M:%S") if len(ms) > IDX else None
        cache[i] = (dt, t); return cache[i]
    cache[i] = (None, ""); return cache[i]

IDX = 0
_, t0 = page(1664344); cache.pop(1664344, None)
ms0 = re.findall(r"(\d\d\.\d\d\.\d{4} \d\d:\d\d:\d\d)", t0)
(O / "calib_1664344.html").write_text(t0)
print("calibration dates:", ms0[:10])
IDX = ms0.index("16.09.2026 20:35:10") if "16.09.2026 20:35:10" in ms0 else 0
print("IDX", IDX)

def find(target, lo=1600000, hi=1690000):
    while hi - lo > 40:
        mid = (lo + hi) // 2
        for j in range(mid, mid + 12):          # skip ids without a page
            dt, _ = page(j)
            if dt: break
        if not dt: lo = mid; continue
        if dt < target: lo = mid
        else: hi = mid
        print("bs", mid, dt)
    return lo

TARGETS = [("DFI", "2026-09-02 18:42:58"), ("THF", "2026-09-02 11:02:16"), ("DFI", "2026-08-10 10:36:08"), ("DFI", "2026-09-16 18:19:25")]
found = {}
for code, ts in TARGETS:
    t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    base = find(t)
    hit = None
    for j in range(base - 60, base + 160):
        dt, txt = page(j)
        if dt and abs((dt - t).total_seconds()) <= 1 and ("Portföy Dağılım" in txt):
            hit = j; break
    print(code, ts, "->", hit)
    found[f"{code} {ts}"] = hit
    if hit:
        d = O / f"{code}_{hit}"; d.mkdir(exist_ok=True)
        (d / "page.html").write_text(cache[hit][1])
        for fid in sorted(set(re.findall(r"api/file/download/([0-9a-f]{32})", cache[hit][1]))):
            r = S.get(f"https://www.kap.org.tr/tr/api/file/download/{fid}", timeout=90)
            man.append({"url": r.url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest()})
            (d / f"file_{fid}").write_bytes(r.content)
        for fid in sorted(set(re.findall(r"(4028328[0-9a-f]{25})", cache[hit][1]))):
            r = S.get(f"https://www.kap.org.tr/tr/api/file/download/{fid}", timeout=90)
            if r.ok and len(r.content) > 1000 and (b"%PDF" in r.content[:200] or r.content[:2] in (b"PK", b"\xd0\xcf") or r.content[:2] == b"\xac\xed"): (d / f"file2_{fid}").write_bytes(r.content)
    (O / "found.json").write_text(json.dumps(found, indent=1))
    commit(f"job6 {code}")
print(found)
