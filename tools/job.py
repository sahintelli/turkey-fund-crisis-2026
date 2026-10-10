"""Job 2: discover the KAP API used by the fund-disclosure list page (client-side), so that
monthly portfolio-report attachments can be located. Saves JS-derived endpoint strings."""
import re, json, time, hashlib
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
     "Accept-Language": "tr-TR,tr;q=0.9"}
OUT = Path("job_out/kap_api"); OUT.mkdir(parents=True, exist_ok=True)
page = "https://www.kap.org.tr/tr/fon-bildirimleri/thf-tera-portfoy-hisse-senedi-tl-fonu-hisse-senedi-yogun-fon"
html = requests.get(page, headers=H, timeout=60).text
srcs = sorted(set(re.findall(r'src="(/_next/static/chunks/[^"]+\.js)"', html)))
found = {}
for s in srcs:
    time.sleep(0.5)
    js = requests.get("https://www.kap.org.tr" + s, headers=H, timeout=60).text
    for m in re.finditer(r'["\'`]([^"\'`]{0,80}api/[^"\'`]{2,120})["\'`]', js):
        found.setdefault(m.group(1), set()).add(s)
    for kw in ("disclosure", "Disclosure", "bildirim"):
        for m in re.finditer(kw, js):
            ctx = js[max(0, m.start() - 150): m.end() + 150]
            if "api" in ctx or "fetch" in ctx or "post" in ctx.lower():
                found.setdefault("CTX:" + ctx.replace("\n", " "), set()).add(s)
(OUT / "endpoints.json").write_text(json.dumps({k: sorted(v) for k, v in found.items()}, indent=1, ensure_ascii=False))
print(len(srcs), "chunks;", len(found), "strings")
for k in sorted(found):
    if not k.startswith("CTX:"):
        print(k)
