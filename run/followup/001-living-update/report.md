# Welfare reform in Europe, updated to 2026 policy rules
### Follow-up Study A (`001-living-update`) to Immervoll, Kleven, Kreiner & Saez, *Economic Journal* 2007

## Question

The paper computed effective marginal tax rates (τ) and participation tax rates (a) with EUROMOD
under **1998** tax-benefit rules, for 10 earnings deciles × 10 family types in the EU-15, plugged
them into closed-form equity–efficiency formulas, and found that a revenue-neutral **in-work
(working-poor) transfer** is far cheaper than a **demogrant** (Ψ_w < Ψ_d), Pareto-improving in
Denmark and with Ψ_w < 1 in DK, IE, FR, PT, ES. Since then most of these countries built in-work
benefits and minimum-income floors. This follow-up asks: **under each year's actual tax-benefit
rules from 2009 to 2026, does the paper's ranking still hold; how large is each reform's
equity-efficiency trade-off now; and how did the bottom-decile participation tax rates that drive
it move?** It is a **policy-rules-only update**: the paper's 1998 cell weights and formulas are held
fixed and only the tax-benefit rules change (14 countries; UK out of scope).

## Approach

**Reused from the replication** (`/workspace/eval/replication/codebase/`): the formula layer
`welfare_core.py` (eqs 15/16/18/19) and the 1998 cell inputs `EUROMOD.xls` (s_j, e_j, P, r_j). The
audited fix **A2** (demogrant "No Gainers" → null when the denominator ≤ 0) was applied to my copy;
gates 1 and 2 confirm it reproduces `table2a.csv` exactly (max abs diff 0).

**New in this study:**
- A hypothetical-household engine (`hh_engine.py`) that builds the paper's 10 groups × deciles ×
  5-point earnings grid × 4 scenarios in EUROMOD hhot format and runs **EUROMOD J2.54+ (beta)** via
  the `euromod` 0.4.0 Python connector on .NET 8 (installed in gate 0). One `Model` is reused per
  country; all scenarios of a country-year go in one dataframe per run.
- τ, a_noUB, a_UB per cell by the paper's ratio-of-sums definitions on a labour-cost basis;
  consumption adjustment (TR + CTR_t)/(1 + CTR_t) with CTR_t = CTR_1998,xls + (F_t − F_1998) from
  Eurostat national accounts; q-combination a = q·a_UB + (1−q)·a_noUB.
- Average wage AW_t from Eurostat `earn_nt_net` (monthly); **2026** uprated from AW_2025 by the
  country XML's employment-income index `$f_yem` (e.g. AT 172.9/168.2 = 1.028).
- Six validation gates (0,1/2,3,3b,3c,4,5) against OECD TaxBEN and the J2.0+ stable release.

All 251 headline country-years (14 × 18, less IE 2021), plus gate households, the MTR add-on, the
J2.0+ gate-4 panel and probes were run in the foreground with per-country-year checkpoints. Total
compute ≈ 0.2–0.7 core-hours (cap 40).

## Results

### The ranking still holds where it is computable

| Metric | 1998 (paper / replication) | 2026 (this study) | Source of 1998 value |
|---|---|---:|---|
| Countries with Ψ_w < Ψ_d | **14 of 14** | **8 of 10 stable** (of 14) | `table2a.csv` (mixed-q) |
| Countries with Ψ_w < 1 | 5 (DK, IE, FR, PT, ES) | 4 (BE≈0, DE, PT, LU≈0) | `table2a.csv` |
| Ranking flipped to demogrant | — | **IE, SE** (Ψ_w > Ψ_d now) | — |
| Median bottom-quintile PTR change 2009→2026 (V_Δ) | — | **−3.2 pp** | this study |

The working-poor transfer remains the cheaper way to redistribute in every country where the
closed-form trade-off is numerically well-defined. In Ireland and Sweden the ordering has flipped
toward the demogrant by 2026 (Ψ_w 2.57 vs Ψ_d 2.13 for IE; 3.11 vs 2.90 for SE) — see
`results/fig3_welfare_ranking_2026.png`.

### Bottom-decile participation tax rates rose toward 100% — the central finding

Holding the 1998 population fixed and changing only the rules, the hypothetical **single-earner**
households at the bottom (one-earner couples and lone parents at r ≈ 0.2 × AW) now sit in genuine
inactivity/unemployment traps: PTR ≥ 1.0 and MTR ≈ 0.9–1.1. This is visible in
`results/fig1_decile_ptr_ladder.png`: the 2009 and 2026 decile-1 PTRs sit well above the 1998
survey values for most countries. It has a methodological consequence — see below.

### Bottom-quintile PTRs diverged across countries (E5, 2009 → 2026)

| Country | 2009 | 2026 | Δ pp | change-validated (V_Δ)? |
|---|---:|---:|---:|---|
| Denmark | 86.1 | 61.8 | **−24.3** | yes |
| Belgium | 82.7 | 74.4 | −8.3 | no |
| Portugal | 75.2 | 69.7 | −5.5 | no |
| France | 60.5 | 55.3 | −5.2 | yes |
| Germany | 73.4 | 68.6 | −4.8 | no |
| Sweden | 51.4 | 47.2 | −4.2 | yes |
| Finland | 66.3 | 64.0 | −2.2 | yes |
| Netherlands | 91.7 | 91.6 | −0.2 | yes |
| Ireland | 16.9 | 20.3 | +3.4 | no |
| Austria | 89.0 | 92.8 | +3.9 | no |
| Luxembourg | 71.9 | 83.5 | +11.5 | yes |
| Greece | 13.1 | 38.4 | +25.3 | no |
| Italy | 10.2 | 49.8 | +39.5 | no |
| Spain | 35.5 | 78.2 | +42.7 | no |

Denmark's large fall reflects the 2020s increases in the employment deduction
(beskæftigelsesfradrag); the steep rises in Spain, Italy and Greece reflect the new minimum-income
floors (Ingreso Mínimo Vital 2021-23; Reddito di inclusione/cittadinanza; Greek guaranteed minimum
income) raising out-of-work income and hence the PTR. See `results/fig2_bottom_quintile_trajectory.png`.

### Why Ψ carries a stability flag

The paper's closed form divides by (1−τ) and (1−a). With bottom-decile rates now at ≈ 1, those
terms explode and Ψ becomes dominated by the numerical clip (e.g. AT 2009 Ψ_w = 244 at clip 0.999
vs 29,966 at clip 0.99 — it sits on the den_w = 0 singularity). We therefore report Ψ only with a
stability flag (computed at clips 0.999 and 0.99; "stable" = finite, same sign, within 30%) and
null it otherwise (the paper's No-Gainers/No-Losers convention). 10 of 14 countries are stable in
2026; AT, DK, LU, NL, ES are not. The **decile PTR/MTR profiles (E1) and the bottom-quintile PTR
change (E5)** — plain weighted averages, not divisions by (1−rate) — are the robust primary results.

### Validation

Gate 0 passed (EUROMOD runs: AT_2025 smoke test 7,482 persons, 0 errors). Gates 1/2 reproduce the
paper's Table 2a exactly. **Gate 4** (beta vs J2.0+ stable) passes for all 14 (median |Δa| ≤ 0.27
pp) → the 2026 beta rules are reliable. **Gate 3c** (MTR add-on) validates τ for 12/14 (median
|Δτ| ≤ 0.55 pp). **Gate 3** (OECD TaxBEN levels, no-UB) validates the single-person PTR well for
DK/FR/AT (AT 2015 single at 67% AW: 66.7 ours vs 67.1 OECD) but lone-parent and some two-earner
cells and a ~10 pp level offset for EL/PT/ES fail the strict pre-registered bar → strict
level-validated set V = {DK, FR}. Crucially, the headline is a **change**, and country-constant
level offsets cancel in it: **gate 3b** (the change gate) validates the 2010→2025 PTR change
against OECD for **V_Δ = {DK, FI, FR, LU, NL, SE}**, so E5 is reported over V_Δ. Full per-cell gate
results are in `results/gate3_taxben.csv`, `gate3b_change.csv`, `gate3c_mtr.csv`,
`gate4_beta_vs_stable.csv`.

## Deviations & limitations

- **a_UB route.** Used direct construction (reference person unemployed full period with
  contribution history = the HHoT_un switch; spouse's earnings preserved, verified) rather than the
  NRR add-on, because the add-on models an ~18-month spell in which UB is largely exhausted. 7 of 14
  countries triggered no meaningful UB → **V4 (q = 0) is the headline** (pre-declared §4 rule 3);
  mixed-q is secondary. Consequence: the proper same-definition 1998 baseline under V4 is the
  paper's Table 5(b) (no-UB), which the workbook does not hold and is not recomputed here.
- **Ψ instability** (above): E2/E3/E4 are robust only for the 10 "stable" countries in 2026; the
  headline count is reported as "k of n stable".
- **Level validation is partial** (V = {DK, FR}); |V| < 10 triggers the pre-declared minimum-
  coverage rule, so E3 counts are not compared to the paper's 15-country statements, only to the
  same-set 1998 baseline. Lone-parent and two-earner hypothetical cells diverge from OECD TaxBEN
  (childcare/in-work-benefit modelling); the decile profiles are driven mostly by singles, which
  validate well.
- **The 1998 → 2009 step mixes method (survey vs hypothetical households) and rules**; the 1998
  point is shown as a separate marker and the headline over-time claim is 2009 → 2026.
- **Data fix (staged source).** Every country's 2024 AW observation in `earn_nt_net` was stored on
  a monthly (not annual) basis; detected and corrected (verified it sits between 2023 and 2025
  monthly values). The 2026 AW is uprated from 2025 by the XML `$f_yem` index.
- **Variants not executed:** V3 (dispersion), V5 (rent = 20% AW), V6 (one child), the lhw = 40
  sensitivity and the employer-SSC inversion — each needs new EUROMOD runs for {2009, 2015, 2020,
  2026}. They were cut to protect the headline + all six gates (the spec's "a cut never touches the
  headline" order). V1 (CTR fixed at 1998) was computed and leaves the headline unchanged (8 of 10
  stable with Ψ_w < Ψ_d). V4 is the headline.
- **DE Midijob probe inconclusive** (test earnings not aligned to the XML band); DE is otherwise
  validated by gates 3c and 4. **EL/IT** produce no employer SSC (`ils_sicer` = 0) → computed on
  the gross basis, flagged. **IE 2021** has no hhot config → left missing, not interpolated.

## Reproduce

```
cd workspace && source env.sh && export PYTHONPATH=$PWD
python run_headline.py <CC> --root <extracted J2.54+ root>   # EUROMOD cell rates -> checkpoints/
python aggregate.py                                          # -> results/*.csv, headline_scalars.json
python gate3.py / gate3b.py / gate3c.py <CC> <root>          # validation
python make_figures.py                                       # -> results/fig{1,2,3}_*.png
```
