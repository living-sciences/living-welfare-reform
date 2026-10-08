"""Item 2: elasticity frontier by era in (eta_avg, eps) space.

For each era in {2009,2015,2020,2026} and each country, find the critical average
extensive elasticity eta_avg* (Table-3 profile eta_avg*[2,2,1.5,1.5,1,1,.5,.5,0,0])
at which each boundary is crossed, as a function of the intensive elasticity eps:
  - identical:  Psi_w = Psi_d        (eta_avg > crit => in-work transfer cheaper)
  - zeroloss:   Psi_w = 1  (Dw = 0)  (eta_avg > crit => Psi_w < 1)
  - pareto:     1 - Dw = max_j s_j/e_j  (eta_avg > crit => no losers / Pareto)
Aggregated as the median over the FIXED panel stable in all four eras:
  PANEL = {FI, FR, EL, IT, SE}.
All at the V4 (q=0) headline regime, cap 0.999 -- identical to 001's Psi.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, '/workspace/eval/followup/002-living-update-cont/workspace')
os.environ.setdefault('SHARED', '/workspace/eval/followup_staging/shared-data')
import welfare_core as wc, fixed_inputs as fi, welfare_layer as wl

RES = '/workspace/eval/followup/003-theory-update/results'
ERAS = [2009, 2015, 2020, 2026]
PANEL = ['FI', 'FR', 'EL', 'IT', 'SE']          # stable in all four eras
EPS_GRID = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
CAP = 0.999

# literature extensive-elasticity bands (item 2), labelled by origin
LIT_BANDS = [
    ('Kleven 2024 (US EITC)', 0.00, 0.02),
    ('Bartels & Shupe 2023', 0.08, 0.14),
    ('Chetty et al. 2011 (mostly US)', 0.20, 0.30),
    ('Lundberg & Norell 2018', 0.36, 0.40),
]
LIT_POINTS = {'Kleven 2024 (US EITC)': 0.0, 'Bartels & Shupe 2023': 0.11,
              'Chetty et al. 2011 (mostly US)': 0.25, 'Lundberg & Norell 2018': 0.38}


def _data(CC, year):
    tau, a, meta = wl.build_tau_a(CC, year, q_override=0.0, cap=CAP)
    if tau is None:
        return None
    cells = fi.cells_1998(fi.EM2WB[CC])
    return dict(cc=CC, P=cells['P'], sh=cells['s'], em=cells['e'], tau=tau, a=a,
                maxse=(cells['s'] / np.where(cells['e'] > 0, cells['e'], np.inf)).max())


def crit_eta(data, eps, which):
    """Critical eta_avg for a condition at given eps; None if no sign change on (1e-6,3]."""
    def metrics(ea):
        return wc.compute(data, wc.eta_table3_profile(ea), eps)
    if which == 'identical':
        f = lambda ea: metrics(ea)['tradeoff_workingpoor'] - metrics(ea)['tradeoff_demogrant']
    elif which == 'zeroloss':
        f = lambda ea: metrics(ea)['Dw']
    elif which == 'pareto':
        f = lambda ea: (1 - metrics(ea)['Dw']) - data['maxse']
    return wl._bracket_root(f)


def run():
    rows = []
    for yr in ERAS:
        datas = {CC: _data(CC, yr) for CC in PANEL}
        for eps in EPS_GRID:
            for which in ['identical', 'zeroloss', 'pareto']:
                vals = []
                for CC in PANEL:
                    d = datas[CC]
                    if d is None:
                        continue
                    c = crit_eta(d, eps, which)
                    if c is not None:
                        vals.append(c)
                        rows.append(dict(era=yr, eps=eps, condition=which, c=CC,
                                         crit_eta=round(c, 4)))
                if vals:
                    rows.append(dict(era=yr, eps=eps, condition=which, c='MEDIAN',
                                     crit_eta=round(float(np.median(vals)), 4)))
    df = pd.DataFrame(rows)
    df.to_csv(f'{RES}/frontier_by_era.csv', index=False)
    print(f"wrote frontier_by_era.csv ({len(df)} rows)")

    # per-country survival table at eps=0.1 vs literature points -------------
    w = pd.read_csv('/workspace/eval/followup/002-living-update-cont/results/welfare_by_year.csv')
    srv = []
    for yr in ERAS:
        stable = w[(w.t == yr) & (w.Psi_w_stab == 'stable') &
                   (w.Psi_d_stab == 'stable')]['c'].tolist()
        for CC in fi.EM_COUNTRIES:
            d = _data(CC, yr)
            if d is None:
                continue
            ci = crit_eta(d, 0.1, 'identical')
            cz = crit_eta(d, 0.1, 'zeroloss')
            cp = crit_eta(d, 0.1, 'pareto')
            row = dict(c=CC, era=yr, stable=int(CC in stable),
                       crit_identical=round(ci, 4) if ci else None,
                       crit_zeroloss=round(cz, 4) if cz else None,
                       crit_pareto=round(cp, 4) if cp else None)
            for lbl, pt in LIT_POINTS.items():
                # conclusion "survives" (holds) at literature elasticity pt if crit<pt
                row[f'identical@{lbl.split()[0]}'] = int(ci is not None and ci < pt)
                row[f'zeroloss@{lbl.split()[0]}'] = int(cz is not None and cz < pt)
            srv.append(row)
    sv = pd.DataFrame(srv)
    sv.to_csv(f'{RES}/frontier_survival.csv', index=False)
    print(f"wrote frontier_survival.csv ({len(sv)} rows)")

    # console summary: median critical eta over PANEL at eps=0.1, per era
    print("\n=== median critical eta_avg over fixed panel {FI,FR,EL,IT,SE}, eps=0.1 ===")
    med = df[(df.c == 'MEDIAN') & (df.eps == 0.1)].pivot(index='era', columns='condition',
                                                         values='crit_eta')
    print(med.to_string())
    print("\n=== survival at literature elasticities (eps=0.1): count of V countries where "
          "Psi_w<Psi_d holds ===")
    for yr in ERAS:
        sub = sv[sv.era == yr]
        line = f"  {yr}: "
        for lbl in LIT_POINTS:
            k = lbl.split()[0]
            line += f"{lbl.split()[0]}({LIT_POINTS[lbl]})={sub[f'identical@{k}'].sum()}/{len(sub)}  "
        print(line)
    return df, sv


if __name__ == '__main__':
    run()
