"""Step 6: figures transcribed from TLY's KAP monthly portfolio reports (February and August 2026).
Each number is copied from the report; re-check against the PDFs listed in data/README.md."""
from common import write

FEB = dict(fpd=62_748_701_548.72,
           tera_shares=11_702_987_497.08 + 139_422_096.00 + 4_081_808_229.00 + 27_065_632.50 + 132_931_681.00 + 1_762_813_080.28,
           repo_to_tera_portfoy=7_145_163_835.62, repo_to_pardus=2_388_411_506.85, tpkgy_units=7_677_376_341.12)
AUG = dict(ftd=268_781_591_425.07,
           tyb_notes=5_299_170_238.37 + 1_135_350_228.22 + 703_458_571.13 + 3_836_739_806.18,
           tvk_leases=8_228_758_844.47 + 103_585_049.06, repo_borrowing=19_043_896_207.31,
           rrepo_to_tera_portfoy=38_945_827_397.26, collateral_units=78_115.74, receivables=33_516_976_940.38)
NAV_TPKGY = 8122.13
g = AUG["tyb_notes"] + AUG["tvk_leases"]
out = ["February 2026 report (% of fund portfolio value):",
       f"  Tera group shares (TERA, TRHOL, TEHOL): {100 * FEB['tera_shares'] / FEB['fpd']:.1f}%",
       f"  OTC reverse repo to Tera Portföy: {FEB['repo_to_tera_portfoy'] / 1e9:.2f} bn ({100 * FEB['repo_to_tera_portfoy'] / FEB['fpd']:.1f}%); to Pardus Portföy: {FEB['repo_to_pardus'] / 1e9:.2f} bn",
       f"  TPKGY units: {FEB['tpkgy_units'] / 1e9:.2f} bn ({100 * FEB['tpkgy_units'] / FEB['fpd']:.1f}%)",
       "August 2026 report (% of fund total value):",
       f"  Tera Yatırım Bankası notes {AUG['tyb_notes'] / 1e9:.2f} bn + Tera Varlık Kiralama lease certificates {AUG['tvk_leases'] / 1e9:.2f} bn = {g / 1e9:.2f} bn ({100 * g / AUG['ftd']:.1f}%)",
       f"  Repo borrowing against those papers: {AUG['repo_borrowing'] / 1e9:.2f} bn ({100 * AUG['repo_borrowing'] / AUG['ftd']:.1f}%)",
       f"  Overnight reverse repo to Tera Portföy against TPKGY units: {AUG['rrepo_to_tera_portfoy'] / 1e9:.2f} bn ({100 * AUG['rrepo_to_tera_portfoy'] / AUG['ftd']:.1f}%)",
       f"  Collateral column {AUG['collateral_units']:,.2f}, read as units, × NAV {NAV_TPKGY:,.2f} = {AUG['collateral_units'] * NAV_TPKGY / 1e9:.2f} bn TL",
       f"  Receivables (sales awaiting settlement): {AUG['receivables'] / 1e9:.2f} bn"]
write("kap_reports.txt", "\n".join(out))
