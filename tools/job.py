"""Job 10b: probe candidate TEFAS JSON endpoint names for daily asset-allocation data (the site states
'Varlık dağılımı Takasbank'a en son bildirilen verileri içermektedir'). Records status/first bytes only."""
import json, time, subprocess
from pathlib import Path
import requests
H = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Referer": "https://www.tefas.gov.tr/",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
O = Path("job_out/tefas_probe3"); O.mkdir(parents=True, exist_ok=True)
names = ["fonVarlikSiraliGetirDosya", "fonDglSiraliGetirDosya", "fonPrtfSiraliGetirDosya", "fonPortfoySiraliGetirDosya", "fonVrlkSiraliGetirDosya",
         "fonVarlikDglmSiraliGetirDosya", "fonPortfoyDagilimBilgiGetir", "fonVarlikDagilimBilgiGetir", "fonDagilimBilgiGetir", "fonVrlkDglmBlgGetir",
         "fonPrtfDglmBlgGetir", "fonPrtfBlgSiraliGetirDosya", "fonPrtBlgSiraliGetirDosya", "fonVrlkBlgSiraliGetirDosya", "fonDglBlgSiraliGetirDosya",
         "fonDglmBlgSiraliGetirDosya", "fonVrlkDglmBlgSiraliGetirDosya", "fonPrtfDglBlgSiraliGetirDosya", "fonVarlikBilgiGetir", "fonPortfoyBilgiGetir",
         "fonDagilimGetir", "fonPrtfDglGetir", "fonVrlkDglGetir", "fonVarlikDagilimListesiGetir", "fonPortfoyGetir", "fonVarlikGetir"]
body = {"dil": "TR", "fonTipi": "YAT", "sfonTurKod": None, "fonKod": "TLY", "fonKodu": "TLY", "fonGrup": None, "basTarih": "20260801",
        "bitTarih": "20260830", "fonTurKod": None, "fonUnvanTip": None, "kurucuKod": None, "fonTurAciklama": None, "periyod": 3}
res = []
for n in names:
    time.sleep(1.5)
    try:
        r = requests.post("https://www.tefas.gov.tr/api/funds/" + n, json=body, headers=H, timeout=60)
        res.append({"name": n, "status": r.status_code, "len": len(r.content), "head": r.text[:600]})
        if r.ok and len(r.content) > 200: (O / f"{n}.json").write_bytes(r.content)
    except Exception as e:
        res.append({"name": n, "error": str(e)})
    print(res[-1].get("status"), res[-1].get("len"), n, (res[-1].get("head") or "")[:160].replace("\n", " "))
for bd in [{"fonKodu": "TLY", "dil": "TR"}, {"fonKodu": "TLY", "dil": "TR", "periyod": 1}, {"fonKod": "TLY", "dil": "TR", "tarih": "20260828"}]:
    for n in ["fonDetayGetir", "fonBilgiGetir"]:
        time.sleep(1.5)
        r = requests.post("https://www.tefas.gov.tr/api/funds/" + n, json=bd, headers=H, timeout=60)
        res.append({"name": n, "body": bd, "status": r.status_code, "len": len(r.content), "head": r.text[:3000]})
        print(r.status_code, len(r.content), n, bd, r.text[:300])
(O / "probe.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m 'job10b [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q", shell=True)
