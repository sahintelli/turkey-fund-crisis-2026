"""Step 1: combine monthly TEFAS exports and price exports into tidy CSV files in data/interim/."""
from common import *

for fund_dir in sorted((RAW / "tefas").iterdir()):
    code = fund_dir.name
    for tab in ("general", "allocation"):
        files = sorted((fund_dir / tab).glob("*.xlsx"))
        if not files:
            continue
        df = pd.concat([read_tefas_export(f) for f in files]).sort_values("Tarih").drop_duplicates("Tarih")
        if tab == "general":
            for c in ["Fiyat", "Tedavüldeki Pay Sayısı", "Kişi Sayısı", "Fon Toplam Değer"]:
                df[c] = pd.to_numeric(df[c])
        else:  # portfolio shares arrive as fractions; store as % of portfolio
            df = (df.drop(columns=["Fon Kodu", "Fon Adı"]).set_index("Tarih").apply(pd.to_numeric, errors="coerce") * 100).reset_index()
        out = INTERIM / f"{code.lower()}_{tab}.csv"
        df.to_csv(out, index=False)
        print(f"{code} {tab}: {len(files)} files, {df['Tarih'].min().date()} → {df['Tarih'].max().date()}, {len(df)} days -> {out.name}")

P, V = {}, {}
for f in sorted((RAW / "prices").glob("*.xlsx")):
    d = read_price_export(f)
    P[f.stem], V[f.stem] = d["Price"], d["Volume"]
if P:
    pd.DataFrame(P).to_csv(INTERIM / "prices.csv")
    pd.DataFrame(V).to_csv(INTERIM / "volumes.csv")
    print(f"prices: {sorted(P)}")
