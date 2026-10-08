#!/usr/bin/env python3
"""Employer-SSC inversion sensitivity, 2025 only (spec §3.2). The paper's deciles
are on a labour-cost basis (gross + employer SSC). The headline treats r as a
gross-earnings ratio; this sensitivity instead places each cell at the labour-cost
position r*(AW + sicer_AW), i.e. inverts so that gross + employer SSC = r*(AW +
employer SSC at AW).

First-order inversion (documented): using the headline-2025 per-cell employer-SSC
ratio sigma_cell = sicer/earns and the country AW-level ratio sigma_AW (from
input_conventions sicer_ratio_med_2025), the gross that reaches labour-cost
position r*(AW*(1+sigma_AW)) is r*AW*(1+sigma_AW)/(1+sigma_cell). So
r'_{g,d} = r_{g,d} * (1+sigma_AW)/(1+sigma_cell). Where employer SSC is
proportional (sigma_cell == sigma_AW) this is identity; it bites only under
non-proportional schedules (FR/BE low-wage relief, caps). Gross-basis countries
(sigma=0) are unaffected.
"""
import os, sys, time, csv, subprocess
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he

WS = '/workspace/eval/followup/002-living-update-cont/workspace'
ZIP = os.environ['J2_54']
Y = 2025


def main():
    ccs = sys.argv[1:] if len(sys.argv) > 1 else fi.EM_COUNTRIES
    ckdir = f'{WS}/checkpoints/ssc_inv'; os.makedirs(ckdir, exist_ok=True)
    logp = f'{WS}/../results/compute_log.csv'
    ic = pd.read_csv(f'{WS}/../results/input_conventions.csv')
    for CC in ccs:
        ckf = f'{ckdir}/{CC}_{Y}.csv'
        if os.path.exists(ckf):
            print(f"[{CC}] ssc_inv exists", flush=True); continue
        cells = fi.cells_1998(fi.EM2WB[CC])
        sig_AW = float(ic[ic.cc == CC]['sicer_ratio_med_2025'].iloc[0])
        # per-cell sigma from headline 2025 checkpoint
        hl = pd.read_csv(f'{WS}/checkpoints/headline/{CC}_{Y}.csv')
        r2 = cells['r'].copy()
        for _, row in hl.iterrows():
            g, d = int(row['g']), int(row['d'])
            sc = row.get('sicer_ratio', np.nan)
            if np.isfinite(sc) and np.isfinite(r2[g-1, d-1]):
                r2[g-1, d-1] = r2[g-1, d-1] * (1 + sig_AW) / (1 + sc)
        cells_i = dict(cells); cells_i['r'] = r2
        dest = f'/tmp/em_{CC}'
        root = subprocess.check_output(['bash', f'{WS}/extract_country.sh', CC, ZIP, dest]).decode().strip().splitlines()[-1]
        cy = he.CY(CC, root); cy.earnvar = ic[ic.cc == CC]['earnvar'].iloc[0]
        aw = fi.aw_month(CC, Y)
        t = time.time()
        cr = cy.cell_rates(Y, cells_i, aw)
        dt = time.time() - t
        cr['aw_month'] = aw; cr['aw_flag'] = f'ssc_inv_sigAW={sig_AW:.3f}'
        cr.to_csv(ckf, index=False)
        subprocess.run(['rm', '-rf', dest])
        with open(logp, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['variant', 'cc', 'year', 'seconds', 'n_cells', 'aw_flag'])
            w.writerow(dict(variant='ssc_inv', cc=CC, year=Y, seconds=round(dt, 2),
                            n_cells=len(cr), aw_flag=f'sigAW={sig_AW:.3f}'))
        print(f"[{CC}] ssc_inv {dt:.1f}s sigAW={sig_AW:.3f} {len(cr)} cells", flush=True)
    print("ssc_inv DONE")


if __name__ == '__main__':
    main()
