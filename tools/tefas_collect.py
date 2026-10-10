"""Collect daily TEFAS fund data (price, units, investors, AUM) for the
turkey-fund-crisis-2026 case file.

Based on the request format of tefas_fon_verisi.py (TEFAS website JSON API,
undocumented; may change without notice).

Run on your own computer (needs: python -m pip install requests pandas):

    python tefas_collect.py                       # 2025-01-01 .. 2026-09-30, all YAT funds
    python tefas_collect.py --start 2026-01-01    # shorter range
    python tefas_collect.py --codes TLY TP2 PRY   # only these codes (fallback mode)

Output (folder ./tefas_out):
    raw/<type>_<start>_<end>.json   untouched API responses (provenance)
    tefas_daily.csv.gz              all rows, one per fund per day
    manifest.csv                    request log: range, rows, sha256 of each raw file

Mode 1 (default) asks for ALL funds per 30-day window (fonKod = null). This gives
both the 131 liquidated funds and the rest of the market as a control group.
Re-running resumes: windows already saved in raw/ are skipped; empty windows
are split into 10-, 5- and 1-day requests. The table is rebuilt from all raw files.
"""
from __future__ import annotations

import argparse, gzip, hashlib, json, sys, time
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://www.tefas.gov.tr/api/funds/fonGnlBlgSiraliGetirDosya"
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.tefas.gov.tr/",
}
COLS = {"tarih": "date", "fonKodu": "code", "fonUnvan": "name", "fiyat": "price",
        "tedPaySayisi": "units", "kisiSayisi": "investors",
        "portfoyBuyukluk": "aum_tl", "borsaBultenFiyat": "exchange_price"}


def chunks(a: date, b: date, days: int = 30):
    while a <= b:
        e = min(a + timedelta(days=days - 1), b)
        yield a, e
        a = e + timedelta(days=1)


def query(s, fund_type, code, a, b, retries=3, pause=2.0):
    body = {"dil": "TR", "fonTipi": fund_type, "sfonTurKod": None, "fonKod": code,
            "fonGrup": None, "basTarih": a.strftime("%Y%m%d"), "bitTarih": b.strftime("%Y%m%d"),
            "fonTurKod": None, "fonUnvanTip": None, "kurucuKod": None, "fonTurAciklama": None}
    problem = ""
    for i in range(retries + 1):
        time.sleep(pause)
        try:
            r = s.post(API_URL, json=body, timeout=120)
            r.raise_for_status()
            payload = r.json()
        except (requests.RequestException, ValueError) as exc:
            problem = f"request/JSON error: {exc}"
        else:
            if payload.get("errorCode"):
                problem = f"API error {payload.get('errorCode')}: {payload.get('errorMessage')}"
            elif isinstance(payload.get("resultList"), list) and payload["resultList"]:
                return r.content, payload["resultList"], ""
            else:
                problem = "HTTP 200 but empty resultList"
        if i < retries:
            time.sleep(min(10 * 2 ** i, 60))
    return None, [], problem


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2025-01-01")
    p.add_argument("--end", default="2026-09-30")
    p.add_argument("--type", default="YAT", choices=["YAT", "EMK", "BYF"])
    p.add_argument("--codes", nargs="*", default=None)
    p.add_argument("--out", default="tefas_out")
    p.add_argument("--pause", type=float, default=2.0)
    a = p.parse_args()

    start = datetime.strptime(a.start, "%Y-%m-%d").date()
    end = datetime.strptime(a.end, "%Y-%m-%d").date()
    out = Path(a.out); (out / "raw").mkdir(parents=True, exist_ok=True)
    targets = [c.upper() for c in a.codes] if a.codes else [None]

    log = []
    man = out / "manifest.csv"
    if man.exists():
        log = pd.read_csv(man).fillna("").to_dict("records")

    def have(tag):
        return (out / "raw" / f"{tag}.json").exists() or (out / "raw" / f"{tag}.json.gz").exists()

    def fetch(s, code, c0, c1, depth=0):
        tag = f"{a.type}_{code or 'ALL'}_{c0:%Y%m%d}_{c1:%Y%m%d}"
        if have(tag):
            return True
        print(f"{'  ' * depth}{tag} ...", end=" ", flush=True)
        raw, res, problem = query(s, a.type, code, c0, c1, pause=a.pause)
        sha = ""
        if raw:
            (out / "raw" / f"{tag}.json").write_bytes(raw)
            sha = hashlib.sha256(raw).hexdigest()
        print(f"{len(res)} rows" if res else f"EMPTY ({problem})")
        log.append({"request": tag, "rows": len(res), "sha256": sha, "problem": problem,
                    "retrieved_utc": datetime.utcnow().isoformat(timespec="seconds")})
        if res:
            return True
        # empty window: split into smaller windows (30 -> 10 -> 5 -> 1 day)
        span = (c1 - c0).days + 1
        if span > 1:
            size = 10 if span > 10 else (5 if span > 5 else 1)
            for d0, d1 in chunks(c0, c1, size):
                fetch(s, code, d0, d1, depth + 1)
        return False

    with requests.Session() as s:
        s.headers.update(HEADERS)
        for code in targets:
            for c0, c1 in chunks(start, end):
                fetch(s, code, c0, c1)

    # rebuild the table from every raw response on disk (old + new)
    rows = []
    for f in sorted((out / "raw").glob("*.json*")):
        b = gzip.decompress(f.read_bytes()) if f.suffix == ".gz" else f.read_bytes()
        rows.extend(json.loads(b).get("resultList") or [])
    pd.DataFrame(log).to_csv(man, index=False)
    if not rows:
        print("No data."); return
    df = pd.json_normalize(rows)
    missing = [k for k in COLS if k not in df.columns]
    if missing:
        print("Warning: fields missing in response:", missing)
        print("Fields present:", list(df.columns))
    df = df.rename(columns=COLS)
    d = df["date"].astype(str)
    df["date"] = (pd.to_datetime(pd.to_numeric(d, errors="coerce"), unit="ms") if d.str.fullmatch(r"\d{12,}").all()
                  else pd.to_datetime(d, errors="coerce", format="mixed", dayfirst=d.str.contains(r"\.").any()))
    for c in ["price", "units", "investors", "aum_tl", "exchange_price"]:
        if c in df: df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.sort_values(["code", "date"]).drop_duplicates(["code", "date"], keep="last")
    df.to_csv(out / "tefas_daily.csv.gz", index=False, compression="gzip")
    print(f"\nSaved {len(df):,} rows, {df['code'].nunique()} funds -> {out/'tefas_daily.csv.gz'}")
    print("Please upload tefas_daily.csv.gz and manifest.csv to the chat.")


if __name__ == "__main__":
    main()
