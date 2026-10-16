"""Job 13: primary-source checks. (A) Borsa Istanbul listing ('gong') announcements 14900-15700: which broker led each
2026 IPO. (B) KAP disclosures by company name inside time windows (sequential IDs, binary search):
PASEU 29.04.2026 (share transfer to Pusula PHB fund), ANELE 03.09.2026 (SPK application, chairman's shares),
PASEU 27-28.09.2026 (statement on fund claims). Untouched pages + sha256 manifest under job_out/job13/."""
import re, json, time, hashlib, subprocess, threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
O = Path("job_out/job13"); (O / "bist").mkdir(parents=True, exist_ok=True); (O / "kap").mkdir(parents=True, exist_ok=True)
man, lock, T0 = [], threading.Lock(), time.time()
tl = threading.local()
def sess():
    if not hasattr(tl, "s"): tl.s = requests.Session(); tl.s.headers.update(H)
    return tl.s
def fetch(url):
    for k in range(3):
        time.sleep(0.3 + 2 * k)
        try: r = sess().get(url, timeout=60)
        except requests.RequestException: continue
        with lock: man.append({"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest()})
        return r
    return None
def commit(msg):
    with lock: (O / "manifest.json").write_text(json.dumps(man, indent=0, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
# (A) Borsa Istanbul announcements
hits = {}
def bist(i):
    r = fetch(f"https://borsaistanbul.com/duyuru/{i}/")
    if not r or not r.ok: return
    t = r.text
    m = re.search(r"<title>(.*?)</title>", t, re.S); title = m.group(1).strip() if m else ""
    if "gong" in title.lower() or "gong" in t[:20000].lower():
        (O / "bist" / f"{i}.html").write_text(t)
        txt = re.sub(r"<[^>]+>", " ", t); txt = re.sub(r"\s+", " ", txt)
        with lock: hits[i] = {"title": title, "tera": "Tera" in txt, "alb": "ALB" in txt or "Alb Yatırım" in txt, "pusula": "Pusula" in txt,
                              "lead": re.findall(r"([A-ZÇĞİÖŞÜ][\wçğıöşüÇĞİÖŞÜ\. ]{2,60}?(?:Yatırım|Menkul)[\wçğıöşü\. ]{0,40}?)(?: Genel Müdürü| liderliğinde| konsorsiyum)", txt)[:4]}
with ThreadPoolExecutor(6) as ex: list(ex.map(bist, range(14900, 15700)))
(O / "bist_gong.json").write_text(json.dumps(hits, indent=1, ensure_ascii=False)); print("bist gong pages:", len(hits)); commit("job13 bist")
# (B) KAP
cache = {}
def page(i):
    if i in cache: return cache[i]
    r = fetch(f"https://www.kap.org.tr/tr/Bildirim/{i}")
    if not r or not r.ok: cache[i] = (None, ""); return cache[i]
    ms = re.findall(r"(\d\d\.\d\d\.\d{4} \d\d:\d\d:\d\d)", r.text)
    cache[i] = (datetime.strptime(ms[0], "%d.%m.%Y %H:%M:%S") if ms else None, r.text); return cache[i]
def find(target, lo=1590000, hi=1700000):
    while hi - lo > 30:
        mid = (lo + hi) // 2; dt = None
        for j in range(mid, mid + 10):
            dt, _ = page(j)
            if dt: break
        if not dt: lo = mid; continue
        if dt < target: lo = mid
        else: hi = mid
    return lo
W = [("PASEU_2904", "2026-04-29 15:00:00", "2026-04-30 10:00:00", "PASİFİK EURASIA"),
     ("ANELE_0309", "2026-09-03 08:00:00", "2026-09-04 09:30:00", "ANEL ELEKTRİK"),
     ("PASEU_2709", "2026-09-26 12:00:00", "2026-09-28 12:00:00", "PASİFİK EURASIA")]
res = {}
for key, a, b, name in W:
    ia, ib = find(datetime.fromisoformat(a)), find(datetime.fromisoformat(b))
    ids = list(range(ia, ib + 30)); print(key, ia, ib, len(ids), round(time.time() - T0))
    found = []
    def chk(j):
        dt, txt = page(j)
        if name in txt:
            d = O / "kap" / key; d.mkdir(exist_ok=True); (d / f"{j}.html").write_text(txt)
            with lock: found.append((j, str(dt)))
    with ThreadPoolExecutor(6) as ex: list(ex.map(chk, ids))
    for j, _ in found:
        for fid in sorted(set(re.findall(r"(4028328[0-9a-f]{25})", cache[j][1]))):
            rr = fetch(f"https://www.kap.org.tr/tr/api/file/download/{fid}")
            if rr and rr.ok and len(rr.content) > 500: (O / "kap" / key / f"{j}_file_{fid}").write_bytes(rr.content)
    res[key] = {"range": [ia, ib], "found": sorted(found)}
    (O / "kap_found.json").write_text(json.dumps(res, indent=1, ensure_ascii=False)); commit(f"job13 {key}")
    if time.time() - T0 > 3000: break
commit("job13 done"); print(res)
