"""Item 4b: external check -- cost per additional worker / FTE of a marginal
lump-sum in-work transfer in Belgium (2016 rules), vs de Mahieu (2021) IJM 14(1):43-72.
[CALIBRATED vs literature]. Paper framework eq. (13); dT cancels.

  net cost        = dT * sum_j E_j [1 - eta_j a_j/(1-a_j)]
  additional work = sum_j eta_j E_j dT / (w_j (1-a_j))
  additional FTE  = same, each cell weighted by lhw_j/40
  w_j = r_j * AW_2016 (annual gross EUR); E_j = P e_j (P cancels in ratios)
  lhw_j = clamp(40 * y_j/(0.5 AW), 8, 40), y_j = r_j AW (k=1) -> clamp(80 r_j, 8, 40)

Published (de Mahieu 2021): per FTE EUR 368.5k-1660.1k; per participant EUR 121.1k-560.7k.
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, '/workspace/eval/followup/002-living-update-cont/workspace')
os.environ.setdefault('SHARED', '/workspace/eval/followup_staging/shared-data')
import welfare_core as wc, fixed_inputs as fi, welfare_layer as wl

RES = '/workspace/eval/followup/003-theory-update/results'
CAP = 0.999
CC, YEAR = 'BE', 2016

cells = fi.cells_1998('BE')
s, e, P = cells['s'], cells['e'], cells['P']
s_d, e_d = s.sum(0), e.sum(0)
r_d = np.where(e_d > 0, s_d / e_d, np.nan)
AW_month = fi.aw_month('BE', YEAR)
AW_ann = AW_month * 12.0
w_d = r_d * AW_ann                                   # annual gross EUR by decile
dp = wl.decile_profile('BE', YEAR, q_override=0.0, cap=CAP)
a_d = dp['a_d']                                      # participation tax rate by decile
lhw_d = np.clip(80.0 * r_d, 8, 40)                   # hours rule at k=1
E_d = P * e_d

ETA_BENCH = wc.ETA_BENCHMARK                          # [.4,.4,.3,.3,.2,.2,.1,.1,0,0]
ETA_BS = np.full(10, 0.11)                            # Bartels & Shupe 2023 mid (0.08 men/0.14 women)

PUB = dict(fte_lo=368.5, fte_hi=1660.1, part_lo=121.1, part_hi=560.7)  # EUR thousand


def compute(target_deciles, eta):
    j = np.array(target_deciles)                     # 0-indexed deciles
    a = a_d[j]; w = w_d[j]; E = E_d[j]; lhw = lhw_d[j]; et = eta[j]
    net_cost = np.sum(E * (1 - et * a / (1 - a)))             # per unit dT
    add_work = np.sum(et * E / (w * (1 - a)))
    add_fte = np.sum(et * E * (lhw / 40.0) / (w * (1 - a)))
    cpp = net_cost / add_work if add_work != 0 else np.nan   # EUR per participant
    cpf = net_cost / add_fte if add_fte != 0 else np.nan     # EUR per FTE
    return cpp / 1000.0, cpf / 1000.0                        # EUR thousand


rows = []
for lbl, eta in [('benchmark', ETA_BENCH), ('Bartels-Shupe', ETA_BS)]:
    for tgt_lbl, tgt in [('deciles_1-2', [0, 1]), ('deciles_1-3', [0, 1, 2])]:
        cpp, cpf = compute(tgt, eta)
        in_fte = 'inside' if PUB['fte_lo'] <= cpf <= PUB['fte_hi'] else ('below' if cpf < PUB['fte_lo'] else 'above')
        in_pp = 'inside' if PUB['part_lo'] <= cpp <= PUB['part_hi'] else ('below' if cpp < PUB['part_lo'] else 'above')
        rows.append(dict(eta=lbl, target=tgt_lbl,
                         model_cost_per_participant_kEUR=round(cpp, 1),
                         model_cost_per_FTE_kEUR=round(cpf, 1),
                         pub_participant_kEUR='121.1-560.7', pub_FTE_kEUR='368.5-1660.1',
                         participant_vs_pub=in_pp, FTE_vs_pub=in_fte))

df = pd.DataFrame(rows)
df.to_csv(f'{RES}/external_check_be.csv', index=False)
print("BE 2016: AW_month=%.1f AW_ann=%.0f EUR" % (AW_month, AW_ann))
print("decile r_d:", np.round(r_d, 3))
print("decile a_d:", np.round(a_d, 3))
print("decile w_d (EUR):", np.round(w_d, 0))
print("decile lhw:", np.round(lhw_d, 1))
print()
print(df.to_string(index=False))
json.dump(dict(AW_ann_EUR=round(AW_ann), rows=df.to_dict('records'), published=PUB),
          open(f'{RES}/item4b_summary.json', 'w'), indent=2)
print("\nwrote external_check_be.csv, item4b_summary.json")
