#!/usr/bin/env python3
"""Write card_corrections.csv (old claim -> corrected claim -> reason) and figures.
Pulls the re-cut numbers from recut_values.json (which now reflects the NL gate-3 PASS)."""
import csv, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("/workspace/eval/followup/004-gate-conformance/results")
rc = json.load(open(OUT/"recut_values.json"))
V = rc["validated_set_V"]; Vd = rc["V_delta"]
Vstr = ", ".join(V)
med_Vd = rc["bottom_quintile_PTR_change"]["median_over_Vdelta_pp"]
med_dkfr = rc["bottom_quintile_PTR_change"]["median_over_DK_FR_only_pp"]
e3 = rc["E3_over_V_2026_V4"]
nV = len(V)

rows = [
 ("source","old_claim","corrected_claim","reason"),
 ("001 card headline / metric 1",
  "in-work transfer beats demogrant (Psi_w<Psi_d) in 8 of 10 countries (as the headline result)",
  f"OECD level-validated in only {nV} of 14 countries ({Vstr}); the '8 of 10' is a descriptive, OECD-unvalidated statistic over a post-hoc Psi-stable set. Validated-set version (2026, V4): {e3['Psi_w_lt_Psi_d']} ({'; '.join([', '.join(e3['Psi_w_lt_Psi_d_ccs'])+' only']+['Psi undefined for '+', '.join(e3['undefined_in_V'])])}).",
  "Spec gate-3 no-UB gives V={DK,FR} + NL (NL gate-3 completion this study PASSED); |V|<10 still triggers the honest-partial rule (spec sec4 rule2): headline must be 'validated in n of 14' and E3 counts must not be presented as the finding. Audit sec2, sec7 item1; NL completion gate3_NL_completion.csv."),
 ("001 card metric 1 baseline",
  "baseline '14 of 14' (1998 paper, mixed-q)",
  f"same-set 1998 no-UB (Table 5b) over V={{{Vstr}}}: {e3['baseline_1998_noUB_Psi_w_lt_Psi_d']}; descriptive stable-10 vs 1998 mixed-q (table2a): 10 of 10",
  "Spec sec4 rule1 (same-set) and rule3 (same q-regime): under a V4 headline the 1998 baseline must be Table 5(b), restricted to the compared set. Audit sec7 item5."),
 ("001 card metric 2 (PTR change)",
  "median bottom-quintile PTR change -3.2 pp over V_delta={DK,FI,FR,LU,NL,SE}",
  f"median {med_Vd} pp over spec-conformant V_delta={{{', '.join(Vd)}}}; {{DK,FR}}-only two-country median {med_dkfr} pp retained as DK-beta-dominated sensitivity; all-14 figure -1.2 pp shown only as a labelled UNVALIDATED panel; -3.2 pp dropped",
  "Spec: V_delta must be subset of V; FI,LU,SE failed the level gate and are dropped. NL is now in V (gate-3 PASS), so V_delta={DK,FR,NL}. Audit sec2 (gate3b), sec3, sec7 item3."),
 ("001 card metric 4 (Spain rise)",
  "'Largest bottom-quintile PTR rise (Spain) +42.7 pp'; Italy +40, headline leads with Spain & Italy",
  "metric removed; ES & IT are CONTRADICTED BY THE OECD CHANGE BENCHMARK (ES AW67 +34.7 vs TaxBEN +9.8; IT +22.9 vs -7.4, opposite sign) and are excluded from the PTR-change metric",
  "Spec gate-3b: failers are dropped from E5 and the card PTR-change metric. ES & IT fail 3b and also fail gate-3 levels badly (0.21/0.09). Audit sec3, sec7 item2."),
 ("001 card metric 3 (Denmark)",
  "Denmark -24.3 pp, attributed to '2020s employment-deduction increases'",
  "Denmark -24.3 pp, of which -18.0 pp is the single 2025->2026 beta-rules step (79.85->61.83); only -6.2 pp is gradual 2009->2025. No gate covers the 2026 beta step.",
  "welfare_by_year.csv DK a_bottom_quintile; gate 4 checks 2025 not 2026, gate 3b DK covers 2010-2024 AW67. Audit sec3, sec7 item4."),
 ("001 card metric 5 / findings Psi_w<1 list",
  "Psi_w<1 in 2026: 'DE, EL, PT and BE' (findings) / '4 of 10 stable' vs baseline '5 of 15'",
  "Psi_w<1 list corrected to {BE, DE, LU, PT} (EL=1.22 is not <1; LU=-0.00 is <1 and was omitted); same-set 1998 baseline (stable-10, mixed-q) is 3 of 10 (FR,IE,PT), not 5 of 15",
  "welfare_by_year.csv 2026; '5 of 15' is the paper's 15-country statement, forbidden as a comparison (spec sec4 rule1/2). Audit sec3, sec7 items5,7."),
 ("001 card table (trade-off, 2026)",
  "10-row 'stable' table that includes DK and ES (both Psi-UNSTABLE) and omits EL and LU (both stable)",
  "table re-cut to the actual Psi-stable set (adds EL, LU); DK and ES shown separately flagged 'Psi unstable' (DK with the beta-step note, ES 'contradicted by OECD change')",
  "welfare_by_year.csv 2026 stability flags. Audit sec3 (mislabelled table)."),
 ("001 card gate table / gate 2",
  "'1-2 Formula anchor (Table 2a) PASS exact'",
  "Gate 2 (plumbing anchor) NOT RUN as specced: the 1998 tau/a arrays were never pushed through the new aggregation path (welfare_layer/aggregate, which adds a consumption adj, q-combination and 0.999 clip); the PASS was gate 1 re-run after the A2 fix",
  "Audit sec2 (gate table), sec7 item6."),
 ("001 card gate table / gate 3c",
  "'3c MTR / tau vs add-on PASS 12/14 (median <=0.55 pp)' with no flag",
  "3c PASS 12/14; FR and EL MTR add-on RE-RUN this study and aborted again both years -> tau UNVALIDATED for FR, EL, flagged wherever their MTR/tau-based numbers appear",
  "gate3c_FR_EL_completion.csv (header only; both aborted). Audit sec2 (gate 3c); spec sec6 gate 3c flag rule. Audit sec7 item6."),
 ("001 card gate table / NL gate 3",
  "(NL silently absent; '3 Levels PASS DK, FR')",
  "NL gate-3 completion RE-RUN this study: no-UB leg PASS (within-5pp 0.92, 0 MINW/S_C2 off>10) -> NL ENTERS V. V = {DK, FR, NL}, |V|=3.",
  "gate3_NL_completion.csv. Audit sec2 (gate 3: 'NL: no rows at all ... not disclosed anywhere'), sec7 item6."),
 ("001 card / summary compute",
  "'0.7 core-h'",
  "0.22 core-h (prior studies' logged figure) + ~0.1 core-h for this study's NL gate-3 and FR/EL gate-3c retries",
  "compute_log.csv; the 0.7 figure is not traceable. Audit sec2 (budget), sec3, sec7 item7."),
 ("003 card notes / findings",
  "'validated set V = 14 countries' and 'no tau-unvalidated country (gate-3c medians <=0.55pp)'",
  f"V = {{{Vstr}}} (|V|={nV}, honest partial); FR and EL are tau-UNVALIDATED (gate-3c aborted, confirmed on retry). The frontier panel {{FI,FR,EL,IT,SE}} contains 4 level-gate failers (only FR is in V); EL/IT are gross-basis; FR/EL have no gate-3c result.",
  "Audit sec2 (gate 3, 3c), sec3 (003 frontier panel), sec7 item6. Corrected in findings addendum."),
]
with open(OUT/"card_corrections.csv","w",newline="") as f:
    csv.writer(f).writerows(rows)
print(f"card_corrections.csv: {len(rows)-1} corrections; V={V}; med_Vd={med_Vd}")

# ================= FIGURES =================
OKABE_ITO = ["#0072B2","#E69F00","#009E73","#D55E00","#CC79A7","#56B4E9","#F0E442","#000000"]
plt.rcParams.update({
    "figure.figsize": (7.5,4.5), "figure.dpi":150, "savefig.dpi":150, "savefig.bbox":"tight",
    "font.size":12,"axes.titlesize":13,"axes.labelsize":12,
    "axes.spines.top":False,"axes.spines.right":False,
    "axes.grid":True,"grid.alpha":0.25,
    "axes.prop_cycle": plt.cycler(color=OKABE_ITO)})

# ---- Fig 1: bottom-quintile PTR change, ours vs OECD, gate-3b status ----
g3b = list(csv.DictReader(open("/workspace/eval/followup/001-living-update/results/gate3b_change.csv")))
aw = [r for r in g3b if r["income_curr"]=="AW67" and r["d_ours"] and r["d_taxben"]]
Vdset = set(Vd)
data=[]
for r in aw:
    data.append((r["c"], float(r["d_ours"]), float(r["d_taxben"]),
                 r["passed"]=="True", r["c"] in Vdset))
data.sort(key=lambda x:x[1])
labels=[d[0] for d in data]; ours=[d[1] for d in data]; oecd=[d[2] for d in data]
x=np.arange(len(labels)); wdt=0.4
fig,ax=plt.subplots(figsize=(8.5,4.6))
cols=[]
for d in data:
    if d[0] in ("ES","IT"): cols.append("#D55E00")
    elif d[4]: cols.append("#009E73")
    else: cols.append("#BBBBBB")
ax.bar(x-wdt/2, ours, wdt, color=cols)
ax.bar(x+wdt/2, oecd, wdt, color="#0072B2", alpha=0.85)
ax.axhline(0,color="k",lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("bottom-quintile PTR change\n2010->2025 (DK/NL ->2024), AW67 (pp)")
ax.set_title("Only DK, FR, NL pass the OECD change gate; ES & IT are contradicted")
for i,d in enumerate(data):
    if d[0] in ("ES","IT"):
        ax.annotate("contradicted", (x[i]-wdt/2, d[1]), textcoords="offset points",
                    xytext=(0,4), ha="center", fontsize=8, color="#D55E00")
from matplotlib.patches import Patch
leg=[Patch(color="#009E73",label=f"validated change (V_Δ = {', '.join(Vd)})"),
     Patch(color="#D55E00",label="contradicted by OECD (ES, IT)"),
     Patch(color="#BBBBBB",label="not level-validated / fails 3b"),
     Patch(color="#0072B2",label="OECD TaxBEN benchmark")]
ax.legend(handles=leg, fontsize=8.5, loc="upper left", framealpha=0.9)
fig.savefig(OUT/"fig1_gate3b_change_validation.png", facecolor="white")
plt.close(fig); print("fig1 written")

# ---- Fig 2: 'in-work beats demogrant' 1998 vs 2026, two cuts ----
def kn(s): a,_,b=s.split(); return int(a), int(b.split()[-1]) if False else (int(a), int(s.split()[-1]))
n_wltd_V = int(e3["Psi_w_lt_Psi_d"].split()[0]); n_V = len(V)
n_base_V = int(e3["baseline_1998_noUB_Psi_w_lt_Psi_d"].split()[0])
fig,ax=plt.subplots(figsize=(8.2,4.6))
groups=[f"Validated set V = {{{Vstr}}}\n[OECD-validated, spec headline]",
        "Descriptive Psi-stable (10)\n[UNVALIDATED]"]
b98=[n_base_V/n_V, 10/10]; b26=[n_wltd_V/n_V, 8/10]
lab98=[f"{n_base_V} of {n_V}","10 of 10"]; lab26=[f"{n_wltd_V} of {n_V}","8 of 10"]
x=np.arange(2); w=0.35
ax.bar(x-w/2, b98, w, color="#0072B2", label="1998 baseline (same set, same q-regime)")
ax.bar(x+w/2, b26, w, color="#E69F00", label="2026 (V4 rules, this study)")
for i in range(2):
    ax.text(x[i]-w/2, b98[i]+0.02, lab98[i], ha="center", fontsize=11, fontweight="bold")
    ax.text(x[i]+w/2, b26[i]+0.02, lab26[i], ha="center", fontsize=11, fontweight="bold")
ax.set_ylim(0,1.15); ax.set_ylabel("share with Psi_w < Psi_d")
ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=9.5)
ax.set_title("'In-work transfer beats demogrant': validated vs descriptive cut")
ax.axhline(1.0,color="k",lw=0.6,ls=":")
ax.legend(fontsize=9, loc="lower center")
fig.text(0.5,-0.03,"1998 baselines: Table 5(b) no-UB for V (DK & NL Psi undefined in 2026); table2a mixed-q for the descriptive set.",
         ha="center",fontsize=8.3,style="italic")
fig.savefig(OUT/"fig2_headline_by_cut.png", facecolor="white")
plt.close(fig); print("fig2 written")
