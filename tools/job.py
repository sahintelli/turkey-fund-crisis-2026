"""Job 12b: KAP company general-information pages (shareholders >=5%, subsidiaries, board) for Tera/Pusula group
companies, companies whose IPO Tera/ALB led, and main stocks held by the liquidated funds. Page paths taken from
KAP's own company list (job_out/kap_company/bist_sirketler.html, job 12). Saves untouched HTML, the rendered page
text and any JSON the page loads, with a sha256 manifest, under job_out/kap_company2/."""
import json, time, hashlib, subprocess, sys
from pathlib import Path
import requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}
S = requests.Session(); S.headers.update(H)
O = Path("job_out/kap_company2"); O.mkdir(parents=True, exist_ok=True); man = []
IDX = {'TERA': '2464-tera-yatirim-menkul-degerler-a-s', 'TRHOL': '1089-tera-finansal-yatirimlar-holding-a-s', 'TEHOL': '968-tera-yatirim-teknoloji-holding-a-s',
 'PEKGY': '4584-peker-gayrimenkul-yatirim-ortakligi-a-s', 'MANAS': '5357-manas-enerji-yonetimi-sanayi-ve-ticaret-a-s', 'KTLEV': '5763-katilimevim-tasarruf-finansman-a-s',
 'GUNDG': '6011-gundogdu-gida-sut-urunleri-sanayi-ve-dis-ticaret-a-s', 'ANELE': '1475-anel-elektrik-proje-taahhut-ve-ticaret-a-s', 'DSTKF': '2191-destek-finans-faktoring-a-s',
 'PSGYO': '5371-pasifik-gayrimenkul-yatirim-ortakligi-a-s', 'VSNMD': '6060-visne-madencilik-uretim-sanayi-ve-ticaret-a-s', 'AKFIS': '6036-akfen-insaat-turizm-ve-ticaret-a-s',
 'BAHKM': '6005-bahadir-kimya-sanayi-ve-ticaret-a-s', 'KZGYO': '5857-kuzugrup-gayrimenkul-yatirim-ortakligi-a-s', 'CVKMD': '5807-cvk-maden-isletmeleri-sanayi-ve-ticaret-a-s',
 'BVSAN': '5769-bulbuloglu-vinc-sanayi-ve-ticaret-a-s', 'ORCAY': '5407-orcay-ortakoy-cay-sanayi-ve-ticaret-a-s', 'IHAAS': '5420-ihlas-haber-ajansi-a-s', 'LIDER': '4310-ldr-turizm-a-s',
 'LIDFA': '1509-lider-faktoring-a-s', 'OZATD': '6018-ozata-denizcilik-sanayi-ve-ticaret-a-s', 'PASEU': '5826-pasifik-eurasia-lojistik-dis-ticaret-a-s',
 'SKYLP': '1602-skyalp-finansal-teknolojiler-ve-danismanlik-a-s', 'ODINE': '5941-odine-solutions-teknoloji-ticaret-ve-sanayi-a-s', 'TMPOL': '2075-temapol-polimer-plastik-ve-insaat-sanayi-ticaret-a-s',
 'IZFAS': '2273-izmir-firca-sanayi-ve-ticaret-a-s', 'ALKLC': '5966-altinkilic-gida-ve-sut-sanayi-ticaret-a-s', 'ISVEA': '6235-isvea-seramik-ve-banyo-urunleri-sanayi-a-s',
 'SVGYO': '6198-savur-gayrimenkul-yatirim-ortakligi-a-s', 'BIGEN': '6059-birlesim-grup-enerji-yatirimlari-a-s', 'KARCL': '3200-kardemir-celik-sanayi-a-s',
 'SELEC': '1420-selcuk-ecza-deposu-ticaret-ve-sanayi-a-s', 'IEYHO': '1031-isiklar-enerji-ve-yapi-holding-a-s', 'ISKPL': '5254-isik-plastik-sanayi-ve-dis-ticaret-pazarlama-a-s',
 'INFO': '1559-info-yatirim-menkul-degerler-a-s', 'HEDEF': '5387-hedef-holding-a-s', 'BALSU': '5614-balsu-gida-sanayi-ve-ticaret-a-s', 'TATEN': '5850-tatlipinar-enerji-uretim-a-s',
 'BALAT': '1627-balatacilar-balatacilik-sanayi-ve-ticaret-a-s'}
def commit(msg):
    (O / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m '%s [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q" % msg, shell=True)
def get(url, dest):
    for k in range(4):
        time.sleep(1.0 + 3 * k)
        try: r = S.get(url, timeout=90)
        except requests.RequestException as e: print("err", url, e); continue
        man.append({"url": url, "status": r.status_code, "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest(), "file": str(dest)})
        if r.ok: dest.write_bytes(r.content)
        return r
for tk, path in IDX.items():
    get(f"https://www.kap.org.tr/tr/sirket-bilgileri/genel/{path}", O / f"{tk}_genel.html")
commit("job12b html")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(locale="tr-TR")
        for n, (tk, path) in enumerate(IDX.items()):
            caps = []
            def on(resp):
                ct = resp.headers.get("content-type") or ""
                if "json" in ct or "/api/" in resp.url:
                    try: caps.append({"url": resp.url, "status": resp.status, "body": resp.text()[:400000]})
                    except Exception as e: caps.append({"url": resp.url, "err": str(e)})
            pg.on("response", on)
            try: pg.goto(f"https://www.kap.org.tr/tr/sirket-bilgileri/genel/{path}", wait_until="networkidle", timeout=90000)
            except Exception as e: print("goto", tk, e)
            pg.wait_for_timeout(3000)
            try:
                txt = pg.inner_text("body")
                (O / f"{tk}_genel_rendered.txt").write_text(txt)
                man.append({"url": f"rendered:{tk}", "bytes": len(txt), "sha256": hashlib.sha256(txt.encode()).hexdigest()})
            except Exception as e: print("text", tk, e)
            pg.remove_listener("response", on)
            (O / f"{tk}_api.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1))
            print("B", tk, len(caps))
            if n % 10 == 9: commit(f"job12b rendered {n}")
        b.close()
except Exception as e:
    print("browser failed", e)
commit("job12b done")
print("done", len(man))
