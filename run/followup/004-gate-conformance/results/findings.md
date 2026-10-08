# Findings — 004-gate-conformance (corrective study)

## What was corrected, and why

This study is an **artifact-level correction** of the living-update follow-ups
(`001-living-update`, `002-living-update-cont`, `003-theory-update`). Those studies computed
the underlying rates correctly — the provenance audit
(`gate-conformance-inputs/immervoll-provenance.md`) found **data provenance CLEAN, memory
CLEAN, and gates 0/1/4 and the continuation handling CLEAN** — but their **reporting layer
violated the spec's own validation rules** (`spec-living-update.md` §4, §6). This card
supersedes theirs for publication; the old studies stay on disk untouched.

The authoritative defect list is the audit **§4–§5 and §7**. In one line: the cards presented
an **OECD-unvalidated** "8 of 10" ranking result as the headline, over a post-hoc Ψ-stable set,
with a cross-regime 1998 baseline ("14 of 14", "5 of 15"), a change metric built over a set
that includes four level-gate failers, and a Spain/Italy "+40 pp" story that the OECD change
benchmark **contradicts**. The spec required the headline to be an **honest partial** keyed to
the gate-3 validated set V, with same-set / same-q-regime 1998 baselines.

No new EUROMOD simulations were run except the three gate completions the instruction allows
(§2). All result CSVs from 001/002/003 were treated as correct computations; the job here is
the honest aggregation and presentation.

## Gate completions run in this study (instruction §2)

| § | Completion | Outcome | Consequence |
|---|---|---|---|
| 2.1 | **NL gate-3 levels** (original run died on a tool timeout; never redone) — re-run with the identical household code from 001's workspace, EUROMOD J2.54+ | **PASS**: no-UB leg n=48, within-5pp share **0.92** (≥0.75), **0** MINW/S_C2 cells off by >10 pp. (UB leg FAILs, moot under V4.) | **NL enters the validated set.** V = **{DK, FR, NL}**, \|V\| = 3. |
| 2.2 | **FR & EL MTR add-on (gate 3c)** — retry once | **FAIL (both)**: all four simulations (FR/EL × 2010/2025) aborted with `… aborted with errors`, identical to the original failure. | FR and EL remain **τ unvalidated**; flagged wherever their MTR/τ numbers appear. |
| 2.3 | **Transcribe paper Table 5(b)** (no-UB 1998 rates) | **DONE**, double-read at 200 dpi from `paper.pdf` p.31 | `results/baseline_1998_noUB.csv` — the same-definition (V4) 1998 baseline. |

Artifacts: `gate3_NL_completion.csv`, `gate3c_FR_EL_completion.csv` (header only, both aborted),
`baseline_1998_noUB.csv`, `gate_completions.json`.

## The gate-conformant cut (instruction §3)

### Validated set and the honest-partial rule
- **V = {DK, FR, NL}** (gate-3 no-UB passers; NL added by §2.1). \|V\| = 3 < 10, so the spec's
  minimum-coverage rule (§4 rule 2) applies: the headline is **"OECD-validated in 3 of 14"**,
  and E3 counts are **not** compared with the paper's 15-country statements anywhere. All-14
  numbers appear only in a clearly labelled **"unvalidated levels"** panel.
- **V_Δ = {DK, FR, NL}** (gate-3b passers ⊆ V).

### Headline estimand E3 (2026, V4), over V, with the Table 5(b) baseline
- **Ψ_w < Ψ_d: 1 of 3** — France only; **Denmark and the Netherlands have numerically
  undefined Ψ in 2026** (bottom-decile participation traps push rates to ≈1, where the paper's
  closed form divides by 1−rate). Same-set **1998 no-UB baseline (Table 5b): 3 of 3**.
- **Ψ_w < 1: 0 of 3** well-defined (FR = 2.14). 1998 no-UB baseline: **1 of 3** (DK, Ψ_w 0.36).

### Bottom-quintile PTR change (E5), over V_Δ
- **Median 2009→2026 = −5.2 pp** over V_Δ = {DK, FR, NL} (DK −24.3, FR −5.2, NL −0.2).
- The **{DK, FR}-only** two-country median is **−14.7 pp**, retained as a DK-beta-dominated
  sensitivity (this was the instruction's provisional figure, which assumed NL would fail §2.1).
- **All-14 median = −1.2 pp**, shown only as a labelled **unvalidated** panel. The old
  **−3.2 pp** figure (over the non-conforming V_Δ = {DK,FI,FR,LU,NL,SE}) is **dropped**.
- **ES and IT are removed** from the PTR-change metric: the OECD change benchmark
  **contradicts** them — ES AW67 ours **+34.7** vs TaxBEN **+9.8**; IT **+22.9** vs **−7.4**
  (opposite sign). They fail gate 3b and fail gate-3 levels badly (0.21 / 0.09).

### Denmark's fall, attributed correctly
- Denmark −24.3 pp (2009 86.1 → 2026 61.8), **of which −18.0 pp is the single 2025→2026
  beta-rules step** (79.85 → 61.83). Only −6.2 pp is the gradual 2009→2025 move. **No gate
  covers the 2026 beta step**: gate 4 checks 2025, and DK's gate 3b covers 2010→2024 AW67.
  The old card's "2020s employment-deduction increases" attribution is replaced accordingly.

### Same-set 1998 baselines
- Descriptive Ψ-stable-10 vs 1998 **mixed-q** (`table2a.csv`): Ψ_w < Ψ_d **10 of 10**;
  Ψ_w < 1 **3 of 10** (FR, IE, PT). Validated V vs 1998 **no-UB** (Table 5b): as above.
- The old "14 of 14" and "5 of 15" baselines (cross-set and cross-regime, and the paper's
  own 15-country statements) are retired per §4 rules 1–3.

### Small-error fixes (§3 item 7)
- **Ψ_w < 1 (2026) list corrected to {BE, DE, LU, PT}** — the old findings said "DE, EL, PT
  and BE" (EL = 1.22 is **not** < 1; LU = −0.00 **is** < 1 and was omitted).
- **Trade-off card table re-cut** to the actual Ψ-stable set (adds **EL, LU**); **DK** and **ES**
  are shown separately, flagged Ψ-unstable (DK with the beta-step note, ES "contradicted").
- **Core-hours corrected to 0.22** (the prior studies' logged figure; the "0.7" was
  untraceable) plus ~0.1 core-h for this study's three gate completions.

## The headline conclusion, re-stated honestly (instruction §3 last item)

**Does "Ψ_w < Ψ_d in 8 of 10 Ψ-stable countries" survive?** As a **descriptive,
OECD-unvalidated** statistic, yes — it is arithmetically correct over the post-hoc Ψ-stable
set (Ireland and Sweden flip to the demogrant), and the same-set 1998 figure is 10 of 10. But
it is **not an OECD-validated finding**: the Ψ-stable-10 contains six countries that fail the
gate-3 level test, and it **excludes Denmark and the Netherlands**, two of the only three
level-validated countries. So the "8 of 10" belongs in a labelled *unvalidated* panel, never
as the headline.

**The validated-set version of the claim** (over V = {DK, FR, NL}, 2026, V4) is **1 of 3** —
and that one is **France alone**. Denmark and the Netherlands do not contradict the paper; their
Ψ is **numerically undefined** in 2026 because bottom-decile participation tax rates have risen
to ≈100% (genuine inactivity traps the paper's 1998 survey averages never reached). The
same-set 1998 no-UB baseline (Table 5b) had all three at Ψ_w < Ψ_d (3 of 3). So the honest
reading is: **the paper's qualitative result is neither confirmed nor overturned on the
validated set — it survives where Ψ is computable (France) and becomes undefined where the new
bottom-decile traps appear (Denmark, Netherlands).** That instability is itself the finding.
We neither soften it ("still holds 8 of 10") nor inflate it ("the result collapses").

## Deviations

1. **V expanded to 3 (not the provisionally-expected 2).** Because the NL gate-3 completion
   (§2.1) **passed**, V and V_Δ are {DK, FR, NL}, not {DK, FR}. The conformant E5 median is
   therefore **−5.2 pp**, not the instruction's provisional **−14.7 pp** (which assumed NL
   would fail). Both are reported, labelled.
2. **FR/EL gate-3c could not be completed** — the MTR add-on aborts for these two countries on
   retry, exactly as before. They stay τ-unvalidated (the instruction's stated fallback).
3. **Tooling install.** The EUROMOD connector (euromod 0.4.0, pythonnet) and the .NET 8.0.31
   runtime had to be installed in this fresh container to run the three gate completions. This
   is tooling only — **no data was fetched** (the EUROMOD zip and all benchmarks were already
   staged locally), so rule 5's data-provenance intent is preserved. Only the paper PDF and
   staged files were read for data.
