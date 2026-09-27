#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/src"
for s in 01_build_interim 02_flows 03_stale_pricing 04_liquidity 05_events 06_kap_reports 07_figures; do
  echo "=== $s"; python "$s.py"
done
