"""Aggregation + formula layer for the living-update follow-up.

Reads per-country-year cell checkpoints (g,d,tau,a_noUB,a_UB,sicer_ratio) produced by
run_headline.py, builds 10x10 tau and a arrays (consumption-adjusted, q-combined),
feeds the 1998-fixed s_j,e_j,P into the replication's welfare_core.compute, and returns
Psi_d, Psi_w, efficiencies, Pareto/No-Gainers flags, decile profiles, and Table-3
critical average elasticities.
"""
import os, glob
import numpy as np, pandas as pd
import fixed_inputs as fi
import welfare_core as wc
from scipy.optimize import brentq

WS = '/workspace/eval/followup/001-living-update/workspace'
CKROOT = f'{WS}/checkpoints'


def load_cells(CC, year, variant='headline'):
    f = f'{CKROOT}/{variant}/{CC}_{year}.csv'
    if not os.path.exists(f):
        return None
    return pd.read_csv(f)


def build_tau_a(CC, year, variant='headline', q_override=None, ctr_fixed_1998=False,
                cap=0.999, clip_lo=-0.5):
    """Return (tau10x10, a10x10, meta) consumption-adjusted and q-combined.
    q_override: None -> use Q_TABLE_A3; else a fraction (e.g. 0.0 for V4).
    cap: rates clipped to [clip_lo, cap]. The closed-form welfare expressions divide
    by (1-rate), so a rate of exactly 1 is undefined; the minimal headline clip 0.999
    only removes that knife-edge. cap=0.95 is the pre-declared gate-5 sensitivity.
    All cells whose RAW rate left [clip_lo, 1.0] are counted in meta for gate 5."""
    cr = load_cells(CC, year, variant)
    if cr is None:
        return None, None, {'missing': True}
    cells = fi.cells_1998(fi.EM2WB[CC])
    e = cells['e']
    q = (fi.Q_TABLE_A3[CC] / 100.0) if q_override is None else q_override
    if ctr_fixed_1998:
        ctr = fi.CTR_1998_XLS[CC] / 100.0; ctr_flag = 'ctr_fixed1998'
    else:
        ctr_pct, ctr_flag = fi.ctr_t(CC, year)
        ctr = (ctr_pct / 100.0) if ctr_pct is not None else 0.0
    tau = np.zeros((10, 10)); a = np.zeros((10, 10))
    missing = []; n_oor_tau = 0; n_oor_a = 0; n_hi_tau = 0; n_hi_a = 0
    for g in range(1, 11):
        for d in range(1, 11):
            if not (e[g-1, d-1] > 0):
                continue
            row = cr[(cr.g == g) & (cr.d == d)]
            if len(row) == 0:
                missing.append((g, d)); continue
            r0 = row.iloc[0]
            a_ub = r0['a_UB'] if np.isfinite(r0['a_UB']) else r0['a_noUB']
            a_comb = (q * a_ub + (1 - q) * r0['a_noUB']) if q > 0 else r0['a_noUB']
            # consumption adjustment (TR + ctr)/(1+ctr)
            tv = (r0['tau'] + ctr) / (1 + ctr)
            av = (a_comb + ctr) / (1 + ctr)
            if tv > 1.0 or tv < clip_lo:
                n_oor_tau += 1
            if av > 1.0 or av < clip_lo:
                n_oor_a += 1
            if tv >= 0.99:
                n_hi_tau += 1
            if av >= 0.99:
                n_hi_a += 1
            tau[g-1, d-1] = min(max(tv, clip_lo), cap)
            a[g-1, d-1] = min(max(av, clip_lo), cap)
    meta = dict(missing=missing, q=q, ctr=ctr, ctr_flag=ctr_flag, cap=cap,
                n_oor_tau=n_oor_tau, n_oor_a=n_oor_a, n_hi_tau=n_hi_tau, n_hi_a=n_hi_a,
                n_cells=int((e > 0).sum()))
    return tau, a, meta


def welfare(CC, year, variant='headline', q_override=None, ctr_fixed_1998=False,
            eta=None, eps=None, cap=0.999):
    tau, a, meta = build_tau_a(CC, year, variant, q_override, ctr_fixed_1998, cap=cap)
    if tau is None:
        return None
    cells = fi.cells_1998(fi.EM2WB[CC])
    data = dict(cc=CC, P=cells['P'], sh=cells['s'], em=cells['e'], tau=tau, a=a)
    eta = wc.ETA_BENCHMARK if eta is None else eta
    eps = wc.EPS_BENCHMARK if eps is None else eps
    r = wc.compute(data, eta, eps)
    r.update(meta=meta)
    return r


def decile_profile(CC, year, variant='headline', q_override=None, ctr_fixed_1998=False, cap=0.999):
    """Employment-weighted (1998 e_j) decile profiles of tau and a (consumption-adj),
    plus bottom-quintile a. Returns dict."""
    tau, a, meta = build_tau_a(CC, year, variant, q_override, ctr_fixed_1998, cap=cap)
    if tau is None:
        return None
    cells = fi.cells_1998(fi.EM2WB[CC]); e = cells['e']
    tau_d = np.full(10, np.nan); a_d = np.full(10, np.nan)
    for d in range(10):
        w = e[:, d]
        if w.sum() > 0:
            tau_d[d] = np.sum(w * tau[:, d]) / w.sum()
            a_d[d] = np.sum(w * a[:, d]) / w.sum()
    # bottom-quintile a: employment-weighted over deciles 1-2
    w12 = e[:, :2]
    a12 = np.nansum(w12 * a[:, :2]) / w12.sum() if w12.sum() > 0 else np.nan
    return dict(tau_d=tau_d, a_d=a_d, a_bottom_quintile=a12, meta=meta)


# --------- Table-3 critical average eta per country-year ---------
def _bracket_root(f, lo=1e-6, hi=3.0, n=600):
    xs = np.linspace(lo, hi, n)
    prev_x, prev_f = xs[0], f(xs[0])
    for x in xs[1:]:
        fx = f(x)
        if np.isfinite(prev_f) and np.isfinite(fx) and prev_f * fx < 0:
            return brentq(f, prev_x, x, xtol=1e-10)
        prev_x, prev_f = x, fx
    return None


def critical_eta(CC, year, variant='headline', q_override=None, ctr_fixed_1998=False, cap=0.999):
    tau, a, meta = build_tau_a(CC, year, variant, q_override, ctr_fixed_1998, cap=cap)
    if tau is None:
        return None
    cells = fi.cells_1998(fi.EM2WB[CC])
    data = dict(cc=CC, P=cells['P'], sh=cells['s'], em=cells['e'], tau=tau, a=a)
    s, e = cells['s'], cells['e']
    maxse = (s / np.where(e > 0, e, np.inf)).max()

    def metrics(ea):
        return wc.compute(data, wc.eta_table3_profile(ea), wc.EPS_BENCHMARK)
    ci = _bracket_root(lambda ea: metrics(ea)['tradeoff_workingpoor'] - metrics(ea)['tradeoff_demogrant'])
    cz = _bracket_root(lambda ea: metrics(ea)['Dw'])
    cp = _bracket_root(lambda ea: (1 - metrics(ea)['Dw']) - maxse)
    return dict(crit_identical=ci, crit_zeroloss=cz, crit_pareto=cp)


if __name__ == '__main__':
    import sys
    CC = sys.argv[1] if len(sys.argv) > 1 else 'AT'
    print(f"=== {CC} headline welfare by year (mixed-q) ===")
    for y in range(2009, 2027):
        r = welfare(CC, y)
        if r is None:
            print(f"{y}: (no checkpoint)"); continue
        dp = decile_profile(CC, y)
        print(f"{y}: Psi_d={r['tradeoff_demogrant']:7.3f} Psi_w={r['tradeoff_workingpoor']:7.3f} "
              f"eff_d={r['eff_demogrant']:+.3f} eff_w={r['eff_workingpoor']:+.3f} "
              f"a12={100*dp['a_bottom_quintile']:.1f} ctr={r['meta']['ctr']:.3f} "
              f"Pareto_w={not r['workingpoor_has_gainers'] or r['eff_workingpoor']>0}")
