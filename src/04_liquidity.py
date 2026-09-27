"""Step 4: trading days needed to sell TLY's largest positions.
    days = position / (participation * average daily traded value)"""
from common import *

P = pd.read_csv(INTERIM / "prices.csv", index_col=0, parse_dates=True)
V = pd.read_csv(INTERIM / "volumes.csv", index_col=0, parse_dates=True)
g = load_general("TLY").set_index("Tarih")
size = g.loc["2026-08-31", "Fon Toplam Değer"]
adv = (P * V).loc["2026-08-17":"2026-09-15"].mean()
out = [f"TLY size 31 Aug 2026: {size / 1e9:.1f} bn TL; weights end-August; ADV = mean(price × volume), 17 Aug–15 Sep 2026",
       "stock   position_bn  ADV_bn   days@100%  days@20%  days@10%"]
for s, w in WEIGHTS["2026-09"].items():
    pos = w / 100 * size
    out.append(f"{s:6s} {pos / 1e9:10.1f} {adv[s] / 1e9:8.3f} {pos / adv[s]:10.0f} {pos / (0.2 * adv[s]):9.0f} {pos / (0.1 * adv[s]):9.0f}")
write("liquidity.txt", "\n".join(out))
