# 004-gate-conformance — re-cutting the living-update cards to the spec's own gate rules

## Question

The living-update follow-ups (`001-living-update`, `002-living-update-cont`,
`003-theory-update`) of Immervoll, Kleven, Kreiner & Saez (EJ 2007) **computed their rates
correctly** — the provenance audit found data, memory, and gates 0/1/4 and the continuation
handling all CLEAN — but their **reporting layer broke the spec's validation rules**
(`spec-living-update.md` §4, §6): they headlined an OECD-unvalidated "8 of 10" ranking result
over a post-hoc Ψ-stable set, paired it with a cross-set / cross-regime 1998 baseline, built
the PTR-change metric over a set containing four level-gate failers, and led with a Spain/Italy
"+40 pp" story the OECD change benchmark contradicts. This study is an **artifact-level
correction**: it re-cuts the cards and findings to the gate-conformant form, running **no new
EUROMOD simulations except the three small gate completions** the instruction allows, and
supersedes the old cards for publication. The authoritative defect list is the audit §4–§5 and
§7, applied against the spec.

## Approach

**Reused from the replication / prior follow-ups (read from disk, treated as correct):**
- `001-living-update/results/`: `welfare_by_year.csv`, `rates_deciles.csv`,
  `headline_scalars.json`, `gate3b_change.csv`, `gate3c_mtr.csv`, `result_card.json`,
  `findings.md`.
- `003-theory-update/results/`: `frontier_by_era.csv`, `frontier_survival.csv`,
  `result_card.json`.
- `replication/codebase/results/table2a.csv` — the 1998 mixed-q baseline (gate-1 anchor).

**New computation (instruction §2):** three gate completions, run in the foreground with the
identical household-construction code copied from 001's workspace (`hh_engine.py`, `gate3.py`,
`gate3c.py`), EUROMOD J2.54+ (beta), euromod 0.4.0, .NET 8.0.31. All outputs written under this
study's `results/`; nothing in the read-only history was modified.

**Re-cut (instruction §3):** a pure-aggregation script (`workspace/recut.py`) recomputes the
validated set V, V_Δ, the E3 counts, the E5 median, the Denmark decomposition, and the same-set
1998 baselines directly from the CSVs above; `workspace/make_corrections.py` writes the
old→corrected claim map and the figures.

## Results

### Gate completions (§2)

| § | Completion | Outcome |
|---|---|---|
| 2.1 | NL gate-3 levels (died on a timeout originally) | **PASS** — no-UB leg n=48, within-5pp **0.92**, **0** MINW/S_C2 off >10 pp → **NL enters V** |
| 2.2 | FR & EL MTR add-on (gate 3c), retry once | **FAIL (both)** — all four runs aborted with errors → FR, EL **τ unvalidated** |
| 2.3 | Transcribe paper Table 5(b) | **DONE** (double-read, p.31) → `baseline_1998_noUB.csv` |

### The gate-conformant cut vs the superseded cards

| Quantity | Old card (001/003) | Corrected (this study) | Source of the old value |
|---|---|---|---|
| Validated set V | `all 14` (hard-coded) | **{DK, FR, NL}**, \|V\|=3 → honest partial "3 of 14" | `headline_scalars.json validated_set`; NL from `gate3_NL_completion.csv` |
| Ψ_w<Ψ_d headline (2026) | "8 of 10" (as the finding) | **1 of 3** over V (FR; DK & NL Ψ undefined); 8 of 10 only as a labelled *unvalidated* panel | `001 result_card.json` headline |
| 1998 baseline for it | "14 of 14" (mixed-q) / "5 of 15" (paper) | **3 of 3** (Table 5b no-UB, over V); descriptive 10 of 10 (mixed-q, stable-10) | `001 result_card.json` metrics |
| Ψ_w<1 (2026) list | "DE, EL, PT and BE" | **{BE, DE, LU, PT}** (EL=1.22 not <1; LU=−0.00 is <1) | `001 findings.md` l.83 |
| Median bottom-q PTR Δ | **−3.2 pp** over {DK,FI,FR,LU,NL,SE} | **−5.2 pp** over V_Δ={DK,FR,NL}; {DK,FR}-only −14.7 pp; all-14 −1.2 pp (unvalidated) | `headline_scalars.json E5_median_d_a12_over_Vdelta` |
| Spain / Italy | "+42.7 / +40, largest rise" metric | **removed — contradicted by OECD** (ES +34.7 vs +9.8; IT +22.9 vs −7.4) | `001 result_card.json` metric 4; `gate3b_change.csv` |
| Denmark −24.3 pp | "2020s employment-deduction increases" | **−18.0 pp is the single 2025→26 beta step** (uncovered by any gate); −6.2 pp gradual | `welfare_by_year.csv` DK `a_bottom_quintile` |
| Gate 2 | "PASS exact" | **NOT RUN as specced** (1998 arrays never fed through the new path) | audit §2 |
| Gate 3c | "PASS 12/14" (no flag) | 12/14 PASS; **FR, EL τ-unvalidated** (aborted on retry) | `gate3c_FR_EL_completion.csv` |
| Core-hours | "0.7" | **0.22** (logged) + ~0.1 this study | `compute_log.csv` |
| 003 "V = 14", "no τ-unvalidated" | asserted | **false** — V={DK,FR,NL}; FR, EL τ-unvalidated | `findings_addendum_003.md` |

### The headline conclusion, restated (§3 last item)

- **Descriptive version** ("Ψ_w < Ψ_d in 8 of 10 Ψ-stable countries"): **survives** as a
  descriptive, OECD-**unvalidated** statistic (correct arithmetic; IE & SE flip; same-set 1998
  is 10 of 10). It must be labelled unvalidated and never be the headline, because the
  Ψ-stable-10 excludes two of the three validated countries (DK, NL) and includes six level-gate
  failers.
- **Validated-set version** (over V={DK,FR,NL}, 2026, V4): **1 of 3 — France only.** Denmark and
  the Netherlands have **numerically undefined Ψ** in 2026 (bottom-decile PTRs ≈ 100%, genuine
  traps the paper's 1998 survey averages never reached), where the paper's closed form divides by
  1−rate. The same-set 1998 no-UB baseline (Table 5b) had all three at Ψ_w < Ψ_d (3 of 3). So the
  honest reading: the paper's result is **neither confirmed nor overturned on the validated set**
  — it holds where Ψ is computable (France) and becomes undefined where the new traps appear
  (Denmark, Netherlands). The Ψ-instability is itself the finding. Neither softened nor inflated.

## Deliverables

- `report.md` (this file); `results/findings.md`; `result_card.json` (validated-set headline
  first, supersedes 001/002/003); `results/card_corrections.csv` (12 old→corrected mappings);
  `results/baseline_1998_noUB.csv` (Table 5b transcription); gate-completion artifacts
  (`gate3_NL_completion.csv`, `gate3c_FR_EL_completion.csv`, `gate_completions.json`);
  `results/findings_addendum_003.md`; `results/recut_values.json`; figures
  `fig1_gate3b_change_validation.png`, `fig2_headline_by_cut.png`.

## Deviations & limitations

1. **V = 3, not the provisionally-expected 2.** The instruction expected V = {DK, FR} and a
   −14.7 pp median, *conditional on §2.1 failing*. The NL gate-3 completion **passed**, so
   V = V_Δ = {DK, FR, NL} and the conformant E5 median is **−5.2 pp**. The −14.7 pp {DK,FR}-only
   figure is retained as a labelled two-country sensitivity. This is a genuine data outcome, not
   a choice.
2. **FR/EL gate-3c not completable** — the MTR add-on aborts for these two countries on retry,
   exactly as in the originals. They stay τ-unvalidated (the instruction's stated fallback).
   This leaves FR with validated *levels* (in V) but unvalidated *τ*; its E2/E4 numbers carry the
   τ flag.
3. **Tooling install (not a data fetch).** This fresh container had no .NET runtime or EUROMOD
   connector, so euromod 0.4.0, pythonnet and .NET 8.0.31 were installed to run the three gate
   completions. No data was fetched — the EUROMOD zip and all Eurostat/OECD benchmarks were
   already staged locally, and only the paper PDF and staged files were read. Rule 5's
   data-provenance intent is preserved. Compute ≈ 0.3 core-h, well under the 2 core-h budget.
4. **Scope.** This is a reporting correction. Underlying rates (001/002/003 CSVs) are taken as
   correct per the instruction; no headline rate was recomputed except the three §2 completions.
