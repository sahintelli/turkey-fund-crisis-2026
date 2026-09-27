# Method

## 1. Flows versus valuation (step 2)

For each trading day *t*, with units outstanding *U*, unit price *P* and fund total value *S* from TEFAS:

- net flow: **F_t = (U_t − U_{t−1}) × P_t**
- valuation change: **G_t = (S_t − S_{t−1}) − F_t**

Summing over a period splits the change in fund size into money that came in or out (F) and changes in the value of what the fund held, plus fees and income (G).

**Worked example (2 Sep 2026, TLY):** units fell from 29,214,243 to 26,825,517 at a price of 9,293.9339 TL. F = −2,388,726 × 9,293.9339 = **−22.20 bn TL**. Fund value fell from 268.78 to 249.31 bn TL (Δ −19.47 bn), so G = −19.47 − (−22.20) = **+2.73 bn TL**.

**Caveat:** subscriptions and redemptions on day *t* are executed at the price published for *t*, which is computed from day *t−1* closing prices (see §2). Valuing flows at P_t is therefore the correct transaction price.

## 2. Stale-pricing test (step 3)

Daily fund return *r_t = P_t / P_{t−1} − 1* is compared with the weighted return of the six largest equity holdings, using monthly weights (end of the previous month, `src/common.py`):

- same day: *x⁰_t = Σ w_i · R_{i,t}*
- previous day: *x¹_t = Σ w_i · R_{i,t−1}*

Sample: 2 Jul – 16 Sep 2026, n = 54 days with both series. Result: corr(r, x⁰) = −0.155; corr(r, x¹) = 0.747 (OLS slope 0.65). Fund documents in the same group state the dealing rule explicitly: orders are executed at "the price calculated on the previous business day" (Pusula Portföy PRY investor information form, 9 Mar 2026). TLY's own dealing terms were not examined.

## 3. Liquidity (step 4)

Days to sell position *i* at participation rate *p* (share of daily traded value the fund takes): **days_i = position_i / (p × ADV_i)**, where ADV is the mean of price × volume from 17 Aug to 15 Sep 2026 and positions are end-August weights × fund value on 31 Aug.

## 4. Event checks (step 5)

TPKGY: traded value on 27–28 Jul = Σ price × volume; value at NAV = units × 8,122.13 TL (manager's NAV at 30 Jun 2026). OZATD 14 May: cost range = 13,036,219 shares × [day low, day high].

## 5. KAP report figures (step 6)

Line items are transcribed from the PDFs and summed; percentages use the report's own denominators (fund portfolio value in February, fund total value in August). The August collateral column (78,115.74) is read as a number of TPKGY units; the report does not label its unit explicitly.

## Assumptions and limitations

- **Weights** are monthly (aggregator, grade C); intra-month changes in holdings are not captured. This affects §2 and §3, not §1.
- **Exchange prices** come from a secondary provider; spot checks against KAP-disclosed trade prices matched (e.g. OZATD block volume on 30 Apr).
- **Fund size dates:** TEFAS total value on 31 Aug (273.3 bn TL) differs from the KAP August report's total value (268.8 bn TL) because of reporting timing and T−1 pricing. Each figure is quoted with its own source.
- **TEFAS "Diğer" and category mapping:** money market "liquid" assets = reverse repo + BIST money market + deposits + participation accounts + government paper.
- Days with zero published price (after 16 Sep for TLY) are excluded.
