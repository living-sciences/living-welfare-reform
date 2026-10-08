#!/usr/bin/env python3
"""Gate 3b (change gate). Compares the no-UB PTR CHANGE between first and last gate
year, ours vs OECD TaxBEN DF_PTRSA, for S_C0 at AW67 and the lowest available level
(MINW where it exists in both years). Pass per comparison: sign match AND
|dPTR_ours - dPTR_taxben| <= 5 pp; sign waived where |dPTR_taxben| < 1 pp.
A country passes 3b iff every comparison passes -> forms V_delta. Writes
results/gate3b_change.csv.
"""
import os, sys, csv
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he
from gate3 import ISO3, taxben_val, minw_month, ours_ptr, _load_ben, LAST2024

RES = '/workspace/eval/followup/001-living-update/results'


def run_country(CC, root, house):
    ptrsa, _ = _load_ben()
    iso = ISO3[CC]
    cy = he.CY(CC, root); cy.probe_earnvar(2015)
    y0, y1 = 2010, (2024 if CC in LAST2024 else 2025)
    rows = []
    # S_C0 AW67, and S_C0 at MINW (if both years have a MINW row)
    for inc in ['AW67', 'MINW']:
        tb0 = taxben_val(ptrsa, iso, y0, 'S_C0', inc, '_Z', house, 'noUB')
        tb1 = taxben_val(ptrsa, iso, y1, 'S_C0', inc, '_Z', house, 'noUB')
        if inc == 'MINW' and (tb0 is None or tb1 is None):
            rows.append(dict(c=CC, income_curr=inc, y0=y0, y1=y1, d_ours=None,
                             d_taxben=None, status='no_benchmark_both_years', passed=None))
            continue
        if tb0 is None or tb1 is None:
            continue
        aw0, aw1 = fi.aw_month(CC, y0), fi.aw_month(CC, y1)
        e0 = (0.67*aw0 if inc == 'AW67' else minw_month(CC, y0))
        e1 = (0.67*aw1 if inc == 'AW67' else minw_month(CC, y1))
        o0, _ = ours_ptr(cy, y0, 1, aw0, e0, 'noUB')
        o1, _ = ours_ptr(cy, y1, 1, aw1, e1, 'noUB')
        d_ours = o1 - o0; d_tb = tb1 - tb0
        sign_ok = (np.sign(d_ours) == np.sign(d_tb)) or (abs(d_tb) < 1.0)
        mag_ok = abs(d_ours - d_tb) <= 5.0
        passed = bool(sign_ok and mag_ok)
        rows.append(dict(c=CC, income_curr=inc, y0=y0, y1=y1,
                         d_ours=round(d_ours, 1), d_taxben=round(d_tb, 1),
                         status='ok', passed=passed))
    return rows


def main():
    CC = sys.argv[1]; root = sys.argv[2]; house = sys.argv[3] if len(sys.argv) > 3 else 'NO'
    rows = run_country(CC, root, house)
    path = f'{RES}/gate3b_change.csv'
    newf = not os.path.exists(path)
    fields = ['c', 'income_curr', 'y0', 'y1', 'd_ours', 'd_taxben', 'status', 'passed']
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if newf: w.writeheader()
        for r in rows: w.writerow(r)
    ok = [r for r in rows if r['status'] == 'ok']
    cpass = all(r['passed'] for r in ok) and len(ok) > 0
    print(f"[{CC}] 3b: {[(r['income_curr'], r['d_ours'], r['d_taxben'], r['passed']) for r in ok]} "
          f"=> {'PASS (in V_delta)' if cpass else 'FAIL'}")


if __name__ == '__main__':
    main()
