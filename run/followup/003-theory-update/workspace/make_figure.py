"""Item 2 deliverable figure: elasticity frontier by era in (eta_avg, eps) space,
with post-2007 literature bands labelled by origin. PNG + PDF.
Plus a supporting figure: critical eta_avg over time (the Table-3 analogue).
"""
import os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

RES = '/workspace/eval/followup/003-theory-update/results'
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})

df = pd.read_csv(f'{RES}/frontier_by_era.csv')
ERAS = [2009, 2015, 2020, 2026]
COND = {'identical': ('Ψ_w<Ψ_d (in-work cheaper)', OKABE_ITO[0], '-'),
        'zeroloss':  ('Ψ_w<1', OKABE_ITO[2], '--'),
        'pareto':    ('Pareto (no losers)', OKABE_ITO[3], ':')}
LIT = [('Kleven 2024 (US EITC)', 0.00, 0.02, '#999999'),
       ('Bartels & Shupe 2023', 0.08, 0.14, '#E69F00'),
       ('Chetty et al. 2011 (mostly US)', 0.20, 0.30, '#56B4E9'),
       ('Lundberg & Norell 2018', 0.36, 0.40, '#CC79A7')]

fig, axes = plt.subplots(2, 2, figsize=(11, 8.5), sharex=True, sharey=True)
for ax, era in zip(axes.ravel(), ERAS):
    for lbl, lo, hi, col in LIT:
        ax.axvspan(lo, hi, color=col, alpha=0.16, zorder=0)
    med = df[(df.c == 'MEDIAN') & (df.era == era)]
    for cond, (clbl, col, ls) in COND.items():
        m = med[med.condition == cond].sort_values('eps')
        ax.plot(m.crit_eta, m.eps, color=col, ls=ls, marker='o', ms=3.5, lw=2, label=clbl, zorder=3)
    ax.axhline(0.1, color='k', lw=0.8, alpha=0.4, zorder=1)
    ax.text(1.42, 0.105, 'ε=0.1 (benchmark)', fontsize=7.5, ha='right', va='bottom', alpha=0.6)
    ax.set_title(f'{era}', fontweight='bold')
    ax.set_xlim(0, 1.5); ax.set_ylim(-0.02, 0.52)
axes[1, 0].set_xlabel('average extensive elasticity  η̄  →  (in-work transfer cheaper to the right)')
axes[1, 1].set_xlabel('average extensive elasticity  η̄')
axes[0, 0].set_ylabel('intensive elasticity  ε'); axes[1, 0].set_ylabel('intensive elasticity  ε')

h1 = [plt.Line2D([], [], color=c, ls=ls, lw=2, marker='o', ms=3.5, label=l)
      for (l, c, ls) in COND.values()]
h2 = [Patch(facecolor=col, alpha=0.16, label=lbl) for (lbl, lo, hi, col) in LIT]
leg1 = fig.legend(handles=h1, loc='upper center', bbox_to_anchor=(0.5, 0.055),
                  ncol=3, frameon=False, fontsize=9, title='critical-η boundary (median over fixed panel FI,FR,EL,IT,SE)')
fig.legend(handles=h2, loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=4,
           frameon=False, fontsize=8.5, title='post-2007 extensive-elasticity evidence (band = source)')
fig.add_artist(leg1)
fig.suptitle('Elasticity frontier by policy era: where the in-work transfer dominates\n'
             '(Immervoll–Kleven–Kreiner–Saez framework, 2026 rules; [CALIBRATED])',
             fontweight='bold', y=0.98)
fig.tight_layout(rect=[0, 0.09, 1, 0.95])
for ext in ['png', 'pdf']:
    fig.savefig(f'{RES}/fig1_elasticity_frontier.{ext}', facecolor='white')
plt.close(fig)
print("wrote fig1_elasticity_frontier.png/.pdf")

# ---- supporting figure: critical eta_avg over time (eps=0.1) + g<0 emp share ----
ce = pd.read_csv('/workspace/eval/followup/002-living-update-cont/results/critical_eta_by_year.csv')
fig2, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.6))
PANEL = ['FI', 'FR', 'EL', 'IT', 'SE']
yrs = list(range(2009, 2027))
for cond, col, ls, lab in [('crit_identical', OKABE_ITO[0], '-', 'Ψ_w=Ψ_d'),
                           ('crit_zeroloss', OKABE_ITO[2], '--', 'Ψ_w=1'),
                           ('crit_pareto', OKABE_ITO[3], ':', 'Pareto')]:
    med = [ce[(ce.t == y) & (ce.c.isin(PANEL))][cond].median() for y in yrs]
    axA.plot(yrs, med, color=col, ls=ls, lw=2, marker='o', ms=3, label=f'critical η̄ for {lab}')
for lbl, lo, hi, c in LIT:
    axA.axhspan(lo, hi, color=c, alpha=0.14)
axA.set_title('Critical average elasticity over time (ε=0.1, median over FI,FR,EL,IT,SE)', fontsize=11)
axA.set_xlabel('policy year'); axA.set_ylabel('critical η̄'); axA.set_ylim(0, 1.5)
axA.legend(fontsize=8, frameon=False)

ag = pd.read_csv(f'{RES}/item1_agreement.csv')
a98 = ag[ag.era == '1998'].set_index('c')['emp_share_g_neg']
a26 = ag[ag.t == 2026].set_index('c')['emp_share_g_neg']
ccs = [c for c in ['AT', 'BE', 'DK', 'FI', 'FR', 'DE', 'EL', 'IE', 'IT', 'LU', 'NL', 'PT', 'ES', 'SE']]
x = np.arange(len(ccs)); wdt = 0.38
axB.bar(x - wdt / 2, [a98.get(c, 0) for c in ccs], wdt, color='#999999', label='1998 (workbook)')
axB.bar(x + wdt / 2, [a26.get(c, 0) for c in ccs], wdt, color=OKABE_ITO[1], label='2026 rules')
axB.set_xticks(x); axB.set_xticklabels(ccs, fontsize=8.5)
axB.set_title('Employment share in deciles with g<0 (inverse-optimum)  [CONSISTENCY CHECK]', fontsize=10.5)
axB.set_ylabel('employment share, g<0 deciles'); axB.legend(fontsize=9, frameon=False)
fig2.tight_layout()
for ext in ['png', 'pdf']:
    fig2.savefig(f'{RES}/fig2_critical_eta_and_g.{ext}', facecolor='white')
plt.close(fig2)
print("wrote fig2_critical_eta_and_g.png/.pdf")
