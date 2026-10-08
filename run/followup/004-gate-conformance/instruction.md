# Corrective study: 004-gate-conformance — re-cut the living-update cards to the spec's own gate rules

## What this is

Studies 001/002/003 computed everything cleanly (the provenance audit found data, gates 0/1/4
and continuation handling CLEAN), but the REPORTING layer violated the spec's validation
rules. This study supersedes their cards and findings with gate-conformant ones. It is an
artifact-level correction: **run no new EUROMOD simulations** except the three small gate
completions listed in §2. The authoritative defect list is
`/workspace/eval/gate-conformance-inputs/immervoll-provenance.md` §4–§5 and §7 (staged; read
it fully first), against the spec at `gate-conformance-inputs/spec-living-update.md`.

## 1. Inputs (all already on disk in the run tree)

- `followup/001-living-update/` + `followup/002-living-update-cont/` results CSVs
  (welfare_by_year.csv, ptr tables, gate artifacts) and `followup/003-theory-update/`
  frontier_by_era.csv. Treat all result CSVs as correct computations; your job is the
  honest aggregation and presentation.
- The staged audit + spec in `gate-conformance-inputs/`.

## 2. The only new computation allowed (gate completions, ~minutes each)

1. **NL gate-3 level rows** (its original run died on a tool timeout and was never redone):
   re-run only the NL OECD-comparison households needed for gate 3, using the identical
   household-construction code from 001's workspace. If it fails again, NL is "no level
   test" and is excluded everywhere, stated.
2. **FR and EL MTR add-on gate (3c)**: the add-on run aborted; retry once. If it fails, both
   are "τ unvalidated" and flagged wherever their MTR-based numbers appear.
3. **Transcribe paper Table 5(b)** (no-UB 1998 rates) from the paper PDF into
   `results/baseline_1998_noUB.csv` so the 1998 V4 baseline is same-definition. Double-read
   every value against the printed table (transcription-fidelity rule).

## 3. Required re-cuts (apply audit §7 items 1–7 exactly)

- Validated set V per the spec's pre-registered thresholds: expected {DK, FR} (+NL only if
  §2.1 passes). Apply the |V| < 10 honest-partial rule: the card headline becomes
  "OECD-validated in k of 14"; all-14 numbers appear only in a clearly-labelled
  "unvalidated levels" panel.
- Remove ES and IT from the PTR-change metric or label them "contradicted by the OECD change
  benchmark" with the numbers (ES +34.7 vs +9.8; IT +22.9 vs −7.4). V_Δ must be a subset of V.
- Median PTR change reported over spec-conformant V_Δ (−14.7 pp over {DK, FR}) with the
  all-14 figure (−1.2 pp) as the labelled unvalidated panel; drop the −3.2 pp number.
- Denmark's −24 pp attributed mainly to the single 2025→2026 beta-rules step (−18 pp), which
  no gate covers; say so on the card.
- Same-set 1998 baselines (stable-10: 10 of 10; Ψ_w < 1: 3 of 10), with the V4 1998 baseline
  from the new Table 5(b) transcription.
- Corrected gate table (gate 2 not run as specced; 3c 12/14 + retries' outcomes; NL status).
  Fix 003's false "V = 14" and "no τ-unvalidated" statements in a findings addendum.
- Fix the small errors: card table rows (add EL, LU; mark DK beta-step and ES), the Ψ_w<1
  country list (BE, DE, LU, PT), the core-hours figure (0.22).
- The headline conclusion must be re-stated under the conformant cut: report whether
  "Ψ_w < Ψ_d in 8 of 10 Ψ-stable countries" survives when the set is labelled as
  descriptive/unvalidated, and what the validated-set version of the claim is. Do not
  soften or inflate either way.

## 4. Deliverables

`report.md`, `results/findings.md` (opens with: what was corrected and why, referencing the
provenance audit), corrected card `result_card.json` whose summary states the validated-set
headline first, `results/card_corrections.csv` (old claim → corrected claim → reason),
the new `baseline_1998_noUB.csv`, and gate-completion artifacts. The old studies stay on
disk untouched; this card supersedes theirs for publication.

## 5. Rules

Foreground execution only; no fetches beyond the paper PDF already staged; honest-partial
over silent substitution everywhere; never present an unvalidated number without its label;
compute budget < 2 core-hours; `--timeout 7200`.