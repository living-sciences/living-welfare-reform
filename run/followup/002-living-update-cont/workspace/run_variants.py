#!/usr/bin/env python3
"""Continuation: run the pre-declared variants that 001 cut (V5 rent=20%AW,
V6 one child, lhw40 hours sensitivity) at t in {2009,2015,2020,2026}, reusing
one EUROMOD Model per country across variants and years. Foreground, checkpointed.

Writes workspace/checkpoints/<variant>/<CC>_<YYYY>.csv (same schema as headline).
Skips any country-year that already has a checkpoint.
"""
import os, sys, time, csv, subprocess
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he

WS = '/workspace/eval/followup/002-living-update-cont/workspace'
ZIP = os.environ['J2_54']
YEARS = [2009, 2015, 2020, 2026]
IE_SKIP = {('IE', 2021)}
VARIANTS = os.environ.get('VARIANTS_ONLY', 'V5,V6,lhw40').split(',')  # headline done; V3/ssc_inv separate
LOGP = f'{WS}/../results/compute_log.csv'


def uprate_2026(cc, model):
    aw25 = fi.aw_month(cc, 2025)
    try:
        byname = {e.name: e for e in model.countries[cc].upratefactors}
        for key in ('$f_yem', '$f_yempv', '$f_cpi'):
            if key not in byname:
                continue
            vals = {}
            for el in byname[key].values:
                try:
                    vals[int(el.year)] = float(el.value)
                except Exception:
                    pass
            if 2025 in vals and 2026 in vals and vals[2025]:
                fac = vals[2026] / vals[2025]
                return aw25 * fac, ('' if key == '$f_yem' else f'aw2026_upr_{key[3:]}')
    except Exception:
        pass
    return aw25, 'aw2026_no_uprating'


def aw_for(cc, y, model):
    if y == 2026:
        return uprate_2026(cc, model)
    aw = fi.aw_month(cc, y)
    if aw is None:
        return fi.aw_month(cc, 2025), 'aw_missing_cf'
    return aw, ''


def run_country(CC):
    dest = f'/tmp/em_{CC}'
    out = subprocess.check_output(['bash', f'{WS}/extract_country.sh', CC, ZIP, dest]).decode().strip()
    root = out.splitlines()[-1]
    cy = he.CY(CC, root)
    # lock in the earnings variable mapping from the headline input_conventions
    ic = pd.read_csv(f'{WS}/../results/input_conventions.csv')
    row = ic[ic.cc == CC]
    if len(row) and str(row.iloc[0].get('earnvar', '')) not in ('', 'nan', '?'):
        cy.earnvar = row.iloc[0]['earnvar']
    else:
        cy.probe_earnvar(2025)
    cells = fi.cells_1998(fi.EM2WB[CC])
    logrows = []
    for variant in VARIANTS:
        ckdir = f'{WS}/checkpoints/{variant}'
        os.makedirs(ckdir, exist_ok=True)
        opts = dict(one_child=(variant == 'V6'), lhw40=(variant == 'lhw40'))
        for y in YEARS:
            if (CC, y) in IE_SKIP:
                print(f"[{CC}] {variant} {y} SKIP (no hhot)", flush=True); continue
            ckf = f'{ckdir}/{CC}_{y}.csv'
            if os.path.exists(ckf):
                print(f"[{CC}] {variant} {y} exists", flush=True); continue
            aw, flag = aw_for(CC, y, cy.m)
            rent = 0.20 * aw if variant == 'V5' else 0.0
            t = time.time()
            try:
                cr = cy.cell_rates(y, cells, aw, rent=rent,
                                   one_child=opts['one_child'], lhw40=opts['lhw40'])
            except Exception as ex:
                print(f"[{CC}] {variant} {y} ERROR {repr(ex)[:160]}", flush=True); continue
            dt = time.time() - t
            cr['aw_month'] = aw; cr['aw_flag'] = flag
            cr.to_csv(ckf, index=False)
            logrows.append(dict(variant=variant, cc=CC, year=y, seconds=round(dt, 2),
                                n_cells=len(cr), aw_flag=flag))
            print(f"[{CC}] {variant} {y} {dt:.1f}s {len(cr)} cells aw={aw:.0f} {flag}", flush=True)
    subprocess.run(['rm', '-rf', dest])
    # append compute log
    newfile = not os.path.exists(LOGP)
    with open(LOGP, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['variant', 'cc', 'year', 'seconds', 'n_cells', 'aw_flag'])
        if newfile:
            w.writeheader()
        w.writerows(logrows)
    return len(logrows)


if __name__ == '__main__':
    ccs = sys.argv[1:] if len(sys.argv) > 1 else fi.EM_COUNTRIES
    tot = 0
    for CC in ccs:
        n = run_country(CC)
        tot += n
        print(f"=== {CC} done ({n} new runs) ===", flush=True)
    print(f"ALL DONE {tot} new runs")
