"""Job 7: (a) KAP monthly/weekly portfolio-report pages + attachments located by send-time
(TLY, TP2 Jun/Jul/Aug; TLY 09.09; PRY/PNU Aug; HKJ Aug); (b) SPK 2026 bulletin PDFs."""
import re, json, time, hashlib, subprocess
from datetime import datetime
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
S = requests.Session(); S.headers.update(H)
O = Path("job_out/kap_find2"); O.mkdir(parents=True, exist_ok=True)
man, cache = [], {}

def commit(msg):
    (O / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)

def fetch(url, tries=4):
    for k in range(tries):
        time.sleep(0.8 + 3 * k)
        try: r = S.get(url, timeout=90)
        except requests.RequestException: continue
        if r.status_code == 429: time.sleep(20); continue
        man.append({"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest()})
        return r
    return None

# ---- (b) SPK bulletins first (small)
try:
    r = fetch("https://spk.gov.tr/spk-bultenleri/2026-yili-spk-bultenleri")
    (O / "spk_2026_index.html").write_text(r.text)
    links = sorted(set(re.findall(r'href="([^"]+\.pdf)"', r.text)))
    want = [l for l in links if re.search(r"2026[-_/ ]?(34|5[89]|6\d)\b", l)]
    print("SPK pdf links:", len(links), "wanted:", want)
    for l in want:
        u = l if l.startswith("http") else "https://spk.gov.tr" + l
        rr = fetch(u.replace(" ", "%20"))
        if rr and rr.ok:
            (O / ("spk_" + re.sub(r"[^A-Za-z0-9_.-]", "_", l.split("/")[-1]))).write_bytes(rr.content)
    commit("job7 spk")
except Exception as e:
    print("SPK failed", e)

def page(i):
    if i in cache: return cache[i]
    r = fetch(f"https://www.kap.org.tr/tr/Bildirim/{i}")
    if not r: cache[i] = (None, ""); return cache[i]
    ms = re.findall(r"(\d\d\.\d\d\.\d{4} \d\d:\d\d:\d\d)", r.text)
    dt = datetime.strptime(ms[0], "%d.%m.%Y %H:%M:%S") if ms else None
    cache[i] = (dt, r.text); return cache[i]

def find(target, lo=1612000, hi=1666000):
    while hi - lo > 40:
        mid = (lo + hi) // 2
        dt = None
        for j in range(mid, mid + 12):
            dt, _ = page(j)
            if dt: break
        if not dt: lo = mid; continue
        if dt < target: lo = mid
        else: hi = mid
    return lo

T = [("2026-09-02 11:02:16", ["TERA PORTFÖY BİRİNCİ SERBEST FON", "TERA PORTFÖY PARA PİYASASI (TL) FONU"]),
     ("2026-08-03 18:14:56", ["TERA PORTFÖY BİRİNCİ SERBEST FON", "TERA PORTFÖY PARA PİYASASI (TL) FONU"]),
     ("2026-07-02 00:50:14", ["TERA PORTFÖY BİRİNCİ SERBEST FON", "TERA PORTFÖY PARA PİYASASI (TL) FONU"]),
     ("2026-09-09 18:00:07", ["TERA PORTFÖY BİRİNCİ SERBEST FON"]),
     ("2026-09-08 17:11:30", ["PUSULA PORTFÖY PARA PİYASASI (TL) FONU", "PUSULA PORTFÖY İKİNCİ PARA PİYASASI (TL) FONU"]),
     ("2026-09-02 17:51:35", ["HEDEF PORTFÖY PARA PİYASASI SERBEST FON"])]
found = {}
for ts, names in T:
    t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    base = find(t); hits = []
    for j in sorted(range(base - 150, base + 250), key=lambda j: abs(j - base)):
        dt, txt = page(j)
        if dt and abs((dt - t).total_seconds()) <= 900 and "Dağılım" in txt:
            got = [n for n in names if n in txt]
            if got:
                hits.append(j); names = [n for n in names if n not in got]
                d = O / f"{j}"; d.mkdir(exist_ok=True); (d / "page.html").write_text(txt)
                for fid in sorted(set(re.findall(r"(4028328[0-9a-f]{25})", txt))):
                    rr = fetch(f"https://www.kap.org.tr/tr/api/file/download/{fid}")
                    if rr and rr.ok and len(rr.content) > 1000 and (b"%PDF" in rr.content[:200] or rr.content[:2] in (b"PK", b"\xd0\xcf", b"\xac\xed")):
                        (d / f"file_{fid}").write_bytes(rr.content)
        if not names: break
    found[ts] = {"hits": hits, "missing": names}
    print(ts, found[ts])
    (O / "found.json").write_text(json.dumps(found, indent=1, ensure_ascii=False))
    commit(f"job7 {ts}")
print(found)
