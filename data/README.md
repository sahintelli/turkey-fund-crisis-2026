# Raw data: what to download and where to put it

All files were downloaded on 26 September 2026. The scripts only need the folder layout below; file names inside each folder are free.

## 1. TEFAS fund data → `data/raw/tefas/<FUND>/<tab>/`

Source: TEFAS › *Tarihsel Veriler* (https://www.tefas.gov.tr). Search the fund code, choose the date range, and export each tab to Excel.

| Fund | Tab | Folder | Period used |
|---|---|---|---|
| TLY | Genel Bilgiler (price, units outstanding, investor count, total value) | `tefas/TLY/general/` | 2 Jan – 16 Sep 2026 |
| TLY | Portföy Dağılımı (daily % by asset class) | `tefas/TLY/allocation/` | 2 Jan – 16 Sep 2026 |
| TP2, PRY, PSE | Genel Bilgiler | `tefas/<FUND>/general/` | 1 Jul – 25 Sep 2026 |
| TP2, PRY, PSE | Portföy Dağılımı | `tefas/<FUND>/allocation/` | 1 Jul – 25 Sep 2026 |

TEFAS limits each export to about three months, so monthly exports are fine; step 1 merges them and removes duplicate dates. Known gap: PSE *Genel Bilgiler* for July 2026 was not available in our exports (series starts 3 Aug).

## 2. Daily prices and volumes → `data/raw/prices/<TICKER>.xlsx`

Tickers: DSTKF, OZATD, TEHOL, TRHOL, PEKGY, ANELE, TPKGY (Borsa Istanbul). Period: 1 Jan – 25 Sep 2026.
Format expected (Investing.com "Historical Data" export): columns `Date` (e.g. `Sep 25, 2026`), `Price`, `Open`, `High`, `Low`, `Vol.` (e.g. `1.25M`), `Change %`.
Volume for TPKGY is in fund units.

## 3. Documents read (not needed to run the code)

| Document | Link |
|---|---|
| KAP, TLY monthly portfolio report, Feb 2026 | https://kap.org.tr/tr/api/file/download/4028328d9c81f588019cb8777b345e7e |
| KAP, TLY monthly portfolio report, Aug 2026 | https://kap.org.tr/tr/api/file/download/4028328c9f52dc4001a06121eaab4d7f |
| SPK Bulletins 2023/76, 2026/47, 2026/59–65 | https://spk.gov.tr/spk-bultenleri |
| SPK Investment Funds Guideline (as amended 28 Aug 2026) | https://spk.gov.tr/data/6a91fe7d8f95db1fb01ff366/Yat%C4%B1r%C4%B1m%20Fonlar%C4%B1na%20%C4%B0li%C5%9Fkin%20Rehber.pdf |

The full reference list is in the case file.
