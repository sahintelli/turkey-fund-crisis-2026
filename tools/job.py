"""Job 15 (dossier v7). Slow, single-threaded KAP collection; untouched files + sha256 manifest in job_out/job15/.
(C) August 2026 portfolio-distribution reports of public funds of the seven managers, and (D) KAP disclosures checked by
company name inside time windows: Hedef Holding default (29.09), end of the PEKGY tender (25.09), Hedef Portföy statement (21.09),
Pusula Portföy redemption-default notice (15.09). KAP disclosure IDs are sequential in time; pages located by binary search."""
import re, json, time, hashlib, subprocess
from datetime import datetime
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
O = Path("job_out/job15"); T0 = time.time(); man = []
(O / "reports").mkdir(parents=True, exist_ok=True)
S = requests.Session(); S.headers.update(H)
IN = json.loads(Path("tools/job15_input.json").read_text())
def fetch(url, pause=2.2):
    for k in range(4):
        time.sleep(pause + 20 * k * k)
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
# (C)+(D) windows
cache = {}
def page(i):
    if i in cache: return cache[i]
    r = fetch(f"https://www.kap.org.tr/tr/Bildirim/{i}", pause=2.0)
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
found = {}
for w in IN["windows"]:
    if time.time() - T0 > 3000: break
    if "scan" in w: ids = range(w["scan"][0], w["scan"][1])
    else:
        a = find(datetime.fromisoformat(w["time"]), w["lo"], w["hi"]); ids = range(a - w.get("back", 10), a + w.get("span", 60))
    want = dict(w["funds"])
    for j in ids:
        dt, txt = page(j)
        for code, name in want.items():
            if name in txt:
                d = O / "reports" / code; d.mkdir(exist_ok=True); (d / f"KAP{j}.html").write_text(txt)
                for fid in sorted(set(re.findall(r"(4028328[0-9a-f]{25})", txt))):
                    rr = fetch(f"https://www.kap.org.tr/tr/api/file/download/{fid}")
                    if rr is not None and rr.ok and len(rr.content) > 500: (d / f"KAP{j}_file_{fid}").write_bytes(rr.content)
                found.setdefault(code, []).append([j, str(dt), "Portföy Dağılım Raporu" in txt])
    (O / "reports_found.json").write_text(json.dumps(found, indent=1)); commit("job15 " + w["id"])
commit("job15 done"); print(found)
