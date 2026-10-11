"""Job 10: probe candidate TEFAS JSON endpoint names for daily asset-allocation data (the site states
'Varlık dağılımı Takasbank'a en son bildirilen verileri içermektedir'). Records status/first bytes only."""
import json, time, subprocess
from pathlib import Path
import requests
H = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Referer": "https://www.tefas.gov.tr/",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
O = Path("job_out/tefas_probe2"); O.mkdir(parents=True, exist_ok=True)
names = ["fonGnlBlgSiraliGetirDosya", "fonPrtfDglmSiraliGetirDosya", "fonPortfoyDagilimSiraliGetirDosya", "fonVarlikDagilimSiraliGetirDosya",
         "fonDagilimSiraliGetirDosya", "fonPrtDglSiraliGetirDosya", "fonPrtfDglSiraliGetirDosya", "fonVrlkDglmSiraliGetirDosya",
         "fonPortfoyDglmSiraliGetirDosya", "fonDglmSiraliGetirDosya", "fonPrtDglmSiraliGetirDosya", "fonVarlikDagilimGetir",
         "fonPortfoyDagilimGetir", "fonVrlkDglmGetir", "fonPrtfDglmGetir", "fonFiyatBilgiGetir", "fonGetiriBazliBilgiGetir",
         "fonDetayGetir", "fonBilgiGetir", "fonVarlikDagilimi", "fonPortfoyDagilimi", "fonPrtfDglmBlgSiraliGetirDosya"]
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
(O / "probe.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
subprocess.run("git config user.name 'github-actions[bot]' && git config user.email '41898282+github-actions[bot]@users.noreply.github.com' && git add job_out && (git commit -q -m 'job10 [skip ci]' || true) && (git pull -q --rebase -X theirs || true) && git push -q", shell=True)
