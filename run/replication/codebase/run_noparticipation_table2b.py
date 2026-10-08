#!/usr/bin/env python3
"""Step 3: Table 2(b) - no participation responses (eta=0, eps=0.1).
With eta=0 the efficiency effects coincide (Dd=Dw) and tradeoff_demogrant <= tradeoff_workingpoor."""
import argparse, csv, json, os
import numpy as np, xlrd
from welfare_core import COUNTRIES, EPS_BENCHMARK, load_country, compute, XLS_PATH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/table2b.csv')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)

    wb = xlrd.open_workbook(XLS_PATH)
    eta0 = np.zeros(10)
    cols = ['country', 'eff_demogrant', 'tradeoff_demogrant',
            'eff_workingpoor', 'tradeoff_workingpoor', 'Dd_equals_Dw']
    rows, jd = [], {}
    for cc in COUNTRIES:
        r = compute(load_country(cc, wb), eta0, EPS_BENCHMARK)
        eq = bool(abs(r['Dd'] - r['Dw']) < 1e-9)
        row = {'country': cc,
               'eff_demogrant': r['eff_demogrant'],
               'tradeoff_demogrant': r['tradeoff_demogrant'],
               'eff_workingpoor': r['eff_workingpoor'],
               'tradeoff_workingpoor': r['tradeoff_workingpoor'],
               'Dd_equals_Dw': eq}
        rows.append(row); jd[cc] = row
        print(f"{cc} eff_d={row['eff_demogrant']:+.3f} eff_w={row['eff_workingpoor']:+.3f} "
              f"psi_d={row['tradeoff_demogrant']:.3f} psi_w={row['tradeoff_workingpoor']:.3f} "
              f"Dd=Dw:{eq} psi_d<=psi_w:{row['tradeoff_demogrant'] <= row['tradeoff_workingpoor'] + 1e-9}")

    alleq = all(r['Dd_equals_Dw'] for r in rows)
    allorder = all(r['tradeoff_demogrant'] <= r['tradeoff_workingpoor'] + 1e-9 for r in rows)
    print(f"\nAll Dd==Dw: {alleq}   All psi_d<=psi_w: {allorder}")
    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    with open(os.path.splitext(args.out)[0] + '.json', 'w') as f:
        json.dump(jd, f, indent=2)
    print(f"Wrote {args.out} ({len(rows)} rows)")


if __name__ == '__main__':
    main()
