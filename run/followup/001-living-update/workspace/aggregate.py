#!/usr/bin/env python3
"""Aggregate headline (and variant) checkpoints into the deliverable result CSVs.

Produces (under ../results/):
  rates_cells.csv, rates_deciles.csv, welfare_by_year.csv,
  critical_eta_by_year.csv, headline_scalars.json

Headline q-regime: V4 (q=0) is the headline iff >=4 countries fall back to q=0
(no UB triggered / UB-leg failure). Mixed-q reported as secondary.
Psi (E2/E4) carries a stability flag: Psi computed at clip caps 0.999 and 0.99;
'unstable' if sign flips, either is nan, or relative difference > 0.30.
"""
import os, json, glob
import numpy as np, pandas as pd
import fixed_inputs as fi
import welfare_layer as wl

RES = '/workspace/eval/followup/001-living-update/results'
GROSS_BASIS = {'EL', 'IT'}          # employer SSC not produced -> gross basis (flagged)
SICER_DK_OK = {'DK'}                # near-zero employer SSC accepted
YEARS = list(range(2009, 2027))


def ub_triggers(CC):
    """True if country triggers UB meaningfully in any headline year (mean gap>0.005)."""
    gaps = []
    for y in YEARS:
        cr = wl.load_cells(CC, y)
        if cr is None:
            continue
        gaps.append((cr['a_UB'] - cr['a_noUB']).mean())
    return (np.nanmean(gaps) if gaps else 0) > 0.005


def psi_stability(CC, y, variant='headline', q_override=None):
    r1 = wl.welfare(CC, y, variant, q_override=q_override, cap=0.999)
    r2 = wl.welfare(CC, y, variant, q_override=q_override, cap=0.99)
    if r1 is None:
        return None
    out = {}
    for key, nm in [('tradeoff_demogrant', 'Psi_d'), ('tradeoff_workingpoor', 'Psi_w')]:
        v1, v2 = r1[key], r2[key]
        if not np.isfinite(v1) or not np.isfinite(v2):
            stab = 'undefined'
        elif (v1 > 0) != (v2 > 0):
            stab = 'unstable'
        elif abs(v1) > 1e-9 and abs(v1 - v2) / abs(v1) > 0.30:
            stab = 'unstable'
        else:
            stab = 'stable'
        out[nm] = v1
        out[nm + '_stab'] = stab
    out['eff_demogrant'] = r1['eff_demogrant']
    out['eff_workingpoor'] = r1['eff_workingpoor']
    out['Dd'] = r1['Dd']; out['Dw'] = r1['Dw']
    out['meta'] = r1['meta']
    out['wp_has_gainers'] = r1['workingpoor_has_gainers']
    out['dg_has_gainers'] = r1['demogrant_has_gainers']
    return out


def main():
    os.makedirs(RES, exist_ok=True)
    qflags = {CC: (not ub_triggers(CC)) for CC in fi.EM_COUNTRIES}  # True -> q=0 fallback
    n_fallback = sum(qflags.values())
    v4_headline = n_fallback >= 4
    regime = 'V4' if v4_headline else 'mixed-q'
    print(f"q=0 fallbacks: {n_fallback} ({[c for c in qflags if qflags[c]]}); headline regime={regime}")

    # ---- rates_cells.csv ----
    cell_rows = []
    for CC in fi.EM_COUNTRIES:
        gb = CC in GROSS_BASIS
        for y in YEARS:
            cr = wl.load_cells(CC, y)
            if cr is None:
                continue
            q = 0.0 if (v4_headline or qflags[CC]) else fi.Q_TABLE_A3[CC] / 100.0
            ctr_pct, ctr_flag = fi.ctr_t(CC, y)
            ctr = (ctr_pct or 0) / 100.0
            for _, r0 in cr.iterrows():
                a_ub = r0['a_UB'] if np.isfinite(r0['a_UB']) else r0['a_noUB']
                a_comb = (q * a_ub + (1 - q) * r0['a_noUB']) if q > 0 else r0['a_noUB']
                a_adj = (a_comb + ctr) / (1 + ctr)
                flags = []
                if gb:
                    flags.append('gross_basis')
                if CC in SICER_DK_OK:
                    flags.append('dk_sicer_exception')
                if ctr_flag:
                    flags.append(ctr_flag)
                if a_adj > 1.0 or a_adj < -0.5:
                    flags.append('a_out_of_range')
                cell_rows.append(dict(c=CC, t=y, g=int(r0['g']), d=int(r0['d']),
                                      tau=round(r0['tau'], 5), a_noUB=round(r0['a_noUB'], 5),
                                      a_UB=round(r0['a_UB'], 5), a=round(a_adj, 5),
                                      sicer_ratio=round(r0['sicer_ratio'], 4),
                                      flags=';'.join(flags)))
    pd.DataFrame(cell_rows).to_csv(f'{RES}/rates_cells.csv', index=False)
    print(f"wrote rates_cells.csv ({len(cell_rows)} rows)")

    # ---- rates_deciles.csv (E1) ----
    dec_rows = []
    for CC in fi.EM_COUNTRIES:
        q = None if not (v4_headline or qflags[CC]) else 0.0
        for y in YEARS:
            dp = wl.decile_profile(CC, y, q_override=q, cap=np.inf)  # raw rates for profile
            if dp is None:
                continue
            for d in range(10):
                dec_rows.append(dict(c=CC, t=y, d=d + 1,
                                     marginal_tax_rate=round(100 * dp['tau_d'][d], 2),
                                     participation_tax_rate=round(100 * dp['a_d'][d], 2)))
    pd.DataFrame(dec_rows).to_csv(f'{RES}/rates_deciles.csv', index=False)
    print(f"wrote rates_deciles.csv ({len(dec_rows)} rows)")

    # ---- welfare_by_year.csv (E2) + bottom-quintile PTR ----
    wrows = []
    for CC in fi.EM_COUNTRIES:
        gb = 'gross_basis' if CC in GROSS_BASIS else ''
        for y in YEARS:
            dp_hl = wl.decile_profile(CC, y, q_override=(0.0 if (v4_headline or qflags[CC]) else None), cap=np.inf)
            if dp_hl is None:
                continue
            # headline regime
            qov = 0.0 if (v4_headline or qflags[CC]) else None
            st = psi_stability(CC, y, q_override=qov)
            # also V4 explicitly and mixed-q explicitly
            st_v4 = psi_stability(CC, y, q_override=0.0)
            m = st['meta']
            wrows.append(dict(
                c=CC, t=y, regime=regime,
                Psi_d=round(st['Psi_d'], 4) if np.isfinite(st['Psi_d']) else None,
                Psi_d_stab=st['Psi_d_stab'],
                Psi_w=round(st['Psi_w'], 4) if np.isfinite(st['Psi_w']) else None,
                Psi_w_stab=st['Psi_w_stab'],
                eff_d=round(st['eff_demogrant'], 4), eff_w=round(st['eff_workingpoor'], 4),
                Psi_w_V4=round(st_v4['Psi_w'], 4) if np.isfinite(st_v4['Psi_w']) else None,
                Psi_w_V4_stab=st_v4['Psi_w_stab'],
                a_bottom_quintile=round(100 * dp_hl['a_bottom_quintile'], 2),
                q=m['q'], ctr=round(m['ctr'], 4),
                n_cells=m['n_cells'], n_hi_a=m['n_hi_a'], n_hi_tau=m['n_hi_tau'],
                n_oor_a=m['n_oor_a'], q0_fallback=int(qflags[CC]),
                flags=';'.join([x for x in [gb, m['ctr_flag']] if x])))
    pd.DataFrame(wrows).to_csv(f'{RES}/welfare_by_year.csv', index=False)
    print(f"wrote welfare_by_year.csv ({len(wrows)} rows)")

    # ---- critical_eta_by_year.csv (E4) ----
    crows = []
    for CC in fi.EM_COUNTRIES:
        qov = 0.0 if (v4_headline or qflags[CC]) else None
        for y in YEARS:
            ce = wl.critical_eta(CC, y, q_override=qov, cap=0.999)
            if ce is None:
                continue
            crows.append(dict(c=CC, t=y, **{k: (round(v, 4) if v is not None else None)
                                            for k, v in ce.items()}))
    pd.DataFrame(crows).to_csv(f'{RES}/critical_eta_by_year.csv', index=False)
    print(f"wrote critical_eta_by_year.csv ({len(crows)} rows)")

    # ---- headline_scalars.json (E3, E5) ----
    scal = dict(regime=regime, n_q0_fallback=n_fallback,
                q0_countries=[c for c in qflags if qflags[c]],
                validated_set=fi.EM_COUNTRIES, n_countries=len(fi.EM_COUNTRIES),
                gross_basis=sorted(GROSS_BASIS))
    # E5: bottom-quintile PTR change 2009->2026, Psi_w/Psi_d change, ranked
    e5 = []
    w = pd.read_csv(f'{RES}/welfare_by_year.csv')
    for CC in fi.EM_COUNTRIES:
        a09 = w[(w.c == CC) & (w.t == 2009)]['a_bottom_quintile']
        a26 = w[(w.c == CC) & (w.t == 2026)]['a_bottom_quintile']
        if len(a09) and len(a26):
            e5.append(dict(c=CC, a12_2009=float(a09.iloc[0]), a12_2026=float(a26.iloc[0]),
                           d_a12=round(float(a26.iloc[0] - a09.iloc[0]), 2)))
    e5 = sorted(e5, key=lambda r: r['d_a12'])
    scal['E5_bottom_quintile_PTR_change'] = e5
    scal['E5_median_d_a12_allcountries'] = round(float(np.median([r['d_a12'] for r in e5])), 2)

    # ---- fold in gate 3 (level, no-UB) and gate 3b (change) validation sets ----
    V = V_delta = []
    try:
        g3 = pd.read_csv(f'{RES}/gate3_taxben.csv')
        V = []
        for CC in fi.EM_COUNTRIES:
            d = g3[(g3.c == CC) & (g3.leg == 'noUB') & (g3.status == 'ok')]
            if len(d) == 0:
                continue
            within = (d['delta'].abs() <= 5).mean()
            bad = d[(d.income_curr == 'MINW') | (d.household_type == 'S_C2')]
            bad_big = (bad['delta'].abs() > 10).sum() if len(bad) else 0
            if within >= 0.75 and bad_big == 0:
                V.append(CC)
    except Exception as ex:
        print("gate3 read err", ex)
    try:
        g3b = pd.read_csv(f'{RES}/gate3b_change.csv')
        V_delta = []
        for CC in fi.EM_COUNTRIES:
            d = g3b[(g3b.c == CC) & (g3b.status == 'ok')]
            if len(d) and d['passed'].all():
                V_delta.append(CC)
    except Exception as ex:
        print("gate3b read err", ex)
    scal['V_level_validated_noUB'] = V
    scal['V_delta_change_validated'] = V_delta
    e5_vd = [r for r in e5 if r['c'] in V_delta]
    scal['E5_median_d_a12_over_Vdelta'] = (round(float(np.median([r['d_a12'] for r in e5_vd])), 2)
                                           if e5_vd else None)
    scal['E5_over_Vdelta'] = e5_vd
    # E3: count Psi_w<Psi_d, Psi_w<1, Pareto in 2026 over STABLE countries
    def counts(year):
        nw_lt_d = nw_lt_1 = npareto = n_stable = 0
        stable_ccs = []
        for CC in fi.EM_COUNTRIES:
            row = w[(w.c == CC) & (w.t == year)]
            if not len(row):
                continue
            row = row.iloc[0]
            if row['Psi_w_stab'] != 'stable' or row['Psi_d_stab'] != 'stable':
                continue
            n_stable += 1; stable_ccs.append(CC)
            pw, pd_ = row['Psi_w'], row['Psi_d']
            if pd.notna(pw) and pd.notna(pd_) and pw < pd_:
                nw_lt_d += 1
            if pd.notna(pw) and pw < 1:
                nw_lt_1 += 1
            if row['eff_w'] > 0:
                npareto += 1
        return dict(year=year, n_stable=n_stable, stable_ccs=stable_ccs,
                    Psi_w_lt_Psi_d=nw_lt_d, Psi_w_lt_1=nw_lt_1, pareto=npareto)
    scal['E3_2026'] = counts(2026)
    scal['E3_2009'] = counts(2009)
    with open(f'{RES}/headline_scalars.json', 'w') as f:
        json.dump(scal, f, indent=2, default=str)
    print("wrote headline_scalars.json")
    print(json.dumps({k: scal[k] for k in ['regime', 'n_q0_fallback', 'E5_median_d_a12_over_Vdelta', 'E3_2026']},
                     indent=2, default=str))


if __name__ == '__main__':
    main()
