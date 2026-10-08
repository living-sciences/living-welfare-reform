#!/usr/bin/env python3
"""Three canvas figures for the living-update follow-up."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
import fixed_inputs as fi

RES = '/workspace/eval/followup/002-living-update-cont/results'
OK = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25,
})
EM2WB = fi.WB2EM
PAPER = pd.read_csv('/workspace/eval/replication/codebase/figures/tax_rates_by_decile.csv')
DEC = pd.read_csv(f'{RES}/rates_deciles.csv')
WBY = pd.read_csv(f'{RES}/welfare_by_year.csv')
SC = json.load(open(f'{RES}/headline_scalars.json'))
Vd = set(SC['V_delta_change_validated'])
ORDER = ['DK','FI','SE','AT','BE','DE','FR','LU','NL','EL','ES','IE','IT','PT']
NAMES = {'AT':'Austria','BE':'Belgium','DK':'Denmark','FI':'Finland','FR':'France','DE':'Germany',
         'EL':'Greece','IE':'Ireland','IT':'Italy','LU':'Luxembourg','NL':'Netherlands',
         'PT':'Portugal','ES':'Spain','SE':'Sweden'}


def fig1():
    fig, axes = plt.subplots(4, 4, figsize=(13, 11), sharex=True)
    axes = axes.flatten()
    for i, cc in enumerate(ORDER):
        ax = axes[i]
        wb = EM2WB_INV(cc)
        p = PAPER[PAPER.country == wb].sort_values('decile')
        d09 = DEC[(DEC.c == cc) & (DEC.t == 2009)].sort_values('d')
        d26 = DEC[(DEC.c == cc) & (DEC.t == 2026)].sort_values('d')
        ax.plot(p.decile, p.participation_tax_rate, 'o', color='gray', ms=5,
                label='1998 (paper)', zorder=5)
        ax.plot(d09.d, d09.participation_tax_rate, '-s', color=OK[0], ms=3, label='2009')
        ax.plot(d26.d, d26.participation_tax_rate, '-^', color=OK[1], ms=3, label='2026')
        tag = ' ✓Δ' if cc in Vd else ''
        ax.set_title(f'{NAMES[cc]}{tag}', fontsize=11)
        ax.set_ylim(-10, 110); ax.set_xticks([1, 4, 7, 10])
    for j in range(len(ORDER), len(axes)):
        axes[j].axis('off')
    axes[0].legend(fontsize=9, loc='lower left')
    for k in [12, 13]:
        axes[k].set_xlabel('earnings decile')
    for k in [0, 4, 8, 12]:
        axes[k].set_ylabel('PTR (%)')
    fig.suptitle('Participation tax rate by earnings decile: 1998 (paper) vs 2009 and 2026 rules\n'
                 '(employment-weighted over family types; V4/q=0 regime; "✓Δ" = change-validated at gate 3b)',
                 fontsize=12, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(f'{RES}/fig1_decile_ptr_ladder.png', facecolor='white')
    plt.close(fig)
    print("fig1 done")


def EM2WB_INV(cc):
    return {v: k for k, v in fi.WB2EM.items()}[cc]


def fig2():
    fig, ax = plt.subplots(figsize=(11, 7))
    for i, cc in enumerate(ORDER):
        d = WBY[WBY.c == cc].sort_values('t')
        hl = cc in Vd
        ax.plot(d.t, d.a_bottom_quintile, '-' if hl else '--',
                color=OK[i % len(OK)], lw=2.2 if hl else 1.1, alpha=1 if hl else 0.55,
                marker='o' if hl else None, ms=3,
                label=f'{cc}{" ✓Δ" if hl else ""}')
        # 1998 marker
        wb = EM2WB_INV(cc)
        p = PAPER[PAPER.country == wb].sort_values('decile')
        a12_1998 = p[p.decile <= 2]['participation_tax_rate'].mean()
        ax.plot(2007, a12_1998, 'o', color=OK[i % len(OK)], ms=6, mec='k', mew=0.5)
    ax.axvspan(2006.3, 2008.0, color='gray', alpha=0.08)
    ax.text(2007.1, 103, '1998\n(paper)', fontsize=8, color='gray', ha='center')
    ax.set_xlabel('policy year'); ax.set_ylabel('bottom-quintile PTR (%)')
    ax.set_title('Bottom-quintile participation tax rate, 1998 (paper marker) and 2009–2026 rules\n'
                 'solid = change-validated (gate 3b, VΔ); dashed = level-shown only', fontsize=12)
    ax.legend(ncol=2, fontsize=8, loc='lower right')
    ax.set_ylim(0, 108)
    fig.tight_layout()
    fig.savefig(f'{RES}/fig2_bottom_quintile_trajectory.png', facecolor='white')
    plt.close(fig)
    print("fig2 done")


def fig3():
    fig, ax = plt.subplots(figsize=(8.5, 7))
    d = WBY[(WBY.t == 2026) & (WBY.Psi_w_stab == 'stable') & (WBY.Psi_d_stab == 'stable')].copy()
    d = d.dropna(subset=['Psi_w', 'Psi_d'])
    ax.plot([0.05, 20], [0.05, 20], '--', color='gray', lw=1, label='Ψ_w = Ψ_d')
    for _, r in d.iterrows():
        col = OK[1] if r.Psi_w < r.Psi_d else OK[3]
        ax.scatter(r.Psi_d, r.Psi_w, color=col, s=70, zorder=5, edgecolor='k', lw=0.4)
        ax.annotate(r.c, (r.Psi_d, r.Psi_w), textcoords='offset points',
                    xytext=(5, 4), fontsize=10)
    ax.axhline(1, color=OK[0], lw=1, ls=':', label='Ψ_w = 1 (as cheap as demogrant benchmark)')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Ψ_d  (demogrant equity–efficiency cost)')
    ax.set_ylabel('Ψ_w  (working-poor transfer cost)')
    ax.set_title('2026 equity–efficiency trade-off: working-poor transfer vs demogrant\n'
                 f'(stable Ψ countries, V4/q=0; {int((d.Psi_w<d.Psi_d).sum())} of {len(d)} below the 45° line → '
                 'in-work transfer cheaper)', fontsize=11)
    ax.legend(fontsize=9, loc='upper left')
    fig.tight_layout()
    fig.savefig(f'{RES}/fig3_welfare_ranking_2026.png', facecolor='white')
    plt.close(fig)
    print("fig3 done")


if __name__ == '__main__':
    fig1(); fig2(); fig3()
