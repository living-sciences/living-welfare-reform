"""Study B, item 1: inverse-optimum (Saez 2002) social marginal welfare weights g_d
by earnings decile, 1998 (workbook) and 2009-2026, for each country in 001's set V.

Saez (2002) QJE 117(3), eq. (16) of NBER WP 7708, mixed extensive+intensive model,
no income effects, normalisation sum_i h_i g_i = 1:

  tau_i/(1-tau_i) = 1/(eps_i w_i h(w_i)) * sum_{j>=i} h_j [1 - g_j - eta_j (T_j-T_0)/(c_j-c_0)]

with c_j-c_0 = w_j(1-a_j) so the last term is eta_j a_j/(1-a_j).

Inverted (differencing i and i+1), with B_i = eps [tau_i/(1-tau_i)] w_i h_i/(w_i-w_{i-1}),
B_{I+1}=0:
  g_i = 1 - eta_i a_i/(1-a_i) - (B_i - B_{i+1})/h_i,   i=1..I
  g_0 = [1 - sum_{i>=1} h_i g_i]/h_0.

Decile mapping (pre-declared): I=10 earnings deciles.
  w_d = s_d/e_d (decile sums of the 1998 workbook shares), w_0=0
  h_d = P e_d, h_0 = 1-P
  tau_d, a_d = employment-weighted decile rates (001's E1), consumption-adjusted,
               q=0 (V4 headline), capped at 0.999 exactly as welfare_core does.
  eta_d = benchmark [.4,.4,.3,.3,.2,.2,.1,.1,0,0], eps=0.1.
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, '/workspace/eval/followup/002-living-update-cont/workspace')
os.environ.setdefault('SHARED', '/workspace/eval/followup_staging/shared-data')
import welfare_core as wc
import fixed_inputs as fi
import welfare_layer as wl

ETA = wc.ETA_BENCHMARK.copy()          # [.4,.4,.3,.3,.2,.2,.1,.1,0,0]
EPS = wc.EPS_BENCHMARK                  # 0.1
CAP = 0.999
EM_COUNTRIES = fi.EM_COUNTRIES


def decile_inputs_1998(CC):
    """1998 workbook: decile w_d, h_d, P, tau_d, a_d (employment-weighted over groups)."""
    cells = fi.cells_1998(fi.EM2WB[CC])
    s, e, P = cells['s'], cells['e'], cells['P']
    d = wc.load_country(fi.EM2WB[CC])
    tau, a = d['tau'], d['a']
    s_d = s.sum(0); e_d = e.sum(0)
    w_d = np.where(e_d > 0, s_d / e_d, np.nan)
    tau_d = np.full(10, np.nan); a_d = np.full(10, np.nan)
    for j in range(10):
        wt = e[:, j]
        if wt.sum() > 0:
            tau_d[j] = np.sum(wt * tau[:, j]) / wt.sum()
            a_d[j] = np.sum(wt * a[:, j]) / wt.sum()
    tau_d = np.clip(tau_d, -0.5, CAP); a_d = np.clip(a_d, -0.5, CAP)
    return dict(w=w_d, P=P, e_d=e_d, s_d=s_d, tau=tau_d, a=a_d)


def decile_inputs_year(CC, year):
    """Policy-year decile rates from the welfare layer (q=0 V4, consumption-adj,
    capped 0.999 -- identical to how 001's Psi is computed). w_d,h_d from 1998 cells."""
    dp = wl.decile_profile(CC, year, q_override=0.0, cap=CAP)
    if dp is None:
        return None
    cells = fi.cells_1998(fi.EM2WB[CC])
    s, e, P = cells['s'], cells['e'], cells['P']
    s_d = s.sum(0); e_d = e.sum(0)
    w_d = np.where(e_d > 0, s_d / e_d, np.nan)
    return dict(w=w_d, P=P, e_d=e_d, s_d=s_d, tau=dp['tau_d'], a=dp['a_d'])


def invert_g(inp, eta=ETA, eps=EPS):
    """Return g_d (length 10), g_0, and diagnostics. inp from decile_inputs_*."""
    w, P, e_d, tau, a = inp['w'], inp['P'], inp['e_d'], inp['tau'], inp['a']
    h = P * e_d                       # h_d
    h0 = 1 - P
    valid = (e_d > 0) & np.isfinite(w) & np.isfinite(tau) & np.isfinite(a)
    # occupation earnings, with w_0 = 0; gaps w_i - w_{i-1}
    wfull = np.concatenate([[0.0], w])
    gaps = np.diff(wfull)             # length 10: w_i - w_{i-1}
    mono = np.all(gaps[valid] > 0)
    B = np.zeros(11)                  # B[1..10]; B[0] unused, B index i -> B[i]
    for i in range(1, 11):
        j = i - 1
        if valid[j] and gaps[j] > 0 and (1 - tau[j]) != 0:
            B[i] = eps * (tau[j] / (1 - tau[j])) * w[j] * h[j] / gaps[j]
        else:
            B[i] = 0.0
    g = np.full(10, np.nan)
    for i in range(1, 11):
        j = i - 1
        if not valid[j]:
            continue
        Bnext = B[i + 1] if i + 1 <= 10 else 0.0
        g[j] = 1 - eta[j] * a[j] / (1 - a[j]) - (B[i] - Bnext) / h[j]
    hg = np.nansum(h * np.where(np.isfinite(g), g, 0.0))
    g0 = (1 - hg) / h0 if h0 > 0 else np.nan
    return dict(g=g, g0=g0, h=h, h0=h0, w=w, mono=bool(mono), valid=valid)


def gw_deciles(CC, year=None):
    """Deciles containing >=1 working-poor net-gainer cell G_w={e>0, s/e<1-Dw},
    and Dw, from welfare_core.compute at the headline regime (q=0)."""
    cells = fi.cells_1998(fi.EM2WB[CC])
    s, e, P = cells['s'], cells['e'], cells['P']
    if year is None:
        d = wc.load_country(fi.EM2WB[CC]); tau, a = d['tau'], d['a']
        tau = np.clip(tau, -0.5, CAP); a = np.clip(a, -0.5, CAP)
    else:
        tau, a, meta = wl.build_tau_a(CC, year, q_override=0.0, cap=CAP)
        if tau is None:
            return None
    data = dict(cc=CC, P=P, sh=s, em=e, tau=tau, a=a)
    r = wc.compute(data, ETA, EPS)
    Dw = r['Dw']
    with np.errstate(divide='ignore', invalid='ignore'):
        se = np.where(e > 0, s / e, np.inf)
    gw = (e > 0) & (se < (1 - Dw))
    gw_dec = [d for d in range(10) if gw[:, d].any()]
    return dict(Dw=Dw, eff_w=r['eff_workingpoor'], Psi_w=r['tradeoff_workingpoor'],
                gw_deciles=gw_dec, gw_mask=gw)


def emp_share_g_neg(inp, g):
    """Share of EMPLOYMENT in deciles with g<0 (employment weights e_d; note sum e_d=1)."""
    e_d = inp['e_d']
    neg = np.isfinite(g) & (g < 0)
    return float(e_d[neg].sum() / e_d[np.isfinite(g)].sum()) if np.isfinite(g).any() else np.nan


if __name__ == '__main__':
    print("=== DK 1998 reproduction check ===")
    inp = decile_inputs_1998('DK')
    print("DK w_d (s/e):", np.round(inp['w'], 3))
    print("DK monotone increasing w?", np.all(np.diff(np.concatenate([[0], inp['w']])) > 0))
    print("DK tau_d:", np.round(inp['tau'], 3))
    print("DK a_d  :", np.round(inp['a'], 3))
    res = invert_g(inp)
    print("DK g_d  :", np.round(res['g'], 3))
    print("DK g_0  :", round(res['g0'], 3))
    gwd = gw_deciles('DK')
    print("DK Dw=%.4f eff_w=%.4f Psi_w=%.3g" % (gwd['Dw'], gwd['eff_w'], gwd['Psi_w']))
    print("DK G_w deciles (0-idx):", gwd['gw_deciles'])
    gneg = [d for d in range(10) if np.isfinite(res['g'][d]) and res['g'][d] < 0]
    print("DK deciles with g<0:", gneg)
    overlap = sorted(set(gwd['gw_deciles']) & set(gneg))
    print("DK G_w-deciles with g<0:", overlap, "-> PARETO-iff reproduced:", len(overlap) > 0)
    print("DK emp share in g<0 deciles:", round(emp_share_g_neg(inp, res['g']), 3))
