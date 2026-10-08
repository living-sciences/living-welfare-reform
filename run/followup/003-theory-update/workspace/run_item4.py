"""Item 4: linearisation accuracy check [CONSISTENCY CHECK] (NOT a validation).
Psi_w is a deterministic function of the rates; this only measures how well a linear
relation between d(bottom-quintile PTR) and d(Psi_w) fits.

Fit cross-country on 2009->2017 (one (d_a12, d_Psi_w) point per country, endpoints of
the window), predict 2018->2026, report out-of-sample fit. Restricted to countries
with a finite, stable Psi_w at all four endpoints.
Also report whether the linear model "explains" the 1998->2026 change for the big
in-work expanders (FR 2016/2019, DK 2025, FI 2025, ES 2023) -- marking the method break.
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RES = '/workspace/eval/followup/003-theory-update/results'
w = pd.read_csv('/workspace/eval/followup/002-living-update-cont/results/welfare_by_year.csv')


def val(CC, yr, col):
    r = w[(w.c == CC) & (w.t == yr)]
    if not len(r):
        return None, None
    return r[col].iloc[0], r['Psi_w_stab'].iloc[0]


def dpair(CC, y0, y1):
    """(d_a12, d_Psi_w) over [y0,y1] if Psi_w finite & stable at both ends."""
    a0, _ = val(CC, y0, 'a_bottom_quintile'); a1, _ = val(CC, y1, 'a_bottom_quintile')
    p0, s0 = val(CC, y0, 'Psi_w'); p1, s1 = val(CC, y1, 'Psi_w')
    if None in (a0, a1, p0, p1):
        return None
    if not (np.isfinite(p0) and np.isfinite(p1)) or s0 != 'stable' or s1 != 'stable':
        return None
    return (a1 - a0, p1 - p0)


CCs = sorted(w.c.unique())
fit_pts = [(CC, dpair(CC, 2009, 2017)) for CC in CCs]
fit_pts = [(c, d) for c, d in fit_pts if d is not None]
test_pts = [(CC, dpair(CC, 2018, 2026)) for CC in CCs]
test_pts = [(c, d) for c, d in test_pts if d is not None]

print("fit (2009->2017) countries:", [c for c, _ in fit_pts])
print("test(2018->2026) countries:", [c for c, _ in test_pts])

X = np.array([d[0] for _, d in fit_pts]); Y = np.array([d[1] for _, d in fit_pts])
beta, intercept = np.polyfit(X, Y, 1)
yhat = beta * X + intercept
ss_res = np.sum((Y - yhat) ** 2); ss_tot = np.sum((Y - Y.mean()) ** 2)
r2_in = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

Xt = np.array([d[0] for _, d in test_pts]); Yt = np.array([d[1] for _, d in test_pts])
Yt_hat = beta * Xt + intercept
ss_res_t = np.sum((Yt - Yt_hat) ** 2); ss_tot_t = np.sum((Yt - Yt.mean()) ** 2)
r2_out = 1 - ss_res_t / ss_tot_t if ss_tot_t > 0 else np.nan
mae_out = np.mean(np.abs(Yt - Yt_hat))

print(f"\nlinear fit d_Psi_w = {beta:.3f} * d_a12 + {intercept:.3f}")
print(f"in-sample  R^2 (2009->2017, n={len(X)}): {r2_in:.3f}")
print(f"out-sample R^2 (2018->2026, n={len(Xt)}): {r2_out:.3f}   MAE={mae_out:.3f}")

out = dict(fit_window='2009-2017', test_window='2018-2026',
           fit_countries=[c for c, _ in fit_pts], test_countries=[c for c, _ in test_pts],
           beta=round(float(beta), 4), intercept=round(float(intercept), 4),
           r2_in=round(float(r2_in), 4), r2_out=round(float(r2_out), 4),
           mae_out=round(float(mae_out), 4),
           fit_points={c: [round(d[0], 3), round(d[1], 3)] for c, d in fit_pts},
           test_points={c: [round(d[0], 3), round(d[1], 3)] for c, d in test_pts})

# 1998 -> 2026 for the big in-work expanders (method break flagged)
t2 = pd.read_csv('/workspace/eval/replication/codebase/results/table2a.csv')
WB = {'FR': 'FR', 'DK': 'DK', 'FI': 'FI', 'ES': 'SP'}
exp = {}
for CC in ['FR', 'DK', 'FI', 'ES']:
    p1998 = float(t2[t2.country == WB[CC]]['tradeoff_workingpoor'].iloc[0])
    p26, s26 = val(CC, 2026, 'Psi_w')
    a26, _ = val(CC, 2026, 'a_bottom_quintile')
    exp[CC] = dict(Psi_w_1998=round(p1998, 4),
                   Psi_w_2026=(round(float(p26), 4) if p26 is not None and np.isfinite(p26) else None),
                   Psi_w_2026_stab=s26, a12_2026=a26)
out['inwork_expanders_1998_vs_2026'] = exp
print("\n=== in-work expanders 1998 vs 2026 (method break: 1998 is survey-cell, 2026 hypothetical hh) ===")
for CC, v in exp.items():
    print(f"  {CC}: Psi_w 1998={v['Psi_w_1998']}  2026={v['Psi_w_2026']} ({v['Psi_w_2026_stab']})  a12_2026={v['a12_2026']}")
json.dump(out, open(f'{RES}/item4_linearisation.json', 'w'), indent=2)
print("\nwrote item4_linearisation.json")
