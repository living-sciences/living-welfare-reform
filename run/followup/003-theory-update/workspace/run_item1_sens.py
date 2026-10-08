"""Item 1 pre-declared robustness rows:
 (a) between-occupation implicit MTR sensitivity: tau_i = (T_i-T_{i-1})/(w_i-w_{i-1}),
     with T_i-T_0 = w_i a_i (c_i-c_0 = w_i(1-a_i)); vs the within-cell MTR headline.
 (b) extensive-only g at the 100-cell level: g_{g,d} = 1 - eta_d a_{g,d}/(1-a_{g,d})
     (eps=0, no adjacent-occupation differencing); share of employment with g<0.
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, '/workspace/eval/followup/002-living-update-cont/workspace')
os.environ.setdefault('SHARED', '/workspace/eval/followup_staging/shared-data')
import saez_inverse as si
import welfare_core as wc, fixed_inputs as fi, welfare_layer as wl

RES = '/workspace/eval/followup/003-theory-update/results'
CAP = 0.999
ETA, EPS = si.ETA, si.EPS


def invert_g_between(inp):
    """g with between-occupation implicit MTR in the intensive (B) term."""
    w, P, e_d, a = inp['w'], inp['P'], inp['e_d'], inp['a']
    h = P * e_d; h0 = 1 - P
    valid = (e_d > 0) & np.isfinite(w) & np.isfinite(a)
    wfull = np.concatenate([[0.0], w]); gaps = np.diff(wfull)
    T = w * a                                   # T_i - T_0
    Tfull = np.concatenate([[0.0], T])
    tau_b = np.where(gaps > 0, np.diff(Tfull) / gaps, np.nan)   # between-occupation MTR
    tau_b = np.clip(tau_b, -0.5, CAP)
    B = np.zeros(11)
    for i in range(1, 11):
        j = i - 1
        if valid[j] and gaps[j] > 0 and (1 - tau_b[j]) != 0 and np.isfinite(tau_b[j]):
            B[i] = EPS * (tau_b[j] / (1 - tau_b[j])) * w[j] * h[j] / gaps[j]
    g = np.full(10, np.nan)
    for i in range(1, 11):
        j = i - 1
        if not valid[j]:
            continue
        Bnext = B[i + 1] if i + 1 <= 10 else 0.0
        g[j] = 1 - ETA[j] * a[j] / (1 - a[j]) - (B[i] - Bnext) / h[j]
    return g, tau_b


def cell_g_extensive(CC, year):
    """Extensive-only g at 100-cell level; share of employment with g<0."""
    cells = fi.cells_1998(fi.EM2WB[CC]); e = cells['e']
    if year == 1998:
        d = wc.load_country(fi.EM2WB[CC]); a = np.clip(d['a'], -0.5, CAP)
    else:
        tau, a, meta = wl.build_tau_a(CC, year, q_override=0.0, cap=CAP)
        if tau is None:
            return None
    eta = np.tile(ETA, (10, 1))
    with np.errstate(divide='ignore', invalid='ignore'):
        g = 1 - eta * a / (1 - a)
    m = (e > 0) & np.isfinite(g)
    neg = m & (g < 0)
    return float(e[neg].sum() / e[m].sum()) if e[m].sum() > 0 else np.nan


rows = []
for CC in si.EM_COUNTRIES:
    for era, yr in [('1998', 1998), ('2026', 2026)]:
        inp = si.decile_inputs_1998(CC) if era == '1998' else si.decile_inputs_year(CC, yr)
        if inp is None:
            continue
        g_head = si.invert_g(inp)['g']
        g_bet, tau_b = invert_g_between(inp)
        cellshare = cell_g_extensive(CC, yr)
        d1_head = g_head[0]; d1_bet = g_bet[0]
        rows.append(dict(c=CC, era=era,
                         g1_within=round(float(d1_head), 4) if np.isfinite(d1_head) else None,
                         g1_between=round(float(d1_bet), 4) if np.isfinite(d1_bet) else None,
                         emp_share_gneg_decile_within=round(si.emp_share_g_neg(inp, g_head), 4),
                         emp_share_gneg_decile_between=round(si.emp_share_g_neg(inp, g_bet), 4),
                         emp_share_gneg_cell_extonly=round(cellshare, 4) if cellshare == cellshare else None))
df = pd.DataFrame(rows)
df.to_csv(f'{RES}/item1_sensitivity.csv', index=False)
print(df.to_string(index=False))
# correlation between within and between decile-1 g
d = df.dropna(subset=['g1_within', 'g1_between'])
print("\ncorr(g1_within, g1_between) =", round(float(np.corrcoef(d.g1_within, d.g1_between)[0, 1]), 3))
print("mean |within-between| decile-1 g =", round(float((d.g1_within - d.g1_between).abs().mean()), 3))
print("wrote item1_sensitivity.csv")
