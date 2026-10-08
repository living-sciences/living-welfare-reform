"""Item 5: calibration table -- 1998 vs 2026 parameters and moments, with sources."""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, '/workspace/eval/followup/002-living-update-cont/workspace')
os.environ.setdefault('SHARED', '/workspace/eval/followup_staging/shared-data')
import welfare_core as wc, fixed_inputs as fi, welfare_layer as wl
import frontier as fr

RES = '/workspace/eval/followup/003-theory-update/results'
PANEL = ['FI', 'FR', 'EL', 'IT', 'SE']
CAP = 0.999


def data_1998(CC):
    d = wc.load_country(fi.EM2WB[CC]); cells = fi.cells_1998(fi.EM2WB[CC])
    tau = np.clip(d['tau'], -0.5, CAP); a = np.clip(d['a'], -0.5, CAP)
    return dict(cc=CC, P=cells['P'], sh=cells['s'], em=cells['e'], tau=tau, a=a,
                maxse=(cells['s'] / np.where(cells['e'] > 0, cells['e'], np.inf)).max())


def crit_med(get_data, which):
    vals = []
    for CC in PANEL:
        d = get_data(CC)
        c = fr.crit_eta(d, 0.1, which)
        if c is not None:
            vals.append(c)
    return round(float(np.median(vals)), 3) if vals else None


# 1998 critical etas
c1998 = {w: crit_med(data_1998, w) for w in ['identical', 'zeroloss', 'pareto']}
# 2026 critical etas
c2026 = {w: crit_med(lambda CC: fr._data(CC, 2026), w) for w in ['identical', 'zeroloss', 'pareto']}

# bottom-quintile PTR median over panel, 1998 (workbook) and 2026
wby = pd.read_csv('/workspace/eval/followup/002-living-update-cont/results/welfare_by_year.csv')
a12_2026 = round(float(wby[(wby.t == 2026) & (wby.c.isin(PANEL))]['a_bottom_quintile'].median()), 1)
# 1998 bottom-quintile PTR from workbook (employment-weighted deciles 1-2)
a12_1998 = []
for CC in PANEL:
    inp = __import__('saez_inverse').decile_inputs_1998(CC)
    cells = fi.cells_1998(fi.EM2WB[CC]); e = cells['e']
    d = wc.load_country(fi.EM2WB[CC]); a = np.clip(d['a'], -0.5, CAP)
    w12 = e[:, :2]
    a12_1998.append(100 * np.nansum(w12 * a[:, :2]) / w12.sum())
a12_1998 = round(float(np.median(a12_1998)), 1)

# share emp g<0 median over panel
ag = pd.read_csv(f'{RES}/item1_agreement.csv')
g98 = round(float(ag[(ag.era == '1998') & (ag.c.isin(PANEL))]['emp_share_g_neg'].median()), 3)
g26 = round(float(ag[(ag.t == 2026) & (ag.c.isin(PANEL))]['emp_share_g_neg'].median()), 3)

rows = [
    dict(parameter='Intensive (hours) elasticity ε', v1998='0.10', v2026='0.10',
         source='paper benchmark (IKKS 2007), held fixed'),
    dict(parameter='Average extensive elasticity η̄', v1998='0.20', v2026='0.20',
         source='paper benchmark profile [.4,.4,.3,.3,.2,.2,.1,.1,0,0]'),
    dict(parameter='q regime (UB-receipt weighting)', v1998='mixed-q (Table A3)', v2026='V4 / q=0',
         source='001 headline rule 3 (7 of 14 no-UB fallbacks)'),
    dict(parameter='Median critical η̄ for Ψ_w=Ψ_d  (panel)', v1998=f'{c1998["identical"]}', v2026=f'{c2026["identical"]}',
         source='this study, Table-3 analogue, ε=0.1, panel {FI,FR,EL,IT,SE}'),
    dict(parameter='Median critical η̄ for Ψ_w=1  (panel)', v1998=f'{c1998["zeroloss"]}', v2026=f'{c2026["zeroloss"]}',
         source='this study'),
    dict(parameter='Median critical η̄ for Pareto  (panel)', v1998=f'{c1998["pareto"]}', v2026=f'{c2026["pareto"]}',
         source='this study'),
    dict(parameter='Median bottom-quintile PTR a_{1-2} (panel)', v1998=f'{a12_1998}%', v2026=f'{a12_2026}%',
         source='1998 workbook / 001 rates_deciles (method break at 1998)'),
    dict(parameter='Median emp. share in g<0 deciles (panel)', v1998=f'{g98}', v2026=f'{g26}',
         source='this study, inverse-optimum [CONSISTENCY CHECK]'),
    dict(parameter='Lit. extensive elasticity: Kleven 2024', v1998='—', v2026='≈0.00',
         source='Kleven 2024, US EITC participation response'),
    dict(parameter='Lit.: Bartels & Shupe 2023 (Europe)', v1998='—', v2026='0.08 (men) / 0.14 (women)',
         source='Bartels & Shupe 2023'),
    dict(parameter='Lit.: Chetty et al. 2011', v1998='—', v2026='≈0.25 (mostly US)',
         source='Chetty et al. 2011'),
    dict(parameter='Lit.: Lundberg & Norell 2018', v1998='—', v2026='0.38',
         source='Lundberg & Norell 2018'),
    dict(parameter='Lit.: Bargain, Orsini & Peichl 2014', v1998='—', v2026='extensive larger at bottom (qualitative)',
         source='Bargain, Orsini & Peichl 2014 (matches benchmark profile shape)'),
]
df = pd.DataFrame(rows)[['parameter', 'v1998', 'v2026', 'source']]
df.columns = ['parameter', '1998', '2026', 'source']
df.to_csv(f'{RES}/calibration_table.csv', index=False)
print(df.to_string(index=False))
json.dump(dict(crit_1998=c1998, crit_2026=c2026, a12_1998=a12_1998, a12_2026=a12_2026,
               gshare_1998=g98, gshare_2026=g26, panel=PANEL),
          open(f'{RES}/calibration_summary.json', 'w'), indent=2)
print("\nwrote calibration_table.csv, calibration_summary.json")
