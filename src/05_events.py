"""Step 5: exchange activity around the TPKGY exit (27–28 Jul) and the OZATD transactions."""
from common import *

P = pd.read_csv(INTERIM / "prices.csv", index_col=0, parse_dates=True)
V = pd.read_csv(INTERIM / "volumes.csv", index_col=0, parse_dates=True)
NAV_TPKGY = 8122.13  # manager's NAV per unit, 30 Jun 2026 (Ekonomi Gazetesi, 27 Jul 2026)
tv = (P.TPKGY * V.TPKGY).loc["2026-07-27":"2026-07-28"]
u = V.TPKGY.loc["2026-07-27":"2026-07-28"].sum()
out = [f"TPKGY 27–28 Jul: {u:,.0f} units, traded value {tv.sum() / 1e9:.2f} bn TL; value at NAV {u * NAV_TPKGY / 1e9:.2f} bn TL;"
       f" normal volume (mean 1 Jun–24 Jul) {V.TPKGY.loc['2026-06-01':'2026-07-24'].mean():.0f} units/day"]
a = load_allocation("TLY")
col = [c for c in a.columns if "Gayrimenkul" in c][0]
out.append("TLY real-estate fund units, % of portfolio: " + ", ".join(f"{d.date()} {a.loc[d, col]:.2f}" for d in a.loc["2026-07-24":"2026-07-31"].index))
o = read_price_export(RAW / "prices/OZATD.xlsx")
d = o.loc["2026-05-14"]
n = 13_036_219
out.append(f"OZATD 30 Apr: close {P.OZATD['2026-04-30']}, volume {V.OZATD['2026-04-30'] / 1e6:.2f}m (block of 15.6m shares at 212 TL per KAP)")
out.append(f"OZATD 14 May: low {d.Low}, high {d.High}, volume {V.OZATD['2026-05-14'] / 1e6:.2f}m → cost of {n:,} shares {n * d.Low / 1e9:.2f}–{n * d.High / 1e9:.2f} bn TL (13m × 212 = {13e6 * 212 / 1e9:.2f} bn)")
out.append(f"OZATD 28+31 Aug volume: {(V.OZATD['2026-08-28'] + V.OZATD['2026-08-31']) / 1e6:.2f}m shares; TLY sales pending settlement per KAP Aug report: 3.25m")
write("events.txt", "\n".join(out))
