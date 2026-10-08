#!/usr/bin/env python3
"""Step 4: Table 4 - sensitivity to hours-of-work elasticity eps in {0, 0.1, 0.2},
holding the benchmark participation profile eta=[.4,.4,.3,.3,.2,.2,.1,.1,0,0] fixed.
The eps=0.1 block equals Table 2(a)."""
import argparse, csv, json, os
import xlrd
from welfare_core import COUNTRIES, ETA_BENCHMARK, load_country, compute, XLS_PATH

EPS_LEVELS = [0.0, 0.1, 0.2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/table4.csv')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)

    wb = xlrd.open_workbook(XLS_PATH)
    # Wide table: one row per country, 4 metrics x 3 eps levels = 12 numeric columns.
    cols = ['country']
    for e in EPS_LEVELS:
        tag = f"eps{e:g}"
        cols += [f'eff_demogrant_{tag}', f'tradeoff_demogrant_{tag}',
                 f'eff_workingpoor_{tag}', f'tradeoff_workingpoor_{tag}']
    rows, jd = [], {}
    for cc in COUNTRIES:
        data = load_country(cc, wb)
        row = {'country': cc}; jd[cc] = {}
        for e in EPS_LEVELS:
            r = compute(data, ETA_BENCHMARK, e)
            tag = f"eps{e:g}"
            row[f'eff_demogrant_{tag}'] = r['eff_demogrant']
            row[f'tradeoff_demogrant_{tag}'] = r['tradeoff_demogrant']
            row[f'eff_workingpoor_{tag}'] = r['eff_workingpoor']
            row[f'tradeoff_workingpoor_{tag}'] = r['tradeoff_workingpoor']
            jd[cc][tag] = {k: r[k] for k in
                           ('eff_demogrant', 'tradeoff_demogrant',
                            'eff_workingpoor', 'tradeoff_workingpoor')}
        rows.append(row)
        print(f"{cc}: " + "  ".join(
            f"eps={e:g}[d {row[f'eff_demogrant_eps{e:g}']:+.2f}/{row[f'tradeoff_demogrant_eps{e:g}']:.2f} "
            f"w {row[f'eff_workingpoor_eps{e:g}']:+.2f}/{row[f'tradeoff_workingpoor_eps{e:g}']:.2f}]"
            for e in EPS_LEVELS))

    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    with open(os.path.splitext(args.out)[0] + '.json', 'w') as f:
        json.dump(jd, f, indent=2)
    print(f"\nWrote {args.out} ({len(rows)} rows, {len(cols)-1} numeric cols)")


if __name__ == '__main__':
    main()
