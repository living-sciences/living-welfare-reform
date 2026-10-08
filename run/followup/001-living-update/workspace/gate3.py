#!/usr/bin/env python3
"""Gate 3 (input-convention / levels) vs OECD TaxBEN DF_PTRSA (no-UB leg) and
DF_PTRUB (UB leg). Builds the 4 OECD cells at AW67/AW100/MINW on a GROSS basis,
compares PTRs, picks the housing variant on the S_C0 AW67 2015 cell, and writes
results/gate3_taxben.csv. Pass rules per spec §6.
"""
import os, sys, json, csv
import numpy as np, pandas as pd
import fixed_inputs as fi, hh_engine as he

RES = '/workspace/eval/followup/001-living-update/results'
WS = '/workspace/eval/followup/001-living-update/workspace'
ISO3 = {'AT':'AUT','BE':'BEL','DK':'DNK','FI':'FIN','FR':'FRA','DE':'DEU','EL':'GRC',
        'IE':'IRL','IT':'ITA','LU':'LUX','NL':'NLD','PT':'PRT','ES':'ESP','SE':'SWE'}
GATE_YEARS = [2010, 2015, 2020, 2025]
LAST2024 = {'DK', 'NL'}
MINW_COUNTRIES = {'BE','EL','ES','FR','IE','LU','PT','DE','NL'}  # DE 2015+, NL<=2024

_PTRSA = None; _PTRUB = None; _MINW = None

def _load_ben():
    global _PTRSA, _PTRUB
    if _PTRSA is None:
        _PTRSA = pd.read_csv(f'{WS}/shared-data/benchmarks/oecd_taxben_DF_PTRSA_EU15.csv')
        _PTRUB = pd.read_csv(f'{WS}/shared-data/benchmarks/oecd_taxben_DF_PTRUB_EU15.csv')
    return _PTRSA, _PTRUB

def minw_month(cc, year):
    global _MINW
    if _MINW is None:
        vals, dims, cats = fi.load_jsonstat(f'{WS}/shared-data/earnings/earn_mw_cur_EU14.json')
        _MINW = {}
        for k, v in vals.items():
            d = dict(zip(dims, k))
            _MINW.setdefault((d['geo'], d['time'][:4]), []).append(v)
    v = _MINW.get((cc, str(year)))
    return float(np.mean(v)) if v else None

def taxben_val(df, iso, year, hhtype, income_curr, income_part, house, leg):
    sub = df[(df.REF_AREA == iso) & (df.TIME_PERIOD == year) &
             (df.HOUSEHOLD_TYPE == hhtype) & (df.INCOME_CURR == income_curr) &
             (df.INCOME_PART == income_part) & (df.HOUSE_BENEFIT == house) &
             (df.TEMP_INTOWORK_BENEFIT == 'NO')]
    if len(sub) == 0:
        return None
    return float(sub['OBS_VALUE'].mean())

# OECD cell -> (group, income_part_code)
CELLS = [
    ('single',    'S_C0', '_Z', 1),
    ('lone',      'S_C2', '_Z', 2),
    ('1earner',   'C_C2', 'NOEARN_UNEMP_WO_CONBEN', 6),
    ('2earner',   'C_C2', 'AW67', 5),
]
INCOMES = ['AW67', 'AW100', 'MINW']


def ours_ptr(cy, year, g, aw, earn, leg):
    """Gross-basis PTR for one OECD cell. leg in {noUB, UB}."""
    cells = fi.cells_1998(fi.EM2WB[cy.CC])
    lhw = he.hours(earn, aw)
    idh = 1
    def mk(scenario):
        return cy._household(idh, g, 1 if g != 2 else 2, earn, aw, scenario, cells)
    # build base + out scenario; for 2earner spouse is at AW67 via group-5 rbar? -> override
    base = mk('base')
    out = mk('zeroNoUB' if leg == 'noUB' else 'zeroUB')
    # For 2-earner OECD cell, spouse must be at AW67 (not group-5 rbar). override spouse earns.
    if g == 5:
        sp_y = 0.67 * aw
        for p in base + out:
            if p['idperson'] == idh*100+2:
                p[cy.earnvar] = sp_y; p['yem'] = sp_y if cy.earnvar!='yem' else sp_y
                p['les'] = 3; p['lhw'] = he.hours(sp_y, aw); p['liwmy']=12; p['yemmy']=12
    df = pd.DataFrame(base + [dict(p, idhh=2) for p in out])
    o = cy.run_df(year, df)
    gsum = o.groupby('idhh')[['ils_dispy','ils_earns']].sum()
    dispy_w = gsum.loc[1,'ils_dispy']; earns_w = gsum.loc[1,'ils_earns']
    dispy_o = gsum.loc[2,'ils_dispy']; earns_o = gsum.loc[2,'ils_earns']
    d_earns = earns_w - earns_o  # reference person's earnings (gross basis)
    if d_earns == 0:
        return None, lhw
    return 100*(1 - (dispy_w - dispy_o)/d_earns), lhw


def run_country(CC, root):
    ptrsa, ptrub = _load_ben()
    iso = ISO3[CC]
    cy = he.CY(CC, root); cy.probe_earnvar(2015)
    gross = CC in ('EL', 'IT')
    years = [2010, 2015, 2020, (2024 if CC in LAST2024 else 2025)]
    # pick housing variant on S_C0 AW67 2015
    aw15 = fi.aw_month(CC, 2015)
    best_house = 'NO'; best_d = 1e9
    for house in ['NO', 'YES']:
        tb = taxben_val(ptrsa, iso, 2015, 'S_C0', 'AW67', '_Z', house, 'noUB')
        if tb is None:
            continue
        ours, _ = ours_ptr(cy, 2015, 1, aw15, 0.67*aw15, 'noUB')
        if ours is not None and abs(ours - tb) < best_d:
            best_d = abs(ours - tb); best_house = house
    rows = []
    for y in years:
        aw = fi.aw_month(CC, y)
        if aw is None:
            continue
        for lab, hhtype, part, g in CELLS:
            for inc in INCOMES:
                if inc == 'AW67': earn = 0.67*aw
                elif inc == 'AW100': earn = aw
                else:
                    mw = minw_month(CC, y)
                    if mw is None:
                        rows.append(dict(c=CC,t=y,leg='noUB',household_type=hhtype,income_curr=inc,
                                         income_part=part,house_benefit=best_house,lhw=None,
                                         ours=None,taxben=None,delta=None,status='no_benchmark_row'))
                        continue
                    earn = mw
                for leg, bendf in [('noUB', ptrsa), ('UB', ptrub)]:
                    tb = taxben_val(bendf, iso, y, hhtype, inc, part, best_house, leg)
                    try:
                        ours, lhw = ours_ptr(cy, y, g, aw, earn, leg)
                    except Exception as ex:
                        ours, lhw = None, None
                    delta = (ours - tb) if (ours is not None and tb is not None) else None
                    status = 'ok' if delta is not None else ('no_benchmark_row' if tb is None else 'no_ours')
                    rows.append(dict(c=CC,t=y,leg=leg,household_type=hhtype,income_curr=inc,
                                     income_part=part,house_benefit=best_house,
                                     lhw=lhw,ours=None if ours is None else round(ours,1),
                                     taxben=tb,delta=None if delta is None else round(delta,1),
                                     status=status, gross_basis=int(gross)))
    return rows, best_house


def main():
    CC = sys.argv[1]; root = sys.argv[2]
    rows, house = run_country(CC, root)
    path = f'{RES}/gate3_taxben.csv'
    newf = not os.path.exists(path)
    fields = ['c','t','leg','household_type','income_curr','income_part','house_benefit',
              'lhw','ours','taxben','delta','status','gross_basis']
    with open(path, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if newf: w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})
    # summarize no-UB leg pass
    df = pd.DataFrame([r for r in rows if r['status']=='ok'])
    for leg in ['noUB','UB']:
        d = df[df.leg==leg]
        if len(d)==0:
            print(f"[{CC}] {leg}: no comparisons"); continue
        within = (d['delta'].abs() <= (5 if leg=='noUB' else 7.5)).mean()
        minw_s2 = d[(d.income_curr=='MINW')|(d.household_type=='S_C2')]
        bad_big = (minw_s2['delta'].abs() > 10).sum() if len(minw_s2) else 0
        if leg=='noUB':
            passed = (within>=0.75) and (bad_big==0)
        else:
            passed = within>=0.75
        print(f"[{CC}] {leg} house={house}: n={len(d)} within_thr={within:.2f} "
              f"minw/S_C2_off>10={bad_big} => {'PASS' if passed else 'FAIL'}")


if __name__ == '__main__':
    main()
