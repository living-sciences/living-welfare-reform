#!/usr/bin/env python3
"""V3 (dispersion update): stretch the 1998 relative-earnings array r_{g,d} in
log space around the employment-weighted median decile position so that the
implied cross-decile P90/P10 equals the SES vintage nearest the policy year, then
re-run EUROMOD. Years {2009,2015,2020,2026}; SES covers 12 geos (no FI, SE).

Operationalization (documented, labelled):
  w_d = sum_g e_gd r_gd / sum_g e_gd       (1998 employment-weighted decile position)
  assign decile midpoint percentile p_d = 10d-5; interpolate log(w) in percentile
  to P10,P50,P90.  R_cur = exp(logw(P90)-logw(P10)).  R_tgt = SES P90/P10 (NAC,TOTAL).
  lambda = ln(R_tgt)/ln(R_cur);  r'_gd = m*(r_gd/m)^lambda,  m = exp(logw(P50)).
Welfare weights s,e,P stay 1998; only earnings placement (hence tau,a) moves.
Also writes results/v3_ses_p90p10.csv (the public Fig-3 analogue).
"""
import os, sys, time, csv, subprocess, json
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he

WS = '/workspace/eval/followup/002-living-update-cont/workspace'
ZIP = os.environ['J2_54']; SHARED = os.environ['SHARED']
YEARS = [2009, 2015, 2020, 2026]
VINTAGE = {2009: '10', 2015: '14', 2020: '18', 2026: '22'}  # nearest SES file suffix
FILES = {'10': 'earn_ses10_adeci.json', '14': 'earn_ses14_adeci.json',
         '18': 'earn_ses18_adeci.json', '22': 'earn_ses22_adeci.json'}


def ses_ratio(cc, suffix):
    """Return (P90/P10, P10, MED, P90) for a geo from a SES vintage. The P90/P10
    ratio is currency-invariant, so unit/worktime choices below don't affect it.
    Dim name is 'quant_inc' (2022) or 'quantile' (<=2018); unit NAC preferred else
    EUR; worktime TOTAL preferred else FT (older vintages carry FT only)."""
    vals, dims, cats = fi.load_jsonstat(f'{SHARED}/earnings/{FILES[suffix]}')
    qdim = 'quant_inc' if 'quant_inc' in dims else 'quantile'

    def pick(unit_pref, wt_pref):
        got = {}
        for k, v in vals.items():
            d = dict(zip(dims, k))
            if d['geo'] != cc:
                continue
            if unit_pref and d.get('unit') != unit_pref:
                continue
            if wt_pref and d.get('worktime') != wt_pref:
                continue
            got[d[qdim]] = v
        return got if all(q in got for q in ('P10', 'MED', 'P90')) else None

    for up, wp in [('NAC', 'TOTAL'), ('EUR', 'TOTAL'), ('NAC', 'FT'),
                   ('EUR', 'FT'), (None, 'FT'), (None, None)]:
        got = pick(up, wp)
        if got:
            return got['P90'] / got['P10'], got['P10'], got['MED'], got['P90']
    return None


def stretched_r(cells, R_tgt):
    """Stretch r around employment-weighted median decile position to hit R_tgt."""
    e = cells['e']; r = cells['r'].copy()
    w = np.full(10, np.nan)
    for d in range(10):
        wsum = e[:, d].sum()
        if wsum > 0:
            w[d] = np.nansum(e[:, d] * r[:, d]) / wsum
    p = np.array([10 * (d + 1) - 5 for d in range(10)], float)  # 5..95
    ok = np.isfinite(w) & (w > 0)
    logw = np.interp([10, 50, 90], p[ok], np.log(w[ok]))
    R_cur = np.exp(logw[2] - logw[0])
    m = np.exp(logw[1])
    lam = np.log(R_tgt) / np.log(R_cur)
    r2 = np.where(np.isfinite(r) & (r > 0), m * (r / m) ** lam, r)
    return r2, R_cur, lam, m


def main():
    ccs = sys.argv[1:] if len(sys.argv) > 1 else fi.EM_COUNTRIES
    ckdir = f'{WS}/checkpoints/V3'; os.makedirs(ckdir, exist_ok=True)
    logp = f'{WS}/../results/compute_log.csv'
    sesrows = []
    for CC in ccs:
        cells = fi.cells_1998(fi.EM2WB[CC])
        # check SES availability (use 2022 as presence probe)
        avail = ses_ratio(CC, '22')
        if avail is None:
            print(f"[{CC}] no SES data -> V3 skipped (flagged)", flush=True)
            sesrows.append(dict(c=CC, vintage='none', p90p10=None, note='no_SES_geo'))
            continue
        dest = f'/tmp/em_{CC}'
        root = subprocess.check_output(['bash', f'{WS}/extract_country.sh', CC, ZIP, dest]).decode().strip().splitlines()[-1]
        cy = he.CY(CC, root)
        ic = pd.read_csv(f'{WS}/../results/input_conventions.csv'); row = ic[ic.cc == CC]
        if len(row):
            cy.earnvar = row.iloc[0]['earnvar']
        logrows = []
        for y in YEARS:
            ckf = f'{ckdir}/{CC}_{y}.csv'
            if os.path.exists(ckf):
                print(f"[{CC}] V3 {y} exists", flush=True); continue
            suf = VINTAGE[y]; sr = ses_ratio(CC, suf)
            if sr is None:
                print(f"[{CC}] V3 {y} no SES vintage {suf}", flush=True); continue
            R_tgt = sr[0]
            r2, R_cur, lam, m = stretched_r(cells, R_tgt)
            cells_v3 = dict(cells); cells_v3['r'] = r2
            if y == 2026:
                aw25 = fi.aw_month(CC, 2025)
                try:
                    byname = {e.name: e for e in cy.m.countries[CC].upratefactors}
                    f = byname['$f_yem']; vals = {int(el.year): float(el.value) for el in f.values if el.value}
                    aw = aw25 * (vals[2026] / vals[2025]); flag = ''
                except Exception:
                    aw = aw25; flag = 'aw2026_no_uprating'
            else:
                aw = fi.aw_month(CC, y) or fi.aw_month(CC, 2025); flag = ''
            t = time.time()
            try:
                cr = cy.cell_rates(y, cells_v3, aw)
            except Exception as ex:
                print(f"[{CC}] V3 {y} ERROR {repr(ex)[:150]}", flush=True); continue
            dt = time.time() - t
            cr['aw_month'] = aw; cr['aw_flag'] = flag
            cr.to_csv(ckf, index=False)
            logrows.append(dict(variant='V3', cc=CC, year=y, seconds=round(dt, 2), n_cells=len(cr), aw_flag=flag))
            sesrows.append(dict(c=CC, vintage=suf, p90p10=round(R_tgt, 3),
                                note=f'R_cur={R_cur:.3f} lambda={lam:.3f} year={y}'))
            print(f"[{CC}] V3 {y} {dt:.1f}s R_tgt={R_tgt:.2f} R_cur={R_cur:.2f} lam={lam:.2f}", flush=True)
        subprocess.run(['rm', '-rf', dest])
        nf = not os.path.exists(logp)
        with open(logp, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['variant', 'cc', 'year', 'seconds', 'n_cells', 'aw_flag'])
            if nf:
                w.writeheader()
            w.writerows(logrows)
        print(f"=== {CC} V3 done ===", flush=True)
    pd.DataFrame(sesrows).to_csv(f'{WS}/../results/v3_ses_p90p10.csv', index=False)
    print("wrote v3_ses_p90p10.csv")


if __name__ == '__main__':
    main()
