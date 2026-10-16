"""Job 12: KAP company general-information pages (shareholders >=5%, subsidiaries, board) for Tera/Pusula group
companies, companies whose IPO Tera led, and the main stocks held by the liquidated funds. Saves untouched HTML +
sha256 manifest under job_out/kap_company/. Also records any JSON responses the page loads (headless browser)."""
import re, json, time, hashlib, subprocess, sys
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
S = requests.Session(); S.headers.update(H)
O = Path("job_out/kap_company"); O.mkdir(parents=True, exist_ok=True); man = []
TICK = ("TERA TRHOL TEHOL PEKGY MANAS KTLEV GUNDG ANELE DSTKF PSGYO VSNMD AKFIS BAHKM KZGYO CVKMD BLUCN ORCAY IHAAS LIDFA LIDER "
        "OZATD PASEU SKYLP ODINE TMPOL IZFAS ALKLC ISVEA SVGYO BIGEN KARCL SELEC IEYHO ISKPL INFO HEDEF BALSU TATEN").split()
def commit(msg):
    (O / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
def get(url, dest=None):
    for k in range(4):
        time.sleep(1.0 + 3 * k)
        try: r = S.get(url, timeout=90)
        except requests.RequestException as e: print("err", url, e); continue
        man.append({"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest(), "file": str(dest) if dest else None})
        if dest is not None and r.ok: dest.write_bytes(r.content)
        return r
    return None
# 1) company list -> id/slug per ticker
idx = {}
for u in ["https://www.kap.org.tr/tr/bist-sirketler", "https://www.kap.org.tr/tr/bist-sirketler/"]:
    r = get(u, O / "bist_sirketler.html")
    if r and r.ok:
        t = r.text
        for m in re.finditer(r'sirket-bilgileri/ozet/(\d+)-([a-z0-9\-]+)', t):
            seg = t[max(0, m.start() - 400): m.end() + 400]
            for tk in TICK:
                if re.search(r'(?<![A-Z0-9])' + tk + r'(?![A-Z0-9])', seg) and tk not in idx:
                    idx[tk] = f"{m.group(1)}-{m.group(2)}"
        print("links:", len(re.findall(r'sirket-bilgileri/ozet/', t)), "matched:", len(idx)); break
(O / "index.json").write_text(json.dumps(idx, indent=1))
print(idx)
# 2) raw pages
for tk, path in idx.items():
    for kind in ["genel", "ozet"]:
        get(f"https://www.kap.org.tr/tr/sirket-bilgileri/{kind}/{path}", O / f"{tk}_{kind}.html")
commit("job12 kap company html")
# 3) headless browser: capture JSON the genel page loads
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(locale="tr-TR")
        for tk, path in idx.items():
            caps = []
            def on(resp):
                ct = resp.headers.get("content-type") or ""
                if "json" in ct or "/api/" in resp.url:
                    try: caps.append({"url": resp.url, "status": resp.status, "body": resp.text()[:400000]})
                    except Exception as e: caps.append({"url": resp.url, "err": str(e)})
            pg.on("response", on)
            try: pg.goto(f"https://www.kap.org.tr/tr/sirket-bilgileri/genel/{path}", wait_until="networkidle", timeout=90000)
            except Exception as e: print("goto", tk, e)
            pg.wait_for_timeout(4000)
            try: (O / f"{tk}_genel_rendered.txt").write_text(pg.inner_text("body"))
            except Exception as e: print("text", tk, e)
            pg.remove_listener("response", on)
            (O / f"{tk}_api.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1))
            print("B", tk, len(caps))
        b.close()
except Exception as e:
    print("browser failed", e)
commit("job12 done")
print("done", len(man))
