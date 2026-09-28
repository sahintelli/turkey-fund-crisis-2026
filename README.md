# Turkey's 2026 fund collapse: reproducible analysis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23004452.svg)](https://doi.org/10.5281/zenodo.23004452)

Code, derived results and figures behind the case file **"Turkey's 2026 fund collapse: who left first"** by Dr. Sahin Telli.

The case file reconstructs how Turkey's largest hedge fund (TLY, Tera Portföy Birinci Serbest Fon) grew about eightfold in 2026, how its reported price rose during the run that preceded the liquidation of 131 funds on 17 September 2026, and how "safe" money market funds were affected. This repository lets anyone recompute every figure in the case file that is derived from data.

> Educational material. Not investment, legal or financial advice. Nobody named in the underlying sources has been convicted of any offence; investigations are ongoing.

## What is here

| Path | Contents |
|---|---|
| `src/` | Numbered Python scripts, run in order (see below) |
| `results/` | Text and CSV outputs of each step (derived figures quoted in the case file) |
| `figures/` | Charts (PNG and SVG, English and Chinese labels), produced by step 7 |
| `docs/method.md` | Formulas, worked examples, assumptions and limitations |
| `data/README.md` | Exactly which raw files to download, from where, and where to put them |
| `CITATION.cff` | How to cite this work |

Raw data files are **not** redistributed here (see *Data and licensing*). `data/raw/` and `data/interim/` are git-ignored.

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# 1. Download the raw files listed in data/README.md into data/raw/
# 2. Run the pipeline
bash run_all.sh
```

| Step | Script | Produces |
|---|---|---|
| 1 | `01_build_interim.py` | Tidy daily CSVs in `data/interim/` from TEFAS and price exports |
| 2 | `02_flows.py` | Daily and monthly flow/valuation decomposition (`results/flows.txt`, `tly_daily_flows.csv`, `tly_monthly.csv`) |
| 3 | `03_stale_pricing.py` | Same-day vs previous-day correlation test (`results/stale_pricing.txt`) |
| 4 | `04_liquidity.py` | Days needed to sell the largest positions (`results/liquidity.txt`) |
| 5 | `05_events.py` | Exchange activity around the TPKGY exit and OZATD transactions (`results/events.txt`) |
| 6 | `06_kap_reports.py` | Figures transcribed from TLY's February and August 2026 KAP reports (`results/kap_reports.txt`) |
| 7 | `07_figures.py` | All charts in `figures/` |

Expected key outputs (to check your run):

| Quantity | Value |
|---|---|
| TLY net flow, 17 Aug → 16 Sep 2026 | −85.5 bn TL |
| TLY valuation change, same window | +46.8 bn TL |
| Correlation of fund return with same-day / previous-day top-6 holdings return | −0.155 / 0.747 |
| TPKGY units traded 27–28 Jul 2026 | 46,620 (≈26.7 bn TL) |
| Reverse repo to Tera Portföy, 31 Aug 2026 (KAP) | 38.95 bn TL (14.5% of fund) |

## Data and licensing

- **TEFAS** (fund prices, units, investors, total value, portfolio breakdown) and **KAP** (fund reports, disclosures) are official public platforms. Check their current terms of use before redistributing raw exports.
- **Exchange price and volume data** were exported from Investing.com, whose terms restrict redistribution. They are therefore not included; `data/README.md` explains how to download them. Any equivalent source of Borsa Istanbul daily closing prices and volumes will work if saved in the same format.
- **Portfolio weights** of the six largest holdings come from Fonoloji monthly holdings pages and are hard-coded, with their source, in `src/common.py`.

Code: MIT License (`LICENSE`). Text, results and figures: CC BY 4.0 (`LICENSE-CONTENT`).

## Citation

Archived on Zenodo. All versions (always resolves to the latest): https://doi.org/10.5281/zenodo.23004452

To cite the specific version you used, use its version DOI. For v1.0.0:

> Telli, S. (2026). *Turkey's 2026 fund collapse: who left first — reproducible analysis* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23004453

Machine-readable metadata: `CITATION.cff`.

## Contact and corrections

Corrections are welcome via GitHub issues. Every correction is recorded in the case file's version notes.
