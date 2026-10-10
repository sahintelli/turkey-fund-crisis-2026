"""Job 3: save KAP front-end JS chunks (to read the request format of the fund-disclosure
list API) and try a few candidate requests. Untouched responses saved under job_out/kap_api2/."""
import re, json, time
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
     "Accept-Language": "tr-TR,tr;q=0.9", "Accept": "application/json, text/plain, */*"}
OUT = Path("job_out/kap_api2"); (OUT / "js").mkdir(parents=True, exist_ok=True)
s = requests.Session(); s.headers.update(H)
page = "https://www.kap.org.tr/tr/fon-bildirimleri/thf-tera-portfoy-hisse-senedi-tl-fonu-hisse-senedi-yogun-fon"
html = s.get(page, timeout=60).text
for src in sorted(set(re.findall(r'src="(/_next/static/chunks/[^"]+\.js)"', html))):
    js = s.get("https://www.kap.org.tr" + src, timeout=60).text
    if any(k in js for k in ("byCriteria", "list/main", "fundOid", "FROM_ROUTE_API", "attachment")):
        (OUT / "js" / src.split("/")[-1]).write_text(js)
# also chunks referenced inside chunks (lazy loaded)
more = set()
for f in (OUT / "js").glob("*.js"):
    more |= set(re.findall(r'(static/chunks/[A-Za-z0-9_\-]+\.js)', f.read_text()))
for m in sorted(more):
    js = s.get("https://www.kap.org.tr/_next/" + m, timeout=60).text
    if any(k in js for k in ("byCriteria", "fundOid", "disclosureClass", "attachment")):
        (OUT / "js" / m.split("/")[-1]).write_text(js)
oid = "4028328c950ba8c70195140f682921da"   # THF member oid (from batch-news link)
cands = [
  ("POST", "api/disclosure/funds/byCriteria", {"fromDate": "2026-08-25", "toDate": "2026-09-15", "fundOidList": [oid]}),
  ("POST", "api/disclosure/funds/byCriteria", {"fromDate": "25.08.2026", "toDate": "15.09.2026", "fundOidList": [oid]}),
  ("POST", "api/disclosure/funds/byCriteria", {"fromDate": "2026-08-25", "toDate": "2026-09-15", "mkkMemberOidList": [oid]}),
  ("GET", f"api/disclosure/funds/byCriteria?fundOid={oid}", None),
  ("POST", "api/disclosure/list/main", {"fromDate": "2026-08-25", "toDate": "2026-09-15", "fundOidList": [oid]}),
]
log = []
for i, (m, path, body) in enumerate(cands):
    time.sleep(1)
    url = "https://www.kap.org.tr/tr/" + path
    r = s.post(url, json=body, timeout=60) if m == "POST" else s.get(url, timeout=60)
    (OUT / f"cand{i}.txt").write_text(r.text[:200000])
    log.append({"i": i, "method": m, "url": url, "body": body, "status": r.status_code, "len": len(r.text), "head": r.text[:300]})
    print(i, r.status_code, len(r.text), r.text[:200].replace("\n", " "))
(OUT / "log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False))
print("js saved:", [p.name for p in (OUT / "js").glob("*.js")])
