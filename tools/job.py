"""Job 9: real browser on TEFAS (site uses a JS bot challenge) - capture every API call (URL, POST body,
JSON response) made by the fund-detail and historical-data pages, to identify the asset-allocation endpoint."""
import json, subprocess, sys
from pathlib import Path
O = Path("job_out/tefas_browser"); O.mkdir(parents=True, exist_ok=True)
def commit(msg):
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
from playwright.sync_api import sync_playwright
caps = []
def on_resp(resp):
    ct = resp.headers.get("content-type") or ""
    if "json" in ct or "/api/" in resp.url:
        rec = {"url": resp.url, "method": resp.request.method, "post": resp.request.post_data, "status": resp.status}
        try: rec["body"] = resp.json()
        except Exception: rec["text"] = (resp.text() or "")[:3000] if "json" in ct else None
        caps.append(rec)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(locale="tr-TR", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    pg = ctx.new_page(); pg.on("response", on_resp)
    for url in ["https://www.tefas.gov.tr/", "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=TLY", "https://www.tefas.gov.tr/TarihselVeriler.aspx"]:
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=90000); pg.wait_for_timeout(12000)
            (O / (url.split("/")[-1].replace("?", "_").replace("=", "_") or "home")).with_suffix(".html").write_text(pg.content())
            print("page", url, pg.url, len(pg.content()))
        except Exception as e: print("goto", url, e)
    # try clicking anything that mentions allocation on the historical page
    for label in ["Portföy Dağılımı", "Varlık Dağılımı", "Fon Dağılımı", "Dağılım"]:
        try:
            pg.get_by_text(label, exact=False).first.click(timeout=5000); pg.wait_for_timeout(8000); print("clicked", label)
        except Exception as e: print("noclick", label)
    b.close()
(O / "captures.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1)[:20_000_000])
for c in caps: print(c["method"], c["status"], c["url"][:160], (c["post"] or "")[:200])
commit("job9 tefas browser")
