#!/usr/bin/env python3
"""Gate 3c (MTR gate). Runs the MTR add-on for groups 1 (S_C0) and 6 (one-earner C_C2),
all deciles and grid points, in 2010 and 2025, reads mtrpc (gross MTR m_g) for the
reference person, derives the labour-cost MTR tau_addon = 1 - (1-m_g)/(1+sigma) with
sigma = d(sicer)/d(earns) from a +3% run of the same household, and compares with
tau_ours (same +3% run, labour-cost basis). Pass: median |tau_ours - tau_addon| <= 5pp.
Writes results/gate3c_mtr.csv.
"""
import os, sys, csv
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he

RES = '/workspace/eval/followup/004-gate-conformance/results'


def run_country(CC, root):
    cy = he.CY(CC, root); cy.probe_earnvar(2015)
    cells = fi.cells_1998(fi.EM2WB[CC])
    r = cells['r']; e = cells['e']
    rows = []
    for year in [2010, 2025]:
        aw = fi.aw_month(CC, year)
        if aw is None:
            continue
        # build base + plus3 households for groups 1 and 6, all deciles/grid
        base_rows = []; idx = {}; idh = 1
        for g in [1, 6]:
            for d in range(10):
                if not (e[g-1, d] > 0 and np.isfinite(r[g-1, d])):
                    continue
                for k in he.GRID:
                    y = r[g-1, d] * aw * k
                    for sc in ['base', 'plus3']:
                        hh = cy._household(idh, g, 1, y, aw, sc, cells)
                        base_rows += hh
                        idx[idh] = (g, d+1, k, sc)
                        idh += 1
        df = pd.DataFrame(base_rows)
        o = cy.run_df(year, df)
        gsum = o.groupby('idhh')[['ils_dispy', 'ils_earns', 'ils_sicer']].sum()
        # MTR add-on run on base households only (one per cell/grid) to read mtrpc
        mtr_rows = []; midx = {}; mi = 1
        for g in [1, 6]:
            for d in range(10):
                if not (e[g-1, d] > 0 and np.isfinite(r[g-1, d])):
                    continue
                for k in he.GRID:
                    y = r[g-1, d] * aw * k
                    hh = cy._household(mi, g, 1, y, aw, 'base', cells)
                    mtr_rows += hh; midx[mi] = (g, d+1, k); mi += 1
        mdf = pd.DataFrame(mtr_rows)
        try:
            with he._suppress():
                mo = cy.c.systems[f'{CC}_{year}'].run(mdf, f'{CC}_{year}_hhot',
                                                      addons=[('MTR', 'MTR')], verbose=False)
            # find the nrr/mtr output with mtrpc
            mout = None
            keys = mo.outputs.keys() if hasattr(mo.outputs, 'keys') else range(len(mo.outputs))
            for kk in keys:
                oo = mo.outputs[kk]
                if any(c.startswith('mtrpc') for c in oo.columns):
                    mout = oo; break
        except Exception as ex:
            print(f"[{CC}] {year} MTR add-on ERR {repr(ex)[:150]}")
            continue
        if mout is None:
            print(f"[{CC}] {year} no mtrpc output"); continue
        mcol = [c for c in mout.columns if c == 'mtrpc'] or [c for c in mout.columns if c.startswith('mtrpc')]
        mcol = mcol[0]
        # ref person = lowest idperson per hh (idhh*100+1)
        mout2 = mout[mout['idperson'] == mout['idhh']*100+1][['idhh', mcol]].set_index('idhh')
        # aggregate ours tau and sigma per cell (ratio of sums over grid)
        from collections import defaultdict
        acc = defaultdict(lambda: dict(dd=0.0, de=0.0, ds=0.0, mg=[], ))
        for idh, (g, d, k, sc) in idx.items():
            if idh not in gsum.index:
                continue
        # pair base/plus3
        cellsums = defaultdict(lambda: {})
        for idh, (g, d, k, sc) in idx.items():
            if idh in gsum.index:
                cellsums[(g, d, k)][sc] = gsum.loc[idh]
        perc = defaultdict(lambda: dict(dd=0.0, de=0.0, ds=0.0))
        for (g, d, k), scd in cellsums.items():
            if 'base' in scd and 'plus3' in scd:
                b, p = scd['base'], scd['plus3']
                perc[(g, d)]['dd'] += (p['ils_dispy'] - b['ils_dispy'])
                perc[(g, d)]['de'] += (p['ils_earns'] - b['ils_earns'])
                perc[(g, d)]['ds'] += (p['ils_sicer'] - b['ils_sicer'])
        # mtrpc per cell (mean over grid of ref mtrpc)
        mg_cell = defaultdict(list)
        for mi_, (g, d, k) in midx.items():
            if mi_ in mout2.index:
                mg_cell[(g, d)].append(float(mout2.loc[mi_, mcol]))
        for (g, d), A in perc.items():
            if A['de'] == 0:
                continue
            tau_ours = 1 - A['dd'] / (A['de'] + A['ds'])
            sigma = A['ds'] / A['de']
            mgs = mg_cell.get((g, d), [])
            if not mgs:
                continue
            m_g = np.mean(mgs) / 100.0
            tau_addon = 1 - (1 - m_g) / (1 + sigma)
            rows.append(dict(c=CC, t=year, g=g, d=d,
                             m_g=round(m_g, 4), sigma=round(sigma, 4),
                             tau_addon=round(tau_addon, 4), tau_ours=round(tau_ours, 4),
                             abs_diff_pp=round(100*abs(tau_ours - tau_addon), 2)))
    return rows


def main():
    CC = sys.argv[1]; root = sys.argv[2]
    rows = run_country(CC, root)
    path = f'{RES}/gate3c_FR_EL_completion.csv'
    newf = not os.path.exists(path)
    fields = ['c', 't', 'g', 'd', 'm_g', 'sigma', 'tau_addon', 'tau_ours', 'abs_diff_pp']
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if newf: w.writeheader()
        for r in rows: w.writerow(r)
    if rows:
        med = np.median([r['abs_diff_pp'] for r in rows])
        print(f"[{CC}] 3c: n={len(rows)} median|dtau|={med:.2f}pp => {'PASS' if med<=5 else 'FAIL (tau unvalidated)'}")
    else:
        print(f"[{CC}] 3c: no rows")


if __name__ == '__main__':
    main()
