#!/usr/bin/env python3
"""Aggregate the continuation's variant checkpoints (V5, V6, lhw40, V3, ssc_inv)
into welfare_variants.csv, under the headline V4 (q=0) regime for comparability.
Also emits variant decile/bottom-quintile rows for the variant-vs-headline figure.
"""
import os, json
import numpy as np, pandas as pd
import fixed_inputs as fi, welfare_layer as wl
from aggregate import psi_stability  # reuse stability logic (q=0 regime)

RES = '/workspace/eval/followup/002-living-update-cont/results'
VARIANTS = ['headline', 'V5', 'V6', 'lhw40', 'V3', 'ssc_inv']
VAR_YEARS = {'V5': [2009, 2015, 2020, 2026], 'V6': [2009, 2015, 2020, 2026],
             'lhw40': [2009, 2015, 2020, 2026], 'V3': [2009, 2015, 2020, 2026],
             'ssc_inv': [2025]}
GROSS_BASIS = {'EL', 'IT'}


def main():
    rows = []
    for variant in VARIANTS:
        years = VAR_YEARS.get(variant, list(range(2009, 2027)))
        for CC in fi.EM_COUNTRIES:
            for y in years:
                cr = wl.load_cells(CC, y, variant)
                if cr is None:
                    continue
                st = psi_stability(CC, y, variant=variant, q_override=0.0)
                if st is None:
                    continue
                dp = wl.decile_profile(CC, y, variant=variant, q_override=0.0, cap=np.inf)
                rows.append(dict(
                    variant=variant, c=CC, t=y,
                    Psi_d=round(st['Psi_d'], 4) if np.isfinite(st['Psi_d']) else None,
                    Psi_d_stab=st['Psi_d_stab'],
                    Psi_w=round(st['Psi_w'], 4) if np.isfinite(st['Psi_w']) else None,
                    Psi_w_stab=st['Psi_w_stab'],
                    eff_d=round(st['eff_demogrant'], 4), eff_w=round(st['eff_workingpoor'], 4),
                    a_bottom_quintile=round(100 * dp['a_bottom_quintile'], 2),
                    a_decile1=round(100 * dp['a_d'][0], 2) if np.isfinite(dp['a_d'][0]) else None,
                    tau_decile1=round(100 * dp['tau_d'][0], 2) if np.isfinite(dp['tau_d'][0]) else None,
                    flags='gross_basis' if CC in GROSS_BASIS else ''))
    df = pd.DataFrame(rows)
    df.to_csv(f'{RES}/welfare_variants.csv', index=False)
    print(f"wrote welfare_variants.csv ({len(df)} rows)")
    # summary: mean |delta a_bottom_quintile| vs headline for each variant, by year
    piv = df.pivot_table(index=['c', 't'], columns='variant', values='a_bottom_quintile')
    summ = {}
    for v in ['V5', 'V6', 'lhw40', 'V3', 'ssc_inv']:
        if v in piv.columns and 'headline' in piv.columns:
            d = (piv[v] - piv['headline']).dropna()
            summ[v] = dict(mean_abs_delta_a12_pp=round(float(d.abs().mean()), 2),
                           max_abs_delta_a12_pp=round(float(d.abs().max()), 2),
                           n=int(len(d)))
    json.dump(summ, open(f'{RES}/variant_summary.json', 'w'), indent=2)
    print(json.dumps(summ, indent=2))


if __name__ == '__main__':
    main()
