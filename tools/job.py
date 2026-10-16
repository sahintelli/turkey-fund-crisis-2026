"""Job 14 (dossier v7, seven managers). Slow, single-threaded KAP collection; untouched files + sha256 manifest in job_out/job14/.
(A) KAP 'genel' company pages: portfolio managers, group brokers, venture-capital trusts, and companies in the
    stake notices of Pardus/Bulls/A1/Atlas/Hedef funds.
(B) Fund 'ozet' pages for funds without a known KAP object id, then yearly notice bundles 2026 (missing funds)
    and 2025 (all liquidated funds).
(C) August 2026 portfolio-distribution reports of public funds: KAP disclosure pages located by send time
    (IDs are sequential in time), matched on the fund name, plus their attached files."""
import re, json, time, hashlib, subprocess, unicodedata
from datetime import datetime
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
O = Path("job_out/job14"); T0 = time.time(); man = []
for sub in ("company", "fund", "bundles2026", "bundles2025", "reports"): (O / sub).mkdir(parents=True, exist_ok=True)
S = requests.Session(); S.headers.update(H)
IN = json.loads(Path("tools/job14_input.json").read_text())
def fetch(url, pause=1.6):
    for k in range(4):
        time.sleep(pause + 25 * k * k)
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
# (A) company pages
for tk, pl in IN["companies"].items():
    if (O / "company" / f"{tk}_genel.html").exists(): continue
    r = fetch(f"https://www.kap.org.tr/tr/sirket-bilgileri/genel/{pl}")
    if r is not None and r.ok: (O / "company" / f"{tk}_genel.html").write_text(r.text)
commit("job14 A companies")
# (B) fund ozet pages -> object ids; bundles
def slugify(s):
    s = s.replace("İ", "I").replace("ı", "i").lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")
obj = dict(IN["obj"])
for code in IN["need_ozet"]:
    cands = [IN["slugs"][code]] if code in IN["slugs"] else []
    base = slugify(code + " " + IN["names"][code])
    cands += [base, base + "u" if base.endswith("-fon") else base, base.replace("-tl-", "-"), re.sub(r"-hisse-senedi-yogun(-fon)?$", "-hisse-senedi-yogun-fon", base)]
    for c in dict.fromkeys(cands):
        r = fetch(f"https://www.kap.org.tr/tr/fon-bilgileri/ozet/{c}")
        if r is None or not r.ok: continue
        m = re.search(r'generalInfo\\?":\{\\?"objId\\?":\\?"([0-9a-f]{32})', r.text)
        if m:
            (O / "fund" / f"{code}_ozet.html").write_text(r.text); obj[code] = m.group(1); print("ozet", code, c); break
(O / "fund_objids.json").write_text(json.dumps(obj, indent=1)); commit("job14 B ozet")
for code in IN["need_2026"]:
    if code in obj and not (O / "bundles2026" / f"{code}_2026.zip").exists():
        r = fetch(f"https://www.kap.org.tr/tr/api/batch-news/file-by-year/{obj[code]}/2026")
        if r is not None and r.ok and len(r.content) > 200: (O / "bundles2026" / f"{code}_2026.zip").write_bytes(r.content)
commit("job14 B 2026")
for i, code in enumerate(sorted(obj)):
    if code not in IN["names"] or (O / "bundles2025" / f"{code}_2025.zip").exists(): continue
    r = fetch(f"https://www.kap.org.tr/tr/api/batch-news/file-by-year/{obj[code]}/2025")
    if r is not None and r.ok and len(r.content) > 200: (O / "bundles2025" / f"{code}_2025.zip").write_bytes(r.content)
    if i % 40 == 39: commit("job14 B 2025 part")
commit("job14 B 2025")
# (C) August reports
cache = {}
def page(i):
    if i in cache: return cache[i]
    r = fetch(f"https://www.kap.org.tr/tr/Bildirim/{i}", pause=1.3)
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
    if time.time() - T0 > 3100: break
    if "scan" in w: ids = range(w["scan"][0], w["scan"][1])
    else:
        a = find(datetime.fromisoformat(w["time"]), w["lo"], w["hi"]); ids = range(a - 15, a + 60)
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
    (O / "reports_found.json").write_text(json.dumps(found, indent=1)); commit("job14 C " + w["id"])
commit("job14 done"); print(found)
