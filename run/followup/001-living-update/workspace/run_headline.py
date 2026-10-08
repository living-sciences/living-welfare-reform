#!/usr/bin/env python3
"""Run the headline EUROMOD cell rates for one country, all policy years 2009-2026.
Writes workspace/checkpoints/headline/<CC>_<YYYY>.csv (g,d,tau,a_noUB,a_UB,sicer_ratio).
Skips a year that already has a checkpoint. Foreground, one Model reused across years.

Usage: run_headline.py <EM_CC> [--variant headline|lhw40|V5|V6|V3] [--years 2009,...]
"""
import os, sys, time, argparse, csv
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he

WS = '/workspace/eval/followup/001-living-update/workspace'
ZIP = os.environ.get('J2_54',
    '/workspace/eval/followup_staging/shared-data/euromod/EUROMOD_RELEASES_J2.54+.zip')

ALL_YEARS = list(range(2009, 2027))
IE_SKIP = {('IE', 2021)}


def uprate_2026(cc, root, model):
    """AW_2026 = AW_2025 * 2026/2025 employment-income uprating factor from XML.
    Fallback: AW_2025, flag. Returns (aw2026, factor, flag)."""
    aw25 = fi.aw_month(cc, 2025)
    # Read the employment-income uprating index ($f_yem) 2026/2025 ratio from the XML.
    fac = None
    try:
        c = model.countries[cc]
        byname = {e.name: e for e in c.upratefactors}
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
                tag = '' if key == '$f_yem' else f'aw2026_upr_{key[3:]}'
                return aw25 * fac, fac, tag
    except Exception:
        pass
    return aw25, None, 'aw2026_no_uprating'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cc')
    ap.add_argument('--variant', default='headline')
    ap.add_argument('--years', default=None)
    ap.add_argument('--root', default=None)
    ap.add_argument('--zip', default=ZIP)
    args = ap.parse_args()
    CC = args.cc
    variant = args.variant
    years = [int(y) for y in args.years.split(',')] if args.years else ALL_YEARS

    ckdir = f'{WS}/checkpoints/{variant}'
    os.makedirs(ckdir, exist_ok=True)
    logpath = f'{WS}/../results/compute_log.csv'

    cells = fi.cells_1998(fi.EM2WB[CC])

    # extract country if needed
    root = args.root
    if not root:
        dest = f'/tmp/em_{CC}'
        ver = None
        import subprocess
        if not os.path.exists(dest):
            out = subprocess.check_output(['bash', f'{WS}/extract_country.sh', CC, args.zip, dest]).decode().strip()
            root = out.splitlines()[-1]
        else:
            # find version dir
            sub = [d for d in os.listdir(dest) if d.startswith('EUROMOD_RELEASES')]
            root = f'{dest}/{sub[0]}'
    print(f"[{CC}] root={root}", flush=True)

    cy = he.CY(CC, root)
    # earnings-variable probe (silent-failure guard §3.2)
    if variant == 'headline':
        pb = cy.probe_earnvar(2025 if 2025 in years else years[-1])
        icpath = f'{WS}/../results/input_conventions.csv'
        newic = not os.path.exists(icpath)
        with open(icpath, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['cc', 'earnvar', 'ils_earns_probe'])
            if newic:
                w.writeheader()
            w.writerow(dict(cc=CC, earnvar=pb[0] if pb else '?',
                            ils_earns_probe=round(pb[1], 2) if pb else None))
        print(f"[{CC}] earnvar probe -> {pb}", flush=True)
    opts = dict()
    if variant == 'lhw40':
        opts['lhw40'] = True
    elif variant == 'V5':
        pass  # rent handled below
    elif variant == 'V6':
        opts['one_child'] = True

    logrows = []
    for y in years:
        if (CC, y) in IE_SKIP:
            print(f"[{CC}] {y} SKIP (no hhot config)", flush=True)
            continue
        ckf = f'{ckdir}/{CC}_{y}.csv'
        if os.path.exists(ckf):
            print(f"[{CC}] {y} checkpoint exists, skip", flush=True)
            continue
        if y == 2026:
            aw, fac, flag = uprate_2026(CC, root, cy.m)
        else:
            aw = fi.aw_month(CC, y); flag = ''
            if aw is None:
                aw = fi.aw_month(CC, 2025); flag = 'aw_missing_cf'
        rent = 0.0
        if variant == 'V5':
            rent = 0.20 * aw
        t = time.time()
        try:
            cr = cy.cell_rates(y, cells, aw, rent=rent,
                               one_child=opts.get('one_child', False),
                               lhw40=opts.get('lhw40', False))
        except Exception as ex:
            print(f"[{CC}] {y} ERROR {repr(ex)[:200]}", flush=True)
            continue
        dt = time.time() - t
        cr['aw_month'] = aw
        cr['aw_flag'] = flag
        cr.to_csv(ckf, index=False)
        logrows.append(dict(variant=variant, cc=CC, year=y, seconds=round(dt, 2),
                            n_cells=len(cr), aw_flag=flag))
        print(f"[{CC}] {y} done {dt:.1f}s {len(cr)} cells aw={aw:.0f} {flag}", flush=True)

    # append compute log
    newfile = not os.path.exists(logpath)
    with open(logpath, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['variant', 'cc', 'year', 'seconds', 'n_cells', 'aw_flag'])
        if newfile:
            w.writeheader()
        w.writerows(logrows)
    print(f"[{CC}] variant={variant} complete ({len(logrows)} new years)", flush=True)


if __name__ == '__main__':
    main()
