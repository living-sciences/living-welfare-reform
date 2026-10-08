#!/usr/bin/env python3
"""Step 6: Table 3 - critical average participation elasticities.
Profile = eta_table3_profile(eta_avg): 2*avg(dec1-2),1.5*avg(3-4),avg(5-6),0.5*avg(7-8),0(9-10).
eps=0.1 fixed. For each country solve for eta_avg where:
  (a) crit_identical : Psi_w = Psi_d  (trade-offs equal)
  (b) crit_zeroloss  : Dw = 0  (Psi_w = 1, zero efficiency loss)
  (c) crit_pareto    : working-poor policy becomes a Pareto improvement (no losers / Psi_w->0)
Root-finder: scipy.optimize.brentq with a sign-change scan to bracket."""
import argparse, csv, json, os
import numpy as np, xlrd
from scipy.optimize import brentq
from welfare_core import (COUNTRIES, EPS_BENCHMARK, load_country, compute,
                          eta_table3_profile, XLS_PATH)


def _bracket_root(f, lo=1e-6, hi=3.0, n=600):
    """Scan [lo,hi] for first sign change of f and brentq it; None if none found."""
    xs = np.linspace(lo, hi, n)
    prev_x, prev_f = xs[0], f(xs[0])
    for x in xs[1:]:
        fx = f(x)
        if np.isfinite(prev_f) and np.isfinite(fx) and prev_f == 0:
            return prev_x
        if np.isfinite(prev_f) and np.isfinite(fx) and prev_f * fx < 0:
            return brentq(f, prev_x, x, xtol=1e-10)
        prev_x, prev_f = x, fx
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='results/table3.csv')
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    wb = xlrd.open_workbook(XLS_PATH)

    cols = ['country', 'crit_identical', 'crit_zeroloss', 'crit_pareto']
    rows, jd = [], {}
    for cc in COUNTRIES:
        data = load_country(cc, wb)
        maxse = (data['sh'] / np.where(data['em'] > 0, data['em'], np.inf)).max()  # max s_j/e_j

        def metrics(ea):
            return compute(data, eta_table3_profile(ea), EPS_BENCHMARK)

        # (a) Psi_w - Psi_d = 0
        crit_identical = _bracket_root(lambda ea: metrics(ea)['tradeoff_workingpoor']
                                       - metrics(ea)['tradeoff_demogrant'])
        # (b) Dw = 0
        crit_zeroloss = _bracket_root(lambda ea: metrics(ea)['Dw'])
        # (c) Pareto: 1 - Dw = max_j(s_j/e_j)  (last/richest worker just gains -> no losers)
        crit_pareto = _bracket_root(lambda ea: (1 - metrics(ea)['Dw']) - maxse)

        row = {'country': cc,
               'crit_identical': crit_identical,
               'crit_zeroloss': crit_zeroloss,
               'crit_pareto': crit_pareto}
        rows.append(row); jd[cc] = row
        ordered = (crit_identical is not None and crit_zeroloss is not None
                   and crit_pareto is not None
                   and crit_identical < crit_zeroloss < crit_pareto)
        fmt = lambda v: f"{v:.3f}" if v is not None else "  None"
        print(f"{cc}  identical={fmt(crit_identical)}  zeroloss={fmt(crit_zeroloss)}  "
              f"pareto={fmt(crit_pareto)}  ordered:{ordered}")

    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    with open(os.path.splitext(args.out)[0] + '.json', 'w') as f:
        json.dump(jd, f, indent=2)
    print(f"\nWrote {args.out} ({len(rows)} rows)")


if __name__ == '__main__':
    main()
