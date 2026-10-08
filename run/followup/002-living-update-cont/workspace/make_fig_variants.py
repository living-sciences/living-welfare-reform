#!/usr/bin/env python3
"""Fig 4: sensitivity of the headline bottom-quintile PTR and the 2026 ranking to
the five pre-declared variants that 001 had cut (V5 rent, V6 one child, lhw40,
V3 dispersion, employer-SSC inversion). Canvas-sized, two panels."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd

RES = '/workspace/eval/followup/002-living-update-cont/results'
OK = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#000000"]
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
                     "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25})
wv = pd.read_csv(f'{RES}/welfare_variants.csv')
VNAME = {'V5': 'V5 rent=20%AW', 'V6': 'V6 one child', 'lhw40': 'lhw=40 (full time)',
         'V3': 'V3 SES dispersion', 'ssc_inv': 'employer-SSC inversion (2025)'}
VCOL = {'V5': OK[0], 'V6': OK[2], 'lhw40': OK[3], 'V3': OK[1], 'ssc_inv': OK[4]}

fig, (axL, axR) = plt.subplots(1, 2, figsize=(14, 6))

# ---- Panel A: variant bottom-quintile PTR vs headline (all country-years) ----
hl = wv[wv.variant == 'headline'][['c', 't', 'a_bottom_quintile']].rename(
    columns={'a_bottom_quintile': 'a_hl'})
for v in ['ssc_inv', 'V5', 'V6', 'lhw40', 'V3']:
    sub = wv[wv.variant == v].merge(hl, on=['c', 't'])
    axL.scatter(sub.a_hl, sub.a_bottom_quintile, s=42, color=VCOL[v],
                edgecolor='k', lw=0.3, alpha=0.8, label=VNAME[v])
axL.plot([0, 100], [0, 100], '--', color='gray', lw=1)
axL.set_xlim(0, 100); axL.set_ylim(0, 100)
axL.set_xlabel('headline bottom-quintile PTR (%)')
axL.set_ylabel('variant bottom-quintile PTR (%)')
axL.set_title('Sensitivity of the key metric to variant assumptions\n'
              '(each point = one country-year; dashed = no change)')
axL.legend(fontsize=9, loc='lower right')

# ---- Panel B: 2026 ranking robustness (share of stable with Psi_w<Psi_d) ----
def share(df):
    d = df[(df.Psi_w_stab == 'stable') & (df.Psi_d_stab == 'stable')].dropna(subset=['Psi_w', 'Psi_d'])
    n = len(d)
    k = int((d.Psi_w < d.Psi_d).sum())
    return k, n
labels, ks, ns, cols = [], [], [], []
for v in ['headline', 'V3', 'V6', 'lhw40', 'V5']:
    k, n = share(wv[(wv.variant == v) & (wv.t == 2026)])
    labels.append('headline' if v == 'headline' else VNAME[v].split(' ')[0])
    ks.append(k); ns.append(n); cols.append('gray' if v == 'headline' else VCOL[v])
k, n = share(wv[(wv.variant == 'ssc_inv') & (wv.t == 2025)])
labels.append('SSC-inv\n(2025)'); ks.append(k); ns.append(n); cols.append(VCOL['ssc_inv'])
y = np.arange(len(labels))
axR.barh(y, [k / n * 100 for k, n in zip(ks, ns)], color=cols, edgecolor='k', lw=0.4)
for i, (k, n) in enumerate(zip(ks, ns)):
    axR.text(k / n * 100 + 1.5, i, f'{k} of {n}', va='center', fontsize=10)
axR.set_yticks(y); axR.set_yticklabels(labels)
axR.invert_yaxis(); axR.set_xlim(0, 100)
axR.set_xlabel('% of stable countries with Ψ_w < Ψ_d (in-work transfer cheaper)')
axR.set_title('2026 ranking is robust across variants\n(all ≈78–100%: in-work transfer stays cheaper)')
fig.tight_layout()
fig.savefig(f'{RES}/fig4_variant_sensitivity.png', facecolor='white')
print("fig4 done")
