#!/usr/bin/env python3
"""005-presentation-fixes: close the six presentation items from the audit re-check.
Pure assembly from existing CSVs (NO EUROMOD runs, NO recomputation except item-1's table,
which is assembled from 001's welfare_by_year.csv). Produces:
  - results/tradeoff_table_corrected.csv   (item 1)
  - results/card_corrections.csv           (item 2: 004 rows + new 002/003 rows)
  - results/fig1_gate3b_change_validation.png (items 3,4: relabel + PT contradicted)
  - copies fig2_headline_by_cut.png into 005/results (card self-containment)
"""
import csv, json, shutil
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R001 = Path("/workspace/eval/followup/001-living-update/results")
R004 = Path("/workspace/eval/followup/004-gate-conformance/results")
OUT  = Path("/workspace/eval/followup/005-presentation-fixes/results")
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(p):
    with open(p) as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))

def fnum(x):
    try: return float(x)
    except: return None

# ======================================================================
# ITEM 1 — corrected trade-off table, all 14 countries, from welfare_by_year.csv (2026, V4)
# ======================================================================
wby = read_csv(R001/"welfare_by_year.csv")
w2026 = [r for r in wby if r["t"] == "2026"]          # file order: AT BE DK FI FR DE EL IE IT LU NL PT ES SE

def fmt(v):
    f = fnum(v)
    return "undefined" if f is None else f"{f:.4g}"

rows = []
n_stable = n_wltd = n_wlt1 = 0
for r in w2026:
    c = r["c"]
    pd_, pw = fnum(r["Psi_d"]), fnum(r["Psi_w_V4"])
    stab = (r["Psi_d_stab"] == "stable" and r["Psi_w_V4_stab"] == "stable")
    if stab:
        n_stable += 1
        wltd = "yes" if pw < pd_ else "no"
        wlt1 = "yes" if pw < 1 else "no"
        if wltd == "yes": n_wltd += 1
        if wlt1 == "yes": n_wlt1 += 1
    else:
        wltd = wlt1 = "n/a (unstable)"
    note = ""
    if c == "DK":
        note = ("beta-step-dependent: of the -24.3 pp 2009->2026 bottom-quintile PTR fall, "
                "-18.0 pp is the single 2025->2026 J2.54+ beta step, covered by no gate; Psi undefined in 2026")
    elif c == "ES":
        note = ("contradicted by the OECD change benchmark (gate 3b: ours +34.7 vs TaxBEN +9.8 at AW67; "
                "+46.6 vs -1.1 at MINW); fails gate-3 levels badly (0.21); Psi undefined in 2026")
    elif not stab:
        note = "Psi unstable in 2026 (bottom-decile PTR/MTR ~=100% participation trap)"
    rows.append([c, "V4", fmt(r["Psi_d"]), fmt(r["Psi_w_V4"]),
                 wltd, wlt1, "stable" if stab else "unstable", note])

hdr_comment = (
    "# Corrected equity-efficiency trade-off table, 2026 (V4, q=0). Source: "
    "followup/001-living-update/results/welfare_by_year.csv (byte-identical in 002-living-update-cont). "
    "All 14 countries incl. EL and LU. Psi_w<Psi_d counted only where Psi is stable. "
    f"Among the {n_stable} Psi-stable countries: Psi_w<Psi_d in {n_wltd}, Psi_w<1 in {n_wlt1}. "
    "DK flagged beta-step-dependent; ES flagged OECD-contradicted. Assembled, not recomputed, by 005.\n")
with open(OUT/"tradeoff_table_corrected.csv", "w", newline="") as f:
    f.write(hdr_comment)
    w = csv.writer(f)
    w.writerow(["country","regime","Psi_d_2026","Psi_w_V4_2026",
                "Psi_w_lt_Psi_d","Psi_w_lt_1","Psi_stable","note"])
    w.writerows(rows)
print(f"[item1] tradeoff_table_corrected.csv: 14 rows; stable={n_stable} wltd={n_wltd} wlt1={n_wlt1}")

# ======================================================================
# ITEM 2 — complete card_corrections.csv: keep 004 rows, update compute row to 0.48,
#          add explicit rows for the 002 card and the 003 card.
# ======================================================================
cc = read_csv(R004/"card_corrections.csv")   # existing 12 rows (DictReader -> dicts)
# item 6: the corrected compute figure is 0.48 core-h (001+002 combined), not 0.22
for r in cc:
    if r["source"] == "001 card / summary compute":
        r["corrected_claim"] = ("0.48 core-h = 001+002 combined (001 0.22 logged + 002 0.30; "
            "002 card '0.30 / 0.48'); the '0.7' is untraceable. 004's gate completions added ~0.1; "
            "005 (assembly only) adds negligible compute")
        r["reason"] = ("compute_log.csv; 002 card metric 'Compute used ... 0.30 / 0.48 core-hours'. "
            "The 0.22 is 001 alone, not the whole living-update. Audit sec2 (budget), sec3, sec7 item7.")

new_rows = [
 # ---- 002 card ----
 {"source":"002 card headline / metric 1",
  "old_claim":"\"Psi_w < Psi_d holds for 8 of 10 stable countries in 2026\" as the headline result; baseline \"14 of 14\" (paper/table2a)",
  "corrected_claim":"same defect as the 001 card: '8 of 10' is a descriptive, OECD-unvalidated statistic over a post-hoc Psi-stable set; OECD level-validated in only 3 of 14 (DK, FR, NL), validated-set version 1 of 3 (FR; DK & NL Psi undefined). Same-set 1998 baselines: stable-10 vs mixed-q 10 of 10; V vs no-UB Table 5(b) 3 of 3 (NOT the cross-regime 14 of 14).",
  "reason":"Spec sec4 rules 1-3 and the |V|<10 honest-partial rule (rule 2). Audit sec2 (gate 3), sec3 ('8 of 10' row), sec7 items 1,5."},
 {"source":"002 card metric 3 (PTR change) value",
  "old_claim":"\"median bottom-quintile PTR change 2009->2026 = -3.24 pp (V_Delta)\"",
  "corrected_claim":"-3.2 pp is computed over the non-conforming V_Delta={DK,FI,FR,LU,NL,SE} and is DROPPED; the spec-conformant median over V_Delta={DK,FR,NL} is -5.2 pp ({DK,FR}-only -14.7 pp sensitivity); the all-14 figure -1.2 pp is a labelled UNVALIDATED panel only",
  "reason":"Spec: V_Delta must be a subset of V. FI, LU, SE failed the gate-3 level test. Audit sec2 (gate 3b), sec3 ('median -3.2 pp' row), sec7 item 3."},
 {"source":"002 card metric 3 (PTR change) note",
  "old_claim":"\"Denmark -24.3 pp ... change-validated at gate 3b\" (also fig2 caption 'solid = change-validated (gate 3b)')",
  "corrected_claim":"Denmark is NOT change-validated for its headline fall: DK's gate 3b covers only 2010->2024 at AW67, whereas -18.0 pp of the -24.3 pp fall is the single 2025->2026 J2.54+ beta step, which no gate covers (gate 4 checks 2025). Only -6.2 pp (2009->2025) is gate-adjacent.",
  "reason":"welfare_by_year.csv DK a_bottom_quintile (79.85->61.83 at the beta step); gate3b_change.csv DK row (y0=2010,y1=2024). Audit sec3 (Denmark row), sec7 item 4."},
 {"source":"002 card table 2 (V_Delta set) rows",
  "old_claim":"\"change-validated set V_Delta\" table lists Denmark, France, Sweden, Finland, Netherlands, Luxembourg (i.e. includes FI, LU, SE)",
  "corrected_claim":"FI, LU and SE are NOT in the spec-conformant V_Delta (V_Delta must be a subset of the level-validated V={DK,FR,NL}); FI/LU/SE failed the gate-3 level test, so they cannot be presented as change-validated. The conformant V_Delta table is DK, FR, NL only.",
  "reason":"Spec gate-3b subset rule; gate-3 level outcomes (FI 0.75 but 13.0pp off, LU 0.75 but 35.1pp off, SE 0.25 fail). Audit sec2 (gate 3, 3b), sec3, sec7 item 3."},
 # ---- 003 card ----
 {"source":"003 card metric 2 / table 1 (\"/14\" denominators)",
  "old_claim":"\"0/14 Kleven, 5/14 Bartels&Shupe, 9/14 Chetty (2026)\" and the whole by-era survival table stated as k / 14",
  "corrected_claim":"the denominator 14 is NOT the validated set V (V={DK,FR,NL}, |V|=3), and the counts include Psi-unstable country-years (e.g. NL 2009 is Psi-unstable yet counted as surviving). The survival counts are descriptive statistics over 14 unvalidated levels; they must be labelled unvalidated and not compared with the paper's '14 of 14 for a wide range' (C12), which the same-set rule forbids.",
  "reason":"frontier_survival.csv sums; audit sec3 (003 '/14' row: 'Denominator 14 is not V. Unstable country-years are counted'). Audit sec2 (gate 3), sec7 item 6."},
 {"source":"003 card headline / metric 1 (\"0.22 -> 0.13\")",
  "old_claim":"\"critical elasticity fell 0.22 -> 0.13\" presented as a strengthening of the paper's result over a 'level-validated V = 14' panel",
  "corrected_claim":"0.22->0.13 traces (frontier_by_era.csv median over panel {FI,FR,EL,IT,SE}) but the panel is POST-HOC and level-UNVALIDATED: 4 of its 5 members (FI, EL, IT, SE) failed the gate-3 level test, EL/IT are gross-basis, and FR/EL have no gate-3c result; only FR is in V. The headline stands only as a DESCRIPTIVE statistic, not an OECD-validated finding. 003's statement that the panel is drawn from a 'level-validated V = 14' is false.",
  "reason":"frontier_by_era.csv; audit sec3 (003 '0.22->0.13' row), sec2 (gate 3/3c), sec7 item 6. Also corrected in 004 findings_addendum_003.md."},
]
fieldnames = ["source","old_claim","corrected_claim","reason"]
with open(OUT/"card_corrections.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in cc:
        w.writerow({k: r[k] for k in fieldnames})
    for r in new_rows:
        w.writerow(r)
print(f"[item2] card_corrections.csv: {len(cc)} carried + {len(new_rows)} new = {len(cc)+len(new_rows)} rows")

# ======================================================================
# ITEMS 3 & 4 — re-render Fig 1 with corrected y-axis/caption (single adult at 67% AW,
#               gate-3b change) and PT marked contradicted like ES and IT.
# ======================================================================
OKABE_ITO = ["#0072B2","#E69F00","#009E73","#D55E00","#CC79A7","#56B4E9","#F0E442","#000000"]
plt.rcParams.update({
    "figure.figsize": (7.5,4.5), "figure.dpi":150, "savefig.dpi":150, "savefig.bbox":"tight",
    "font.size":12,"axes.titlesize":13,"axes.labelsize":12,
    "axes.spines.top":False,"axes.spines.right":False,
    "axes.grid":True,"grid.alpha":0.25,
    "axes.prop_cycle": plt.cycler(color=OKABE_ITO)})

g3b = read_csv(R001/"gate3b_change.csv")
aw = [r for r in g3b if r["income_curr"]=="AW67" and r["d_ours"] and r["d_taxben"]]
Vd = ["DK","FR","NL"]
Vdset = set(Vd)
CONTRADICTED = {"ES","IT","PT"}   # item 4: PT joins ES & IT (opposite OECD sign at BOTH levels)
data=[]
for r in aw:
    data.append((r["c"], float(r["d_ours"]), float(r["d_taxben"]),
                 r["passed"]=="True", r["c"] in Vdset))
data.sort(key=lambda x:x[1])
labels=[d[0] for d in data]; ours=[d[1] for d in data]; oecd=[d[2] for d in data]
x=np.arange(len(labels)); wdt=0.4
fig,ax=plt.subplots(figsize=(8.5,4.8))
cols=[]
for d in data:
    if d[0] in CONTRADICTED: cols.append("#D55E00")
    elif d[4]: cols.append("#009E73")
    else: cols.append("#BBBBBB")
ax.bar(x-wdt/2, ours, wdt, color=cols)
ax.bar(x+wdt/2, oecd, wdt, color="#0072B2", alpha=0.85)
ax.axhline(0,color="k",lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(labels)
# item 3: y-axis is the gate-3b PTR change for a SINGLE ADULT at 67% AW, not bottom-quintile
ax.set_ylabel("PTR change, single adult at 67% AW\n2010->2025 (DK/NL ->2024), gate 3b (pp)")
ax.set_title("Gate-3b change (single adult, 67% AW): DK, FR, NL pass; ES, IT, PT contradicted")
for i,d in enumerate(data):
    if d[0] in CONTRADICTED:
        ax.annotate("contradicted", (x[i]-wdt/2, d[1]), textcoords="offset points",
                    xytext=(0,4 if d[1]>=0 else -12), ha="center", fontsize=8, color="#D55E00")
from matplotlib.patches import Patch
leg=[Patch(color="#009E73",label=f"validated change (V_delta = {', '.join(Vd)})"),
     Patch(color="#D55E00",label="contradicted by OECD change (ES, IT, PT)"),
     Patch(color="#BBBBBB",label="not level-validated / fails 3b"),
     Patch(color="#0072B2",label="OECD TaxBEN change benchmark")]
ax.legend(handles=leg, fontsize=8.5, loc="upper left", framealpha=0.9)
fig.savefig(OUT/"fig1_gate3b_change_validation.png", facecolor="white")
plt.close(fig)
print("[item3,4] fig1 re-rendered (relabelled; PT contradicted)")

# copy fig2 unchanged so the superseding 005 card is self-contained (not one of the six items)
shutil.copy2(R004/"fig2_headline_by_cut.png", OUT/"fig2_headline_by_cut.png")
print("[card] fig2_headline_by_cut.png copied into 005/results")
