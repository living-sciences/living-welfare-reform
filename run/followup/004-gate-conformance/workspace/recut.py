#!/usr/bin/env python3
"""004-gate-conformance: re-cut the living-update cards to the spec's own gate rules.
Pure aggregation from existing study CSVs (no new EUROMOD runs here). Reads 001/003
result CSVs + the replication table2a.csv + the new Table 5(b) transcription, and writes
the gate-conformant recut values, card_corrections.csv, and figures.
"""
import json, csv, statistics as st
from pathlib import Path

R001 = Path("/workspace/eval/followup/001-living-update/results")
R003 = Path("/workspace/eval/followup/003-theory-update/results")
REPL = Path("/workspace/eval/replication/codebase/results")
OUT  = Path("/workspace/eval/followup/004-gate-conformance/results")
OUT.mkdir(parents=True, exist_ok=True)

def read_csv(p):
    with open(p) as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))

# ---- load inputs ----
wby = read_csv(R001/"welfare_by_year.csv")
g3b = read_csv(R001/"gate3b_change.csv")
hs  = json.load(open(R001/"headline_scalars.json"))
# replication 1998 mixed-q baseline (table2a.csv) with paper code map
t2a = read_csv(REPL/"table2a.csv")
PCODE = {"GE":"DE","GR":"EL","IR":"IE","SP":"ES","SW":"SE"}  # UK excluded from baseline
t2a_map = {}
for r in t2a:
    cc = PCODE.get(r["country"], r["country"])
    t2a_map[cc] = {"Psi_d": float(r["tradeoff_demogrant"]),
                   "Psi_w": float(r["tradeoff_workingpoor"])}
# Table 5(b) no-UB 1998 baseline (my transcription)
t5b = {}
for r in read_csv(OUT/"baseline_1998_noUB.csv"):
    if r["country_code"].startswith("#"): continue
    t5b[r["country_code"]] = {"Psi_d": float(r["Psi_d"]), "Psi_w": float(r["Psi_w"])}

# 2026 welfare values
w2026 = {r["c"]: r for r in wby if r["t"]=="2026"}
def fnum(x):
    try: return float(x)
    except: return None

# ========= 1. Validated sets (spec gate rules) =========
# Gate 3 no-UB level passers. Base = headline_scalars V_level_validated_noUB = {DK, FR}.
# NL gate-3 completion (instruction sec2.1) was re-run in this study and PASSED the no-UB
# leg (within-5pp 0.92, 0 MINW/S_C2 off>10pp -> see gate3_NL_completion.csv), so NL joins V.
V_base = set(hs["V_level_validated_noUB"])        # {DK, FR}
NL_gate3_passed = True                            # from gate3_NL_completion.csv this study
if NL_gate3_passed:
    V_base |= {"NL"}
V = sorted(V_base)                                # {DK, FR, NL}
# Gate 3b passers that are also in V  -> V_delta  (subset rule)
g3b_pass = set()
by_c = {}
for r in g3b:
    by_c.setdefault(r["c"], []).append(r)
for c, rows in by_c.items():
    comps = [r for r in rows if r["passed"] in ("True","False")]
    if comps and all(r["passed"]=="True" for r in comps):
        g3b_pass.add(c)
V_delta = sorted(set(V) & g3b_pass)

# ========= 2. E3 counts over V (2026, V4) with no-UB 1998 baseline =========
def psi_pair(c):
    r = w2026[c]
    pw = fnum(r["Psi_w_V4"]); pd = fnum(r["Psi_d"])
    stab = r["Psi_w_V4_stab"]
    return pw, pd, stab
e3_V = {"wltd":[], "wlt1":[], "undefined":[]}
for c in V:
    pw, pd, stab = psi_pair(c)
    if pw is None or pd is None or stab!="stable":
        e3_V["undefined"].append(c); continue
    if pw < pd: e3_V["wltd"].append(c)
    if pw < 1:  e3_V["wlt1"].append(c)
# 1998 no-UB baseline over V (Table 5b)
base_V_wltd = [c for c in V if t5b[c]["Psi_w"] < t5b[c]["Psi_d"]]
base_V_wlt1 = [c for c in V if t5b[c]["Psi_w"] < 1]

# ========= 3. Descriptive Psi-stable set (2026) + mixed-q 1998 baseline =========
stable10 = hs["E3_2026"]["stable_ccs"]   # BE FI FR DE EL IE IT LU PT SE
desc_wltd, desc_wlt1 = [], []
for c in stable10:
    pw, pd, stab = psi_pair(c)
    if pw < pd: desc_wltd.append(c)
    if pw < 1:  desc_wlt1.append(c)
base10_wltd = [c for c in stable10 if t2a_map[c]["Psi_w"] < t2a_map[c]["Psi_d"]]
base10_wlt1 = [c for c in stable10 if t2a_map[c]["Psi_w"] < 1]

# ========= 4. Bottom-quintile PTR change: V_delta median + panels =========
dmap = {d["c"]: d["d_a12"] for d in hs["E5_bottom_quintile_PTR_change"]}
med_Vdelta = round(st.median([dmap[c] for c in V_delta]), 1)
med_all14  = hs["E5_median_d_a12_allcountries"]   # -1.2
old_bad_median = hs["E5_median_d_a12_over_Vdelta"]  # -3.24 (non-conforming)

# ES/IT contradiction detail from gate3b AW67
def g3b_aw67(c):
    for r in g3b:
        if r["c"]==c and r["income_curr"]=="AW67":
            return float(r["d_ours"]), float(r["d_taxben"])
    return None
es = g3b_aw67("ES"); it = g3b_aw67("IT")

# ========= 5. Denmark decomposition =========
dk = {r["t"]: fnum(r["a_bottom_quintile"]) for r in wby if r["c"]=="DK"}
dk_total = round(dk["2026"]-dk["2009"],2)
dk_beta_step = round(dk["2026"]-dk["2025"],2)     # 2025->2026
dk_pre = round(dk["2025"]-dk["2009"],2)

# ========= assemble =========
recut = {
 "validated_set_V": V, "V_count": len(V), "V_total": 14,
 "V_delta": V_delta,
 "headline_honest_partial": f"OECD level-validated in {len(V)} of 14 (|V|<10 -> honest partial)",
 "E3_over_V_2026_V4": {
    "Psi_w_lt_Psi_d": f"{len(e3_V['wltd'])} of {len(V)}",
    "Psi_w_lt_Psi_d_ccs": e3_V["wltd"],
    "undefined_in_V": e3_V["undefined"],
    "Psi_w_lt_1": f"{len(e3_V['wlt1'])} of {len(V)}",
    "baseline_1998_noUB_Psi_w_lt_Psi_d": f"{len(base_V_wltd)} of {len(V)}",
    "baseline_1998_noUB_Psi_w_lt_1": f"{len(base_V_wlt1)} of {len(V)} ({','.join(base_V_wlt1)})",
 },
 "descriptive_stable10_2026_UNVALIDATED": {
    "set": stable10,
    "Psi_w_lt_Psi_d": f"{len(desc_wltd)} of {len(stable10)}",
    "flips_to_demogrant": [c for c in stable10 if c not in desc_wltd],
    "Psi_w_lt_1": f"{len(desc_wlt1)} of {len(stable10)}",
    "Psi_w_lt_1_ccs": sorted(desc_wlt1),
    "baseline_1998_mixedq_Psi_w_lt_Psi_d": f"{len(base10_wltd)} of {len(stable10)}",
    "baseline_1998_mixedq_Psi_w_lt_1": f"{len(base10_wlt1)} of {len(stable10)} ({','.join(sorted(base10_wlt1))})",
 },
 "bottom_quintile_PTR_change": {
    "median_over_Vdelta_pp": med_Vdelta, "Vdelta": V_delta,
    "unvalidated_all14_median_pp": med_all14,
    "dropped_nonconforming_median_pp": old_bad_median,
    "contradicted_by_OECD": {
       "ES_AW67_ours_vs_taxben": es, "IT_AW67_ours_vs_taxben": it},
 },
 "denmark_decomposition": {
    "a12_2009": dk["2009"], "a12_2025": dk["2025"], "a12_2026": dk["2026"],
    "total_2009_2026_pp": dk_total,
    "beta_step_2025_2026_pp": dk_beta_step,
    "gradual_2009_2025_pp": dk_pre,
    "note": "beta step uncovered by any gate (gate 4 checks 2025, gate 3b DK covers 2010-2024 AW67)"},
 "Psi_w_lt_1_2026_list_corrected": sorted(desc_wlt1),
 "core_hours_corrected": 0.22,
 "tau_unvalidated_countries": ["FR","EL"],
 "gate_completions": {
   "NL_gate3_noUB": "PASS (within-5pp 0.92; 0 MINW/S_C2 off>10) -> NL in V",
   "FR_EL_gate3c_mtr": "FAIL on retry (add-on aborted both years) -> FR, EL tau-unvalidated",
   "table5b": "transcribed to baseline_1998_noUB.csv",
 },
 "note_vs_instruction": ("Instruction sec3 provisionally expected V={DK,FR} and median -14.7pp "
   "over {DK,FR}; because the NL gate-3 completion (sec2.1) PASSED, V and V_delta expand to "
   "{DK,FR,NL} and the conformant median is "+str(med_Vdelta)+" pp. The {DK,FR}-only median "
   "(-14.7 pp, DK-beta-dominated) is retained as a two-country sensitivity."),
}
# two-country {DK,FR} median retained as sensitivity (instruction's provisional figure)
recut["bottom_quintile_PTR_change"]["median_over_DK_FR_only_pp"] = round(
    st.median([dmap["DK"], dmap["FR"]]),1)
json.dump(recut, open(OUT/"recut_values.json","w"), indent=2)
print(json.dumps(recut, indent=2))
