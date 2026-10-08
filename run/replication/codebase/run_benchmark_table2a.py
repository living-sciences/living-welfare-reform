#!/usr/bin/env python3
"""Step 2: Benchmark scenario -> Table 2(a) and Table 7 cols (1)-(2).
Benchmark: eps=0.1, eta=[.4,.4,.3,.3,.2,.2,.1,.1,0,0] (avg 0.2), constant across groups."""
import argparse, csv, json, os
import xlrd
from welfare_core import (COUNTRIES, ETA_BENCHMARK, EPS_BENCHMARK,
                          load_country, compute, XLS_PATH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/table2a.csv')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)

    wb = xlrd.open_workbook(XLS_PATH)
    cols = ['country', 'eff_demogrant', 'tradeoff_demogrant',
            'eff_workingpoor', 'tradeoff_workingpoor',
            'share_pop_gaining_demogrant', 'share_emp_gaining_workingpoor']
    rows, jd = [], {}
    for cc in COUNTRIES:
        r = compute(load_country(cc, wb), ETA_BENCHMARK, EPS_BENCHMARK)
        row = {'country': cc,
               'eff_demogrant': r['eff_demogrant'],
               'tradeoff_demogrant': r['tradeoff_demogrant'],
               'eff_workingpoor': r['eff_workingpoor'],
               'tradeoff_workingpoor': r['tradeoff_workingpoor'],
               'share_pop_gaining_demogrant': r['share_pop_gaining_demogrant'],
               'share_emp_gaining_workingpoor': r['share_emp_gaining_workingpoor']}
        rows.append(row); jd[cc] = row
        print(f"{cc} eff_d={row['eff_demogrant']:+.3f} psi_d={row['tradeoff_demogrant']:7.3f} "
              f"eff_w={row['eff_workingpoor']:+.3f} psi_w={row['tradeoff_workingpoor']:7.3f} "
              f"pg={row['share_pop_gaining_demogrant']:.3f} eg={row['share_emp_gaining_workingpoor']:.3f}")

    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    jpath = os.path.splitext(args.out)[0] + '.json'
    with open(jpath, 'w') as f:
        json.dump(jd, f, indent=2)
    print(f"\nWrote {args.out} ({len(rows)} rows) and {jpath}")


if __name__ == '__main__':
    main()
