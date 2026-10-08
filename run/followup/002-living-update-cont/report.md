# Welfare reform in Europe, updated to 2026 — Study A continuation (`003-living-update-cont` role)

**Run:** `followup/002-living-update-cont/` · **Date:** 2026-10-05 · **Model:** EUROMOD J2.54+ beta (Sept 2026), connector `euromod==0.4.0`, .NET 8 coreclr.

This session is the **continuation** of `followup/001-living-update/`. Per the continuation rule (§10 of the spec), it links 001's checkpoints, results and `input_conventions.csv`, skips every country-year that already has a checkpoint, does not re-run gates that already have a results row, **finishes the remaining work, and writes the deliverables.**

---

## 1. Question

Hold the Immervoll–Kleven–Kreiner–Saez (EJ 2007) 1998 cell structure (wage shares s_j, employment shares e_j, participation P, relative earnings r_j = s_j/e_j) and closed-form welfare formulas fixed; recompute each cell's effective marginal tax rate τ and participation tax rate a from EUROMOD run on hypothetical households under **each year's actual tax-benefit rules, 2009–2026**, for 14 pre-2004 EU members; then ask, through the paper's own formula layer, whether the "in-work transfer beats demogrant" ranking still holds, how large the equity–efficiency trade-off is now, and how bottom-decile participation tax rates moved. This is a **policy-rules-only counterfactual**: only the rules change, never the 1998 population weights.

## 2. What was inherited vs. what this continuation added

**Inherited from 001, reproduced exactly (not re-run):**
- Gate 0 (environment), Gates 1–2 (anchor: reproduce paper Table 2a through the copied `welfare_core.py` — re-verified here, DK/SE/PT/ES values match the paper, e.g. Ψ_d SE = 8.35, Ψ_w PT = 0.99).
- The **headline** EUROMOD cell rates: 14 countries × 18 years (less IE 2021) = 251 country-year checkpoints.
- Gate 3 / 3b / 3c (OECD TaxBEN levels, change gate, MTR gate) and Gate 4 (beta vs stable J2.0+).
- Re-running `aggregate.py` on the inherited checkpoints reproduced 001's headline **bit-for-bit**: regime **V4 (q=0)**, 7 q=0 fallbacks; 2026 count **8 of 10** stable countries with Ψ_w < Ψ_d; median 2009→2026 bottom-quintile PTR change over V_Δ = **−3.24 pp**.

**Completed by this continuation (the work 001 cut despite using only 0.7 of 40 core-hours — the cut was *not* budget-justified):** the five pre-declared secondary variants, each a fresh set of EUROMOD runs at t ∈ {2009, 2015, 2020, 2026} (SSC-inversion at 2025):

| Variant | What it changes | New runs |
|---|---|---|
| **V3** | SES-dispersion update: stretch log r_d around the employment-weighted median decile position so implied cross-decile P90/P10 = SES vintage nearest t | 14 × 4 = 56 |
| **V5** | rent = 20% of AW (OECD housing convention) | 14 × 4 = 56 |
| **V6** | one child (aged 6) instead of two | 14 × 4 = 56 |
| **lhw40** | hours fixed at 40 (vs the §3.2 part-time hours rule) | 14 × 4 = 56 |
| **employer-SSC inversion** | place cells on a labour-cost basis: gross + employer SSC = r·(AW + employer SSC at AW) | 14 × 1 (2025) = 14 |

Total this session: **238 new EUROMOD runs**, **0.30 core-hours** added (whole study, incl. inherited logged runs, 0.48 core-hours — vs the 40 core-hour cap). All variants checkpointed under `workspace/checkpoints/<variant>/` and aggregated at the headline **V4 (q=0)** regime for comparability (`results/welfare_variants.csv`).

**Defect fixed in the copied code.** The inherited `hh_engine._household` accepted a `rent` argument but `_person` hard-coded `xhcrt = 0`, so V5's `rent = 0.20·AW` never reached EUROMOD — the first V5 pass was byte-identical to the headline (Δ ≡ 0). I wired the rent onto the household head (`ref['xhcrt'] = rent`) and re-ran V5; it now moves the bottom-quintile PTR by up to 6.4 pp. (Fix applied only to the workspace copy; `run/replication/` untouched.)

## 3. Results

### 3.1 Headline (inherited, reproduced)

The paper's core qualitative finding **survives where the closed form is computable**: in 2026, **8 of 10** stable-Ψ countries have Ψ_w < Ψ_d (in-work transfer cheaper than demogrant); the ranking flips toward the demogrant only in IE and SE. Ψ_w < 1 in 4 of 10; Pareto (no losers) in 4 of 10 (BE, DE, LU, PT). The central *new* phenomenon, unchanged from 001: under 2009+ rules, bottom-decile PTR/MTR in single-earner hypothetical households approach 100% (participation traps), which destabilises the paper's closed-form Ψ for the lower deciles — so the **robust** deliverables are the decile PTR profiles and the bottom-quintile PTR *change*, not the Ψ levels.

**E5 — bottom-quintile PTR change 2009→2026 over the change-validated set V_Δ = {DK, FI, FR, LU, NL, SE}** (median **−3.24 pp**):

| Country | 2009 | 2026 | Δ |
|---|---|---|---|
| Denmark | 86.1 | 61.8 | **−24.3** |
| France | 60.5 | 55.3 | −5.2 |
| Sweden | 51.4 | 47.2 | −4.2 |
| Finland | 66.3 | 64.0 | −2.2 |
| Netherlands | 91.7 | 91.6 | −0.2 |
| Luxembourg | 71.9 | 83.5 | +11.5 |

The bottom-quintile PTR fell in 5 of 6 change-validated countries — the in-work reforms of the 2010s–2020s show up as lower participation tax rates at the bottom, led by Denmark (−24 pp).

### 3.2 Variant sensitivity (new — the question "how robust is the headline?")

Each variant is reported as the four pre-declared points beside the 18-year headline line (`results/welfare_variants.csv`; figure 4). Effect on the key metric (bottom-quintile PTR) and on the 2026 ranking:

| Variant | mean \|Δ bottom-quintile PTR\| | max \|Δ\| | 2026 Ψ_w < Ψ_d (stable) |
|---|---|---|---|
| **headline** | — | — | **8 / 10** |
| V3 SES dispersion | 3.06 pp | 12.28 pp | 8 / 10 |
| lhw = 40 | 1.83 pp | 20.93 pp | 7 / 9 |
| V6 one child | 0.74 pp | 3.77 pp | 7 / 9 |
| V5 rent = 20% AW | 0.68 pp | 6.35 pp | 7 / 8 |
| employer-SSC inversion (2025) | 0.20 pp | 1.52 pp | 6 / 8 (vs 6/8 headline-2025) |

**Conclusion: the headline is robust.** The share of stable countries with Ψ_w < Ψ_d stays in the 75–100% band under every variant (V3 is identical to the headline, 8/10; SSC-inversion identical to headline-2025, 6/8). The paper's "in-work transfer is cheaper" ranking does **not** flip under any pre-declared assumption change.

The variant that moves the key metric most on average is **V3 (dispersion)** — unsurprising, since it relocates the whole earnings grid. Its largest 2026 shifts: IE −10.3 pp (headline 20.3 → 10.0), DK +5.0, PT −4.7, BE −3.7, NL −3.7. The **hours rule** (lhw40) has the single largest cell-level effect (20.9 pp max) at the bottom decile, confirming the spec's concern that hours drive bottom-decile rates for WFP/Midijob-type rules. The **SSC basis** (inversion) barely matters (0.2 pp mean), as expected where employer SSC is close to proportional.

### 3.3 Comparison to the original paper

| Quantity | Original (source) | This study (2026) | Note |
|---|---|---|---|
| Countries with Ψ_w < Ψ_d | 14 of 14 (`table2a.csv`) | 8 of 10 stable | survives; flips in IE, SE |
| Countries with Ψ_w < 1 | 5 of 15 — DK,IE,FR,PT,ES (`table2a.csv` + C5) | 4 of 10 stable (V4/q=0) | set + q-regime differ |
| Robustness of ranking to assumptions | not tested in paper | **8/10 → 7–8/≤10 across 5 variants** | ranking never flips |
| DK bottom-quintile PTR | 84% decile-1 1998 (paper C2) | 86.1 (2009) → 61.8 (2026) | largest fall, change-validated |
| Table 2a anchor (gate 1) | `table2a.csv` | max abs diff 0 | formula layer reused exactly |

## 4. Deviations & limitations

- **Headline regime is V4 (q = 0)** (pre-declared rule 3): 7 of 14 countries triggered no meaningful unemployment benefit in the hypothetical households, so the no-benefit panel is the headline and mixed-q is secondary. Inherited from 001, unchanged.
- **Ψ levels are unstable for the lower deciles** (PTR/MTR → 1 traps); Ψ-based counts are reported only over the "stable" countries, and this instability is itself a finding. Robust deliverables are the decile profiles and the bottom-quintile PTR change.
- **V5 rent was a no-op in the inherited code**; fixed here (see §2). This means 001's own V1 (and any report that implied V5 was run) would have shown no rent effect; the corrected V5 moves PTR by up to 6.4 pp.
- **V3 operationalization is documented and labelled**: w_d = employment-weighted decile earnings position; interpolate log w in percentile to P10/P50/P90; λ = ln(SES P90/P10)/ln(current); r′ = m·(r/m)^λ. SES data (`earn_ses*_adeci`) cover all 14 countries for all four vintages, so V3 ran for all 14 (SES P90/P10 by country logged in `results/v3_ses_p90p10.csv`, the public analogue of the blocked Fig 3). Vintage mapping: 2009→2010, 2015→2014, 2020→2018, 2026→2022.
- **Employer-SSC inversion is a first-order reparameterization**: r′_{g,d} = r·(1+σ_AW)/(1+σ_cell) using the headline-2025 per-cell employer-SSC ratio σ_cell and the AW-level σ_AW from `input_conventions.csv`; identity where SSC is proportional. One run per country, no iteration — adequate for a 2025-only labelled sensitivity.
- **Gate-0 output variable count** was 735 (euromod 0.4.0) vs the spec's "~436/446"; this is how the connector returns output columns, not an error — the smoke test ran with 0 errors and the correct 7,482 persons.
- Gross-basis countries (**EL, IT**, employer SSC not produced → `ils_sicer = 0`) and the **IE 2021** gap (no hhot config) are inherited unchanged; the SSC-inversion is therefore the identity for EL/IT.
- **Out of scope** (stated as limits): UK (left EUROMOD; tables are 14-country), representative-microdata claims C1/C3/C8/Table 7 (need EU-SILC behind a Eurostat RPP), policy years 2005–2008 (no hhot configs), post-2004 members, elasticity re-estimation (Study B). Bottom-decile rates (r ≈ 0.2, part-time) have no external TaxBEN benchmark in any country; they rest on the internal IE-hours (PASS) and DE-Midijob (inconclusive) probes only.
- **The 1998 → 2009 step mixes method and rules** (1998 rates are survey-cell averages; 2009+ are hypothetical households), so it is shown as a separate unjoined marker; the headline over-time claim is the 2009 → 2026 change.

## 5. Artifacts

Headline (regenerated into this run's `results/`, identical to 001): `rates_cells.csv`, `rates_deciles.csv`, `welfare_by_year.csv`, `critical_eta_by_year.csv`, `headline_scalars.json`, `gate3_taxben.csv`, `gate3b_change.csv`, `gate3c_mtr.csv`, `gate4_beta_vs_stable.csv`, `input_conventions.csv`, `findings.md`.
New this continuation: `welfare_variants.csv` (489 rows, all 5 variants + headline at the variant years), `variant_summary.json`, `v3_ses_p90p10.csv`, `compute_log.csv` (updated), and `fig4_variant_sensitivity.png`. Figures `fig1`–`fig3` regenerated.
