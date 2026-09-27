"""Step 2: decompose daily changes in fund size into net flows and valuation.
    flow_t      = (units_t - units_{t-1}) * price_t
    valuation_t = (size_t - size_{t-1}) - flow_t
"""
from common import *


def prep(code):
    g = load_general(code)
    g = g[g["Fiyat"] > 0].reset_index(drop=True)
    g["flow_bn"] = g["Tedavüldeki Pay Sayısı"].diff() * g["Fiyat"] / 1e9
    g["size_bn"] = g["Fon Toplam Değer"] / 1e9
    g["valuation_bn"] = g["size_bn"].diff() - g["flow_bn"]
    return g


def window(g, a, b):
    s0 = g[g.Tarih <= a].iloc[-1]
    s = g[(g.Tarih > a) & (g.Tarih <= b)]
    s1 = s.iloc[-1]
    return dict(size_start=s0.size_bn, size_end=s1.size_bn, net_flow=s.flow_bn.sum(), valuation=s.valuation_bn.sum(),
                price_chg_pct=100 * (s1.Fiyat / s0.Fiyat - 1),
                units_chg_pct=100 * (s1["Tedavüldeki Pay Sayısı"] / s0["Tedavüldeki Pay Sayısı"] - 1),
                investors_start=int(s0["Kişi Sayısı"]), investors_end=int(s1["Kişi Sayısı"]))


out = ["Flow/valuation decomposition (bn TL). Source: TEFAS 'Genel Bilgiler' exports.", ""]
t = prep("TLY")
t[["Tarih", "Fiyat", "Tedavüldeki Pay Sayısı", "Kişi Sayısı", "size_bn", "flow_bn", "valuation_bn"]].round(4).to_csv(RESULTS / "tly_daily_flows.csv", index=False)
ends = ["2026-01-02", "2026-01-30", "2026-02-27", "2026-03-31", "2026-04-30", "2026-05-29", "2026-06-30", "2026-07-31", "2026-08-31", "2026-09-16"]
rows = []
out.append("TLY by month:")
for a, b in zip(ends[:-1], ends[1:]):
    w = window(t, a, b)
    rows.append(dict(start=a, end=b, **w))
    out.append(f"  {a}→{b}: size {w['size_start']:6.1f}→{w['size_end']:6.1f} | flow {w['net_flow']:+7.1f} | valuation {w['valuation']:+7.1f} | price {w['price_chg_pct']:+6.1f}% | investors {w['investors_start']:,}→{w['investors_end']:,}")
pd.DataFrame(rows).round(2).to_csv(RESULTS / "tly_monthly.csv", index=False)
w = window(t, "2026-01-02", "2026-08-17")
out.append(f"\nTLY 02.01→17.08: size {w['size_start']:.1f}→{w['size_end']:.1f}; net flow {w['net_flow']:+.1f}; valuation {w['valuation']:+.1f}; investors {w['investors_start']:,}→{w['investors_end']:,}")
w = window(t, "2026-08-17", "2026-09-16")
out.append(f"TLY 17.08→16.09: net flow {w['net_flow']:+.1f}; valuation {w['valuation']:+.1f}; price {w['price_chg_pct']:+.1f}%; units {w['units_chg_pct']:+.1f}%; investors {w['investors_start']:,}→{w['investors_end']:,} ({100 * (w['investors_end'] / w['investors_start'] - 1):+.1f}%)")
out.append("\nTLY five largest daily outflows:")
out += ["  " + r for r in t.nsmallest(5, "flow_bn")[["Tarih", "flow_bn"]].round(2).to_string(index=False).splitlines()]
ex = t[t.Tarih == "2026-09-02"].iloc[0]
prev = t[t.Tarih < "2026-09-02"].iloc[-1]
out.append(f"\nWorked example, 2 Sep 2026: units {prev['Tedavüldeki Pay Sayısı']:,.0f} → {ex['Tedavüldeki Pay Sayısı']:,.0f}; price {ex.Fiyat:,.6f};"
           f" flow = ({ex['Tedavüldeki Pay Sayısı']:,.0f} − {prev['Tedavüldeki Pay Sayısı']:,.0f}) × {ex.Fiyat:,.6f} = {ex.flow_bn:+.2f} bn TL;"
           f" size {prev.size_bn:.2f} → {ex.size_bn:.2f} bn (Δ {ex.size_bn - prev.size_bn:+.2f}); valuation = Δsize − flow = {ex.valuation_bn:+.2f} bn TL")
for code in ["TP2", "PRY", "PSE"]:
    try:
        g = prep(code)
    except FileNotFoundError:
        continue
    pk = g.loc[g.size_bn.idxmax()]
    out.append(f"\n{code}: {g.Tarih.min().date()}→{g.Tarih.max().date()}; peak {pk.size_bn:.1f} bn on {pk.Tarih.date()}; last {g.size_bn.iloc[-1]:.1f} bn")
    out += ["  " + r for r in g[g.Tarih >= "2026-09-10"][["Tarih", "size_bn", "flow_bn", "Kişi Sayısı"]].round(2).to_string(index=False).splitlines()]
write("flows.txt", "\n".join(out))
