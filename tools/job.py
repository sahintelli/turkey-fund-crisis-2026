"""Job 8: discover TEFAS website API endpoints (for asset-allocation data), save JS-derived strings."""
import re, json, time, subprocess
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
S = requests.Session(); S.headers.update(H)
O = Path("job_out/tefas_api"); O.mkdir(parents=True, exist_ok=True)
def commit(msg):
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
found, pages = {}, ["https://www.tefas.gov.tr/", "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=TLY", "https://www.tefas.gov.tr/TarihselVeriler.aspx",
                    "https://www.tefas.gov.tr/fon-detay/TLY", "https://www.tefas.gov.tr/tarihsel-veriler"]
srcs = set()
for p in pages:
    try:
        r = S.get(p, timeout=60); print(p, r.status_code, len(r.text))
        (O / (re.sub(r"[^a-z0-9]+", "_", p.split("//")[1])[:60] + ".html")).write_text(r.text)
        srcs |= set(re.findall(r'src="([^"]+\.js[^"]*)"', r.text))
        for m in re.finditer(r'["\'`]([^"\'`]{0,60}api/[^"\'`]{2,120})["\'`]', r.text): found.setdefault(m.group(1), []).append(p)
    except Exception as e:
        print(p, e)
for s in sorted(srcs):
    u = s if s.startswith("http") else "https://www.tefas.gov.tr" + (s if s.startswith("/") else "/" + s)
    try:
        js = S.get(u, timeout=60).text
    except Exception: continue
    for m in re.finditer(r'["\'`]([^"\'`]{0,60}api/[^"\'`]{2,120})["\'`]', js): found.setdefault(m.group(1), []).append(u)
    for kw in ("Dagilim", "dagilim", "Dağılım", "varlik", "Varlik"):
        for m in re.finditer(kw, js):
            c = js[max(0, m.start() - 160): m.end() + 160]
            if "api" in c or "fetch" in c or "post" in c.lower(): found.setdefault("CTX:" + c, []).append(u)
(O / "endpoints.json").write_text(json.dumps(found, indent=1, ensure_ascii=False))
for k in sorted(found):
    if not k.startswith("CTX"): print(k)
commit("job8 tefas api")
