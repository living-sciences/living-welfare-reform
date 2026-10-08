"""Item 1 driver: inverse-optimum g_d for 1998 + 2009-2026, all 14 V countries.
Writes results/g_by_decile.csv and results/item1_agreement.csv (+ console summary).
[CONSISTENCY CHECK] -- g is built from the same tau,a,formulas that produce 001's
Pareto flags, so agreement with those flags is close to mechanical.
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import saez_inverse as si
import welfare_core as wc, fixed_inputs as fi, welfare_layer as wl

RES = '/workspace/eval/followup/003-theory-update/results'
os.makedirs(RES, exist_ok=True)
YEARS = list(range(2009, 2027))
V = si.EM_COUNTRIES

# 001 Pareto flags (eff_w>0) and Psi from welfare_by_year.csv (V4 headline)
wby = pd.read_csv('/workspace/eval/followup/002-living-update-cont/results/welfare_by_year.csv')

rows_g = []        # long: c,era,t,d,w,tau,a,eta,g, g0(on d=0 marker)
rows_agree = []    # one row per (c,era): g-Pareto vs 001 flag, emp-share g<0

def handle(CC, era, year):
    if era == '1998':
        inp = si.decile_inputs_1998(CC); gw = si.gw_deciles(CC, None)
        # 001 flag for 1998 = table2a eff_w>0
        t2 = pd.read_csv('/workspace/eval/replication/codebase/results/table2a.csv')
        wbcode = fi.EM2WB[CC]
        effw = float(t2[t2.country == wbcode]['eff_workingpoor'].iloc[0])
        psiw = float(t2[t2.country == wbcode]['tradeoff_workingpoor'].iloc[0])
        flag001 = effw > 0; stab = 'paper'
    else:
        inp = si.decile_inputs_year(CC, year)
        if inp is None:
            return
        gw = si.gw_deciles(CC, year)
        row = wby[(wby.c == CC) & (wby.t == year)]
        effw = float(row['eff_w'].iloc[0]); psiw = row['Psi_w'].iloc[0]
        flag001 = effw > 0; stab = row['Psi_w_stab'].iloc[0]
    res = si.invert_g(inp)
    g = res['g']
    for d in range(10):
        rows_g.append(dict(c=CC, era=era, t=year, d=d + 1,
                           w=round(float(inp['w'][d]), 4) if np.isfinite(inp['w'][d]) else None,
                           tau=round(float(inp['tau'][d]), 4) if np.isfinite(inp['tau'][d]) else None,
                           a=round(float(inp['a'][d]), 4) if np.isfinite(inp['a'][d]) else None,
                           eta=si.ETA[d], g=round(float(g[d]), 4) if np.isfinite(g[d]) else None))
    gneg = [d for d in range(10) if np.isfinite(g[d]) and g[d] < 0]
    gwd = set(gw['gw_deciles'])
    g_pareto = len(gwd & set(gneg)) > 0                 # iff restricted to G_w deciles
    g_pareto_all = len(gneg) > 0                        # all-employed version (beside it)
    rows_agree.append(dict(
        c=CC, era=era, t=year,
        g0=round(float(res['g0']), 4) if np.isfinite(res['g0']) else None,
        emp_share_g_neg=round(si.emp_share_g_neg(inp, g), 4),
        n_dec_g_neg=len(gneg),
        g_pareto_iff=int(g_pareto), g_pareto_allemp=int(g_pareto_all),
        flag001_eff_w_pos=int(flag001), eff_w=round(effw, 4),
        Psi_w=(round(float(psiw), 4) if (psiw == psiw and psiw is not None) else None),
        Psi_w_stab=stab, Dw=round(float(gw['Dw']), 4), mono_w=int(res['mono']),
        agree=int(g_pareto == flag001)))

for CC in V:
    handle(CC, '1998', 1998)
for CC in V:
    for y in YEARS:
        handle(CC, 'policy', y)

dg = pd.DataFrame(rows_g); dg.to_csv(f'{RES}/g_by_decile.csv', index=False)
da = pd.DataFrame(rows_agree); da.to_csv(f'{RES}/item1_agreement.csv', index=False)
print(f"wrote g_by_decile.csv ({len(dg)}), item1_agreement.csv ({len(da)})")

# ---- 1998 all-country report vs table2a (only DK 'Pareto' in paper's strict sense) ----
print("\n=== 1998 inverse-optimum, all V countries (g-Pareto iff vs table2a eff_w>0) ===")
d98 = da[da.era == '1998'].copy()
print(d98[['c', 'g0', 'emp_share_g_neg', 'g_pareto_iff', 'g_pareto_allemp',
           'flag001_eff_w_pos', 'eff_w', 'agree']].to_string(index=False))

# ---- agreement over policy years ----
dp = da[da.era == 'policy']
print("\n=== [CONSISTENCY CHECK] g-Pareto-iff vs 001 eff_w>0, policy years 2009-2026 ===")
print("overall agreement: %d/%d = %.1f%%" % (dp.agree.sum(), len(dp), 100 * dp.agree.mean()))
# restrict to 'stable' rows where Psi_w is meaningful
dps = dp[dp.Psi_w_stab == 'stable']
print("on 'stable' country-years only: %d/%d = %.1f%%"
      % (dps.agree.sum(), len(dps), 100 * dps.agree.mean() if len(dps) else 0))

# ---- share of employment with g<0 by country, 1998 vs 2026 ----
print("\n=== share of employment in g<0 deciles: 1998 vs 2026 ===")
piv = []
for CC in V:
    a98 = da[(da.c == CC) & (da.era == '1998')]['emp_share_g_neg']
    a26 = da[(da.c == CC) & (da.t == 2026)]['emp_share_g_neg']
    piv.append(dict(c=CC, s1998=float(a98.iloc[0]) if len(a98) else None,
                    s2026=float(a26.iloc[0]) if len(a26) else None))
pv = pd.DataFrame(piv)
pv['delta'] = pv['s2026'] - pv['s1998']
print(pv.round(3).to_string(index=False))
json.dump({'agreement_policy_pct': round(100 * dp.agree.mean(), 1),
           'agreement_stable_pct': round(100 * dps.agree.mean(), 1) if len(dps) else None,
           'n_policy': int(len(dp)), 'n_stable': int(len(dps)),
           'emp_share_g_neg_1998_2026': pv.round(4).to_dict('records')},
          open(f'{RES}/item1_summary.json', 'w'), indent=2)
print("\nwrote item1_summary.json")
