"""Step 3: does TLY's reported daily return track same-day or previous-day moves in its largest holdings?"""
from common import *

P = pd.read_csv(INTERIM / "prices.csv", index_col=0, parse_dates=True)
R = P.drop(columns="TPKGY", errors="ignore").pct_change()
g = load_general("TLY")
g = g[g["Fiyat"] > 0].set_index("Tarih")
fr = g["Fiyat"].pct_change()
xs, ys = {0: [], 1: []}, []
for d in fr.loc["2026-07-02":"2026-09-16"].index:
    if d not in R.index:
        continue
    i = R.index.get_loc(d)
    w = WEIGHTS[d.strftime("%Y-%m")]
    for lag in (0, 1):
        xs[lag].append(sum(w[s] / 100 * R.iloc[i - lag][s] for s in w))
    ys.append(fr[d])
out = ["Stale-pricing test, 2 Jul – 16 Sep 2026 (weights: common.WEIGHTS)."]
for lag in (0, 1):
    c = np.corrcoef(xs[lag], ys)[0, 1]
    b = np.polyfit(xs[lag], ys, 1)[0]
    out.append(f"  lag {lag}: corr = {c:.3f}, slope = {b:.2f}, n = {len(ys)}")
d = pd.Timestamp("2026-09-16")
w = WEIGHTS["2026-09"]
same = sum(w[s] / 100 * R.loc[d, s] for s in w)
prev = sum(w[s] / 100 * R.iloc[R.index.get_loc(d) - 1][s] for s in w)
out.append(f"16 Sep: fund {100 * fr[d]:+.2f}% | top-6 same day {100 * same:+.2f}% | previous day {100 * prev:+.2f}%")
r = P.loc["2026-09-25"] / P.loc["2026-09-15"] - 1
out.append("15→25 Sep: " + ", ".join(f"{s} {100 * r[s]:+.1f}%" for s in w) + f" | implied effect on TLY {100 * sum(w[s] / 100 * r[s] for s in w):+.1f}%")
write("stale_pricing.txt", "\n".join(out))
