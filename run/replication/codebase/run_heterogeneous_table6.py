#!/usr/bin/env python3
"""Step 5: Table 6 - participation elasticities heterogeneous across demographic groups.
Panel (a): benchmark (eta varies only with decile) = Table 2(a).
Panel (b): eta concentrated on female groups 2,4,6,8,10 with profile
           [.9,.9,.6,.6,.4,.4,.2,.2,0,0]; eta=0 for groups 1,3,5,7,9. eps=0.1 throughout."""
import argparse, csv, json, os
import xlrd
from welfare_core import (COUNTRIES, ETA_BENCHMARK, EPS_BENCHMARK,
                          load_country, compute, eta_table6_hetero, XLS_PATH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/table6.csv')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)

    wb = xlrd.open_workbook(XLS_PATH)
    eta_b = eta_table6_hetero()
    cols = ['country',
            'eff_demogrant_a', 'tradeoff_demogrant_a', 'eff_workingpoor_a', 'tradeoff_workingpoor_a',
            'eff_demogrant_b', 'tradeoff_demogrant_b', 'eff_workingpoor_b', 'tradeoff_workingpoor_b']
    rows, jd = [], {}
    for cc in COUNTRIES:
        data = load_country(cc, wb)
        ra = compute(data, ETA_BENCHMARK, EPS_BENCHMARK)
        rb = compute(data, eta_b, EPS_BENCHMARK)
        row = {'country': cc,
               'eff_demogrant_a': ra['eff_demogrant'], 'tradeoff_demogrant_a': ra['tradeoff_demogrant'],
               'eff_workingpoor_a': ra['eff_workingpoor'], 'tradeoff_workingpoor_a': ra['tradeoff_workingpoor'],
               'eff_demogrant_b': rb['eff_demogrant'], 'tradeoff_demogrant_b': rb['tradeoff_demogrant'],
               'eff_workingpoor_b': rb['eff_workingpoor'], 'tradeoff_workingpoor_b': rb['tradeoff_workingpoor']}
        rows.append(row); jd[cc] = row
        wp_below = row['tradeoff_workingpoor_b'] <= row['tradeoff_demogrant_b'] + 1e-9
        print(f"{cc} (b): eff_d={row['eff_demogrant_b']:+.3f} psi_d={row['tradeoff_demogrant_b']:7.3f} "
              f"eff_w={row['eff_workingpoor_b']:+.3f} psi_w={row['tradeoff_workingpoor_b']:7.3f} "
              f"wp_tradeoff<demo:{wp_below}")

    allbelow = all(r['tradeoff_workingpoor_b'] <= r['tradeoff_demogrant_b'] + 1e-9 for r in rows)
    print(f"\nPanel(b) working-poor trade-off below demogrant in all countries: {allbelow}")
    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    with open(os.path.splitext(args.out)[0] + '.json', 'w') as f:
        json.dump(jd, f, indent=2)
    print(f"Wrote {args.out} ({len(rows)} rows)")


if __name__ == '__main__':
    main()
