"""Job 5 (= job 4 made resumable, with incremental commits) (all parts save untouched responses + sha256 manifest under job_out/):
 A) KAP 2026 disclosure bundles for all 129 liquidated funds (+ TMV, FSU, TGI)
 B) headless browser: capture the JSON behind KAP fund-disclosure list pages (DFI, ABG, THF, DOH)
 C) daily prices (Yahoo Finance chart API) for IEYHO and stocks named in fund stake notices
 D) SPK bulletin index pages"""
import hashlib, json, re, time, unicodedata, subprocess, sys
from pathlib import Path
import requests, pandas as pd

CODES = "BHN BYZ CBD CAH CHY AJ1 PAB P1A SEH LGO BSH AP5 BAC AP4 ABG LAI KHD BTJ KLH PPT PSE SNY DFI GCD UHS BLA BOS BBO BP5 BOH BI5 BBN BDO IHY BIK BMU BPZ BSN BUC YLZ HLR HEH HAT HKM HIM HPL HDH HBV HDA HVA HMK HGH HGJ HPI HFI HKP KSA HPF HMV FNT NFK HYV HPH HKJ HVB HVC DUH HDK HPZ AP6 PAO BST PHY BRT BHH PBY BSE BDI AC7 PCH PDH DHI DRH PGE KHA AC8 IAU AC5 KRH PKU PMH PMP MGE POF POS POB PO9 PPO POI PO8 OHI POU PO7 AC4 PST PSR SHI CSH PYD PYI PYR PHB PBH PDG PDC PGH PHN PKD PNU PKZ PRY PKM PCS TLY DOH THF TP2 TLV T3B".split() + ["TMV", "FSU", "TGI", "TMM", "PBR", "PHE", "PUK", "PDE", "NNF", "HGV", "HJB", "HGM", "HNC", "HIF"]
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
     "Accept-Language": "tr-TR,tr;q=0.9"}
O = Path("job_out"); man = []
S = requests.Session(); S.headers.update(H)

def get(url, dest=None, tries=4):
    for k in range(tries):
        time.sleep(1.2 + 4 * k)
        try:
            r = S.get(url, timeout=90)
        except requests.RequestException as e:
            err = str(e); continue
        if r.status_code == 429:
            time.sleep(30); continue
        rec = {"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest(), "file": str(dest) if dest else None}
        man.append(rec)
        if dest and r.ok:
            dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(r.content)
        return r
    man.append({"url": url, "status": "failed"}); return None

def slug(code, name):
    s = name.replace("İ", "i").replace("I", "ı").lower().translate(str.maketrans("çğıöşü", "cgiosu"))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return f"{code.lower()}-" + re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def commit(msg):
    (O / "manifest_job5.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)

names = pd.read_csv("tefas_out/tefas_daily.csv.gz", usecols=["code", "name"]).groupby("code").name.last().to_dict()

# ---- B) headless browser first
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(locale="tr-TR")
        for code in ["DFI", "ABG", "THF", "DOH"]:
            caps = []
            def on_resp(resp):
                if "/api/" in resp.url and "json" in (resp.headers.get("content-type") or ""):
                    try: caps.append({"url": resp.url, "method": resp.request.method, "post": resp.request.post_data, "body": resp.json()})
                    except Exception as e: caps.append({"url": resp.url, "err": str(e)})
            pg.on("response", on_resp)
            try:
                pg.goto(f"https://www.kap.org.tr/tr/fon-bildirimleri/{slug(code, names[code])}", wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print("B goto", code, e)
            pg.wait_for_timeout(15000)
            pg.remove_listener("response", on_resp)
            (O / "browser").mkdir(parents=True, exist_ok=True)
            (O / "browser" / f"{code}_api.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1))
            print("B", code, len(caps), [c["url"] for c in caps][:8])
        b.close()
    commit("job5 browser")
except Exception as e:
    print("B failed:", e)

# ---- C) prices
TICK = ["IEYHO", "ISKPL", "GUNDG", "KTLEV", "PASEU", "SKYLP", "TMPOL", "ODINE", "ANELE", "BALSU", "TATEN", "DAPGM", "HEDEF", "BORLS",
        "INFO", "TEHOL", "TRHOL", "TERA", "PEKGY", "DSTKF", "OZATD", "MANAS", "ALKLC", "SVGYO", "KARCL", "SELEC", "BIGEN", "CVKMD", "XU100"]
for t in TICK:
    sym = t + ".IS"
    get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1735689600&period2=1791590400&interval=1d&events=div,split",
        O / "prices" / f"{t}.json")

commit("job5 prices")
# ---- D) SPK bulletin index
for u in ["https://spk.gov.tr/bultenler", "https://spk.gov.tr/spk-bultenleri", "https://spk.gov.tr/spk-bultenleri/2026", "https://www.spk.gov.tr/Bulten/Goster"]:
    get(u, O / "spk" / (re.sub(r"[^a-z0-9]+", "_", u.split("//")[1]) + ".html"))

# ---- A) bundles
PRI = sorted(CODES, key=lambda c: 0 if names.get(c, "").startswith(("PUSULA", "TERA", "ATLAS", "HEDEF")) else 1)
for n_, code in enumerate(PRI):
    if n_ % 10 == 9: commit(f"job5 bundles {n_}")
    if (O / "bundles" / f"{code}_2026.zip").exists() or (Path("job_out/kap") / code / "bundle_2026").exists(): continue
    nm = names.get(code)
    if not nm: print("A no name", code); continue
    r = get(f"https://www.kap.org.tr/tr/fon-bilgileri/ozet/{slug(code, nm)}")
    if not r or not r.ok: print("A ozet fail", code); continue
    for oid, yr in sorted(set(re.findall(r"api/batch-news/file-by-year/([0-9a-f]{32})/(\d{4})", r.text))):
        if yr == "2026":
            get(f"https://www.kap.org.tr/tr/api/batch-news/file-by-year/{oid}/{yr}", O / "bundles" / f"{code}_2026.zip")
    print("A", code, "ok")

print("done", len(man))
commit("job5 done")
