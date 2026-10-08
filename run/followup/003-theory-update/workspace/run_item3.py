"""Item 3: minimal amendment -- reallocate the extensive elasticity onto secondary
earners and lone parents (groups 2,7,8,9,10; 0-idx 1,6,7,8,9), holding the
employment-weighted AGGREGATE eta fixed at the benchmark. Paper Table 6(b) / the
authors' couples extension (Immervoll, Kleven, Kreiner & Verdelin 2011, JPubE).
Ask whether concentration explains where in-work dominance weakens by 2026.

Alternative discussed & rejected: an unemployment/wage-response channel
(Kroft, Kucko, Lehmann & Schmieder 2020, AEJ:Policy) -- needs parameters 001
cannot calibrate. [PROPOSED]
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, '/workspace/eval/followup/002-living-update-cont/workspace')
os.environ.setdefault('SHARED', '/workspace/eval/followup_staging/shared-data')
import welfare_core as wc, fixed_inputs as fi, welfare_layer as wl

RES = '/workspace/eval/followup/003-theory-update/results'
SEC_GROUPS = [1, 6, 7, 8, 9]            # groups 2,7,8,9,10 (0-indexed)
ERAS = [2009, 2015, 2020, 2026]
CAP = 0.999
BENCH = wc.ETA_BENCHMARK                 # == eta_table3_profile(0.2)


def eta_concentrated(e_cells):
    """10x10 eta: benchmark decile profile placed only on secondary/lone-parent
    groups, rescaled so employment-weighted aggregate eta == benchmark's."""
    prof = BENCH
    target = float((e_cells * np.tile(prof, (10, 1))).sum())      # aggregate with benchmark on all groups
    eta = np.zeros((10, 10))
    for g in SEC_GROUPS:
        eta[g, :] = prof
    raw = float((e_cells * eta).sum())
    if raw > 0:
        eta *= target / raw
    return eta


def welf(CC, year, eta):
    tau, a, meta = wl.build_tau_a(CC, year, q_override=0.0, cap=CAP)
    if tau is None:
        return None
    cells = fi.cells_1998(fi.EM2WB[CC])
    data = dict(cc=CC, P=cells['P'], sh=cells['s'], em=cells['e'], tau=tau, a=a)
    return wc.compute(data, eta, wc.EPS_BENCHMARK)


def run():
    w = pd.read_csv('/workspace/eval/followup/002-living-update-cont/results/welfare_by_year.csv')
    rows = []
    for yr in ERAS:
        stable = w[(w.t == yr) & (w.Psi_w_stab == 'stable') &
                   (w.Psi_d_stab == 'stable')]['c'].tolist()
        for CC in fi.EM_COUNTRIES:
            cells = fi.cells_1998(fi.EM2WB[CC])
            rb = welf(CC, yr, BENCH)
            rc = welf(CC, yr, eta_concentrated(cells['e']))
            if rb is None or rc is None:
                continue
            rows.append(dict(
                c=CC, era=yr, stable=int(CC in stable),
                Psi_w_bench=round(rb['tradeoff_workingpoor'], 4),
                Psi_d_bench=round(rb['tradeoff_demogrant'], 4),
                effw_bench=round(rb['eff_workingpoor'], 4),
                inwork_cheaper_bench=int(np.isfinite(rb['tradeoff_workingpoor']) and
                    np.isfinite(rb['tradeoff_demogrant']) and
                    rb['tradeoff_workingpoor'] < rb['tradeoff_demogrant']),
                Psi_w_conc=round(rc['tradeoff_workingpoor'], 4),
                Psi_d_conc=round(rc['tradeoff_demogrant'], 4),
                effw_conc=round(rc['eff_workingpoor'], 4),
                inwork_cheaper_conc=int(np.isfinite(rc['tradeoff_workingpoor']) and
                    np.isfinite(rc['tradeoff_demogrant']) and
                    rc['tradeoff_workingpoor'] < rc['tradeoff_demogrant'])))
    df = pd.DataFrame(rows)
    df.to_csv(f'{RES}/item3_concentration.csv', index=False)
    print(f"wrote item3_concentration.csv ({len(df)})")

    print("\n=== in-work-cheaper count (Psi_w<Psi_d) over STABLE set: benchmark vs concentrated ===")
    for yr in ERAS:
        s = df[(df.era == yr) & (df.stable == 1)]
        print(f"  {yr}: n_stable={len(s)}  benchmark={s.inwork_cheaper_bench.sum()}  "
              f"concentrated={s.inwork_cheaper_conc.sum()}")

    print("\n=== 2026 per-country: does concentration change the in-work-cheaper verdict? ===")
    s26 = df[(df.era == 2026)]
    flip = s26[s26.inwork_cheaper_bench != s26.inwork_cheaper_conc]
    print(s26[['c', 'stable', 'Psi_w_bench', 'Psi_d_bench', 'inwork_cheaper_bench',
               'Psi_w_conc', 'Psi_d_conc', 'inwork_cheaper_conc']].to_string(index=False))
    print("\nflips (bench != conc):", flip.c.tolist())

    # efficiency improvement from concentration (stable 2026)
    s = df[(df.era == 2026) & (df.stable == 1)].copy()
    s['d_effw'] = s.effw_conc - s.effw_bench
    print("\n=== 2026 stable: change in eff_w from concentrating eta on secondary/lone-parent ===")
    print(s[['c', 'effw_bench', 'effw_conc', 'd_effw']].round(4).to_string(index=False))
    return df


if __name__ == '__main__':
    run()
