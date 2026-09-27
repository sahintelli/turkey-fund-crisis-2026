"""Shared paths, loaders and documented constants."""
from pathlib import Path
import pandas as pd, numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW, INTERIM, RESULTS, FIG = ROOT / "data/raw", ROOT / "data/interim", ROOT / "results", ROOT / "figures"
for p in (INTERIM, RESULTS, FIG):
    p.mkdir(parents=True, exist_ok=True)


def read_tefas_export(path):
    """Read a TEFAS 'Tarihsel Veriler' Excel export (either tab). The header row is the 5th row.
    Depending on the export, dates arrive as dd.mm.yyyy strings, Excel serials or datetimes."""
    df = pd.read_excel(path, header=None, skiprows=4)
    df.columns = df.iloc[0]
    df = df.iloc[1:].copy()
    t = df["Tarih"]
    first = t.iloc[0]
    if isinstance(first, (int, float)) or (isinstance(first, str) and first.replace(".", "").isdigit() and first.count(".") <= 1):
        df["Tarih"] = pd.to_datetime(t.astype(float), unit="D", origin="1899-12-30")
    else:
        df["Tarih"] = pd.to_datetime(t, dayfirst=True)
    return df


def read_price_export(path):
    """Read an investing.com 'Historical Data' Excel export: Date, Price, Open, High, Low, Vol., Change %."""
    d = pd.read_excel(path)
    d["Date"] = pd.to_datetime(d["Date"], format="%b %d, %Y")

    def vol(v):
        v = str(v).strip()
        if v in ("nan", "-", ""):
            return np.nan
        m = {"K": 1e3, "M": 1e6, "B": 1e9}
        return float(v[:-1]) * m[v[-1]] if v[-1] in m else float(v)

    d["Volume"] = d["Vol."].map(vol)
    return d.sort_values("Date").set_index("Date")


def load_general(code):
    return pd.read_csv(INTERIM / f"{code.lower()}_general.csv", parse_dates=["Tarih"]).sort_values("Tarih").reset_index(drop=True)


def load_allocation(code):
    return pd.read_csv(INTERIM / f"{code.lower()}_allocation.csv", parse_dates=["Tarih"], index_col="Tarih")


# Monthly portfolio weights (% of portfolio) of TLY's six largest equity holdings.
# Source: Fonoloji monthly holdings pages (aggregator of TEFAS and KAP/Takasbank data),
# https://fonoloji.com/fon/TLY/dagilim . Weights for month m are the end-of-previous-month
# weights and are applied to every day of month m (an approximation; see docs/method.md).
WEIGHTS = {
    "2026-07": dict(DSTKF=22.8, OZATD=14.3, TEHOL=7.1, TRHOL=5.6, PEKGY=7.7, ANELE=2.0),   # end-June
    "2026-08": dict(DSTKF=12.0, OZATD=34.3, TEHOL=9.2, TRHOL=4.0, PEKGY=8.8, ANELE=2.2),   # end-July
    "2026-09": dict(DSTKF=21.1, OZATD=19.4, TEHOL=10.6, TRHOL=6.7, PEKGY=8.9, ANELE=3.0),  # end-August
}


def write(name, text):
    (RESULTS / name).write_text(text + "\n", encoding="utf-8")
    print(text)
