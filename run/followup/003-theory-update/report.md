# Study B — Theory, updated to 2026 (`002-theory-update`)

**Run:** `followup/003-theory-update/` · **Date:** 2026-10-05 · **Compute:** CPU only, minutes, **no EUROMOD runs, no fetches** (per spec §11.6).

## Question

Write the "Theory, updated to 2026" section the Immervoll–Kleven–Kreiner–Saez (IKKS, *EJ* 2007) welfare-reform paper would carry today, *as a model*. Starting from the paper's own discrete participation + intensive framework (eqs 15–19, Table-3 logic) and Study A's recomputed 2009–2026 tax-benefit rates, (1) read each era's tax-benefit system as an **inverse optimum** (Saez 2002) and recover social marginal welfare weights g by decile; (2) draw the **elasticity frontier** by era in (η̄, ε) space and overlay post-2007 literature; (3) propose **one minimal amendment** (η on secondary earners/lone parents) and reject one alternative (unemployment channel); (4) run a **linearisation accuracy** consistency check and (4b) an **external validation** of the cost-per-job of a marginal in-work transfer in Belgium against de Mahieu (2021); (5) ship `theory_update.md`, `external_check_be.csv`, `calibration_table.csv`, one frontier figure, and tag every claim [ESTIMATED]/[CALIBRATED]/[PROPOSED].

## Approach

**Reused, not re-run.** Study A's completed continuation `002-living-update-cont/` supplied all rates and code. I copied `welfare_core.py` and `fixed_inputs.py` into my workspace and imported `welfare_layer.py` from the 002-cont workspace (read-only) to rebuild the q=0/V4, consumption-adjusted, capped-0.999 decile rates **identically to how 001 computes Ψ** — guaranteeing the inverse optimum and the frontier use the same numbers as Study A's Pareto flags. I read the 1998 baseline from the replication's `table2a.csv` and the 1998 cell structure from `EUROMOD.xls`. No EUROMOD, no network.

**Respected from Study A:** validated set V = all 14 countries; headline regime **V4 (q=0)** (7 UB-leg fallbacks); **no "τ unvalidated" country** (gate-3c medians ≤ 0.55 pp); Ψ-instability for the lower deciles.

**Built (all in `workspace/`):** `saez_inverse.py` (the g inversion), `run_item1.py` (+ `run_item1_sens.py`), `frontier.py`, `run_item3.py`, `run_item4.py`, `run_item4b.py`, `run_calibration.py`, `make_figure.py`.

## Results (full write-up in `results/theory_update.md`)

1. **Inverse optimum [CONSISTENCY CHECK].** DK 1998 reproduces the paper's Pareto result: decile-1 g = **−0.73 < 0** in a working-poor-gainer decile (D_w = −1.654, matches `table2a.csv`). The strict g-iff flags **only DK** in 1998 (matching the paper), vs 001's looser eff_w>0 which adds 4 knife-edge cases. g-iff ↔ 001-flag agreement is **89.9% on stable country-years** (72.5% overall). By 2026 bottom-decile g turns negative in AT, BE, DE, ES, LU, NL, PT — but in AT/NL/ES this is a **participation-trap artifact** (a→1, Ψ unstable), not a genuine Pareto gain; the g-iff **over-predicts** there, which I flag.

2. **Elasticity frontier [ESTIMATED; CALIBRATED bands]** (`fig1_elasticity_frontier.png/.pdf`). The "in-work transfer cheaper" boundary **moved left after ~2017**: median critical η̄ (panel {FI,FR,EL,IT,SE}, ε=0.1) fell **0.22 (2009) → 0.13 (2026)**. Count of 14 V-countries where Ψ_w<Ψ_d holds, by literature elasticity (2026): **Kleven US-EITC (≈0): 0/14**, Bartels & Shupe (≈0.11): 5/14, Chetty (0.25): 9/14, Lundberg & Norell (0.38): 10/14. **The paper's conclusion survives mid-range elasticities and is strengthened post-2017, but collapses at the US-EITC floor.** Full Pareto became *harder* (critical η̄ 0.42→0.92).

3. **Minimal amendment [ESTIMATED; CALIBRATED].** Reallocating η onto secondary earners + lone parents (groups 2,7–10), aggregate η̄ held fixed, barely moves the 2026 ranking (in-work-cheaper 8→7 of 10 stable; one flip, IT). So *composition* is not the mechanism; the *level* of bottom-decile PTRs is. Kept as the minimal theory-grounded change.

4. **Rejected alternative [PROPOSED].** Kroft, Kucko, Lehmann & Schmieder (2020) unemployment/wage-response channel — rejected on calibration grounds (needs parameters 001's artefacts cannot identify).

5. **Linearisation accuracy [CONSISTENCY CHECK].** Fit on 2009→2017 (R²=0.57, n=6) predicts 2018→2026 with **R²=−0.18** — the linearisation does not track, reinforcing that the robust carrier is the PTR change, not Ψ_w levels.

6. **Belgium external check — validation [CALIBRATED vs literature]** (`external_check_be.csv`). Model marginal cost per FTE of a lump-sum in-work transfer sits **below** de Mahieu (2021)'s €368.5k–1,660.1k: **self-financing (negative) at benchmark η**, €22–30k at Bartels-Shupe η. This is the **pre-declared expected direction** (model transfer is a lump sum with no phase-out; BE bottom-decile PTRs ≈0.85 make the extensive-margin revenue large). Consistent with the published estimate; BE only.

### Comparison to the original

| Quantity | Original (source) | This study (2026) | Note |
|---|---|---|---|
| DK Pareto in 1998 (g<0 in a G_w decile) | Pareto, eff_w=+1.654 (`table2a.csv`) | g_1=−0.73<0, reproduced | reproduction check passes |
| Only-DK-Pareto statement (1998) | paper | g-iff flags only DK | matches paper's strict claim |
| Critical η̄ for Ψ_w<Ψ_d | — | 0.22 (2009) → 0.13 (2026) | in-work dominance now at lower η |
| In-work beats demogrant "for a wide range of η" (C12) | 14/14 at benchmark | 0/14 (US-EITC) → 9/14 (Chetty) in 2026 | survives mid-range; fails at η≈0 |
| Cost per FTE, marginal in-work transfer, BE | €368.5k–1,660.1k (de Mahieu 2021) | −€7.5k (benchmark η) … €22–30k (B&S η) | below range, as pre-declared |

## Deviations & limitations

- **No new rates.** By design Study B reuses 001's rates; it inherits every Study A limitation (V4/q=0 headline, Ψ-instability at the bottom, gross-basis EL/IT, IE-2021 gap, UK out of scope, method break at 1998→2009). The 1998 point is survey-cell averages; 2009+ are hypothetical households — never joined.
- **g over-prediction flagged, not hidden.** The strict g<0 "iff" flags Pareto in 3 extra 2026 countries (AT, NL, ES) that are participation-trap/Ψ-unstable; reported as a consistency-check artifact, not a finding.
- **Frontier panel is 5 countries** ({FI,FR,EL,IT,SE}) — those stable in all four eras — chosen for a like-for-like across-era comparison; per-country critical values for all 14 are in `frontier_survival.csv`. EL, IT are gross-basis.
- **Linearisation n is small** (6 fit / 7 test) because Ψ_w is finite+stable for few country-years; the negative out-of-sample R² is itself the point of the check.
- **Bartels-Shupe η operationalised as a flat 0.11** (mid of 0.08 men / 0.14 women) across target deciles for the frontier survival counts and the BE check; the men/women split is noted.
- **External check is Belgium only** — the sole study country with a cited behavioural cost-per-job estimate.
- All figures/tables/numbers are produced by this session's execution; original-side values are read from `run/replication/codebase/results/table2a.csv` and 001's `headline_scalars.json`/CSVs (cited inline).
