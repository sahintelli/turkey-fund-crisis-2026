"""Fetch public KAP fund documents for the case file (run by .github/workflows/job.yml).
For each fund: KAP summary page -> current prospectus (izahname) + 2026 disclosure bundle.
Everything is saved untouched under job_out/kap/<CODE>/ with a sha256 manifest."""
import hashlib, json, re, time, unicodedata
from pathlib import Path
import requests

FUNDS = {
 "PCS": "PUSULA PORTFÖY ÜÇÜNCÜ HİSSE SENEDİ SERBEST FON (HİSSE SENEDİ YOĞUN FON)",
 "PKZ": None, "HDH": None, "PHB": None, "PGH": None, "PHN": "PUSULA PORTFÖY İKİNCİ HİSSE SENEDİ SERBEST FON (HİSSE SENEDİ YOĞUN FON)",
 "HMV": None, "T3B": None, "DFI": "ATLAS PORTFÖY SERBEST FON", "ABG": None,
 "THF": "TERA PORTFÖY HİSSE SENEDİ (TL) FONU (HİSSE SENEDİ YOĞUN FON)",
 "DOH": "TERA PORTFÖY DÖRDÜNCÜ HİSSE SENEDİ SERBEST (TL) FON (HİSSE SENEDİ YOĞUN FON)",
}
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
     "Accept-Language": "tr-TR,tr;q=0.9"}
OUT = Path("job_out/kap"); OUT.mkdir(parents=True, exist_ok=True)
manifest = []

def names_from_tefas():
    import pandas as pd
    f = Path("tefas_out/tefas_daily.csv.gz")
    if f.exists():
        d = pd.read_csv(f, usecols=["code", "name"])
        return d.groupby("code").name.last().to_dict()
    return {}

def slug(code, name):
    s = name.replace("İ", "i").replace("I", "ı").lower()
    s = s.translate(str.maketrans("çğıöşü", "cgiosu"))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"{code.lower()}-{s}"

def get(url, dest=None):
    time.sleep(1.5)
    try:
        r = requests.get(url, headers=H, timeout=90)
    except requests.RequestException as e:
        print("  FAIL", url, e); manifest.append({"url": url, "status": "error", "error": str(e)}); return None
    sha = hashlib.sha256(r.content).hexdigest()
    rec = {"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": sha,
           "content_type": r.headers.get("content-type"), "file": str(dest) if dest else None}
    manifest.append(rec); print(" ", r.status_code, len(r.content), url)
    if dest and r.ok:
        dest.write_bytes(r.content)
    return r

tefas = names_from_tefas()
for code, name in FUNDS.items():
    name = name or tefas.get(code)
    if not name:
        print("no name for", code); continue
    d = OUT / code; d.mkdir(exist_ok=True)
    s = slug(code, name)
    print(code, s)
    r = get(f"https://www.kap.org.tr/tr/fon-bilgileri/ozet/{s}", d / "ozet.html")
    if not r or not r.ok:
        continue
    html = r.text
    files = sorted(set(re.findall(r"api/file/download/([0-9a-f]{32})", html)))
    batches = sorted(set(re.findall(r"api/batch-news/file-by-year/([0-9a-f]{32})/(\d{4})", html)))
    (d / "links.json").write_text(json.dumps({"files": files, "batches": batches}, indent=1))
    for fid in files:
        get(f"https://www.kap.org.tr/tr/api/file/download/{fid}", d / f"file_{fid}")
    for oid, yr in batches:
        if yr in ("2026",):
            get(f"https://www.kap.org.tr/tr/api/batch-news/file-by-year/{oid}/{yr}", d / f"bundle_{yr}")
    get(f"https://www.kap.org.tr/tr/fon-bildirimleri/{s}", d / "bildirimler.html")

Path("job_out/manifest_kap.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
print("done", len(manifest), "requests")
