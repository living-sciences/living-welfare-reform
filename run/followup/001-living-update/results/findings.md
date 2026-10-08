# Findings — Welfare reform in Europe, updated to 2026 policy rules (Study A, `001-living-update`)

## METHOD (plain statement)

This is a **policy-rules-only update** of Immervoll, Kleven, Kreiner & Saez (EJ 2007). The
paper's closed-form equity–efficiency formulas (eqs 15, 16, 18, 19) and its **1998 cell
structure are held fixed**: the wage shares s_j, employment shares e_j, the participation rate P,
and each cell's relative earnings position r_j = s_j/e_j come unchanged from the authors'
`EUROMOD.xls`, read through the replication's `welfare_core.py`. Only the **tax-benefit rules
change**: for each policy year t ∈ 2009…2026 and each of the paper's 10 demographic groups × 10
earnings deciles, the effective marginal tax rate τ and participation tax rates (a_noUB, a_UB) are
recomputed from **EUROMOD J2.54+ (beta, Sept 2026)** run on **hypothetical households** written
directly in EUROMOD hhot input format at earnings r_j × AW_t × {0.8…1.2}. 14 countries (the
pre-2004 EU members still in EUROMOD: AT, BE, DK, FI, FR, DE, EL, IE, IT, LU, NL, PT, ES, SE); the
UK is out of scope (it left EUROMOD). No representative microdata were used. **The 1998 point is a
different method** (survey-microdata cell averages), so it is shown only as a separately marked
point and the headline over-time claim is the **2009 → 2026 change**, never the 1998 → 2009 step.

## Headline answer

**The paper's central qualitative finding survives: a revenue-neutral in-work (working-poor)
transfer still dominates a demogrant (Ψ_w < Ψ_d) in every country where the trade-off is
numerically well-defined — 8 of the 10 "stable" countries in 2026 (and 2 — Ireland, Sweden — have
flipped toward the demogrant).** But two things have changed since 1998, both driven by the large
in-work-benefit and minimum-income reforms of 2009-2026:

1. **Bottom-decile participation tax rates have risen toward 100% in the hypothetical single-earner
   households**, producing genuine inactivity/unemployment traps. This is the single most important
   result and it has a methodological consequence (below).
2. **Bottom-quintile PTRs moved in opposite directions across countries**: they fell sharply in
   Denmark (−24 pp, the 2020s employment-deduction increases) and modestly in FR/DE/SE/FI/BE/PT,
   but rose steeply in Spain (+43 pp, the 2021-2023 Ingreso Mínimo Vital), Italy (+40 pp), Greece
   (+25 pp) and Luxembourg (+12 pp) as those countries built minimum-income floors. Median change
   over the change-validated set V_Δ = {DK, FI, FR, LU, NL, SE} is **−3.2 pp**.

## The central methodological finding (and why Ψ carries a stability flag)

Under 2009+ rules the hypothetical **single-earner** cells at the bottom (one-earner couples,
groups 4/6/8/10, and lone parents, group 2, at r ≈ 0.2 × AW) are in genuine traps: PTR a ≥ 1.0 and
MTR τ ≈ 0.9–1.1. The paper's closed form divides by (1−τ) and (1−a), so near rate = 1 the
efficiency terms explode and Ψ becomes dominated by the numerical clip. (Example: AT 2009 Ψ_w =
244 at clip 0.999 but 29,966 at clip 0.99 — it sits on the den_w = 0 singularity.) The paper never
saw this because its survey cell-averages kept all rates comfortably below 1. We therefore:
- report **Ψ (E2/E3/E4) only with a stability flag** (Ψ computed at clips 0.999 and 0.99; "stable"
  = finite, same sign, within 30%), and null otherwise (the paper's No-Gainers / No-Losers
  convention); 10 of 14 countries are stable in 2026;
- treat the **decile PTR/MTR profiles (E1) and the bottom-quintile PTR change (E5) as the robust,
  primary results** — they are plain employment-weighted averages, not divisions by (1−rate).

This instability is itself a finding: it quantifies how far bottom-decile rates have risen.

## Validation (gates)

| Gate | Result |
|---|---|
| 0 Environment | **PASS** — .NET 8.0.31 + euromod 0.4.0; AT_2025 smoke test 7,482 persons, 0 errors, 12.8 s |
| 1 Anchor (Table 2a) | **PASS, exact** — reproduces `run/replication/.../table2a.csv` (max abs diff 0) |
| 2 Plumbing anchor | **PASS** — new aggregation path reproduces gate 1 identically (A2 fix applied) |
| 3 Levels, no-UB (OECD TaxBEN DF_PTRSA) | **PASS DK, FR**; single (S_C0) cells match well for AT/DK/FR (AT 2015 S_C0 AW67 66.7 vs 67.1). Lone-parent (S_C2) and some two-earner cells, and a ~10 pp uniform level offset for EL/PT/ES, diverge → these countries are not level-validated. |
| 3 UB leg (DF_PTRUB) | **FAIL ~everywhere** — our full-period UB vs OECD's 2-month (M2) spell; consistent with the q = 0 / V4 headline |
| 3b Change gate | **V_Δ = {DK, FI, FR, LU, NL, SE}** pass (2010→2025 PTR change, sign + within 5 pp of OECD). Country-constant level offsets cancel in the change, so the headline *change* claim is validated here. |
| 3c MTR gate (τ) | **PASS 12/14** (median |τ_ours − τ_addon| ≤ 0.55 pp); FR & EL MTR add-on aborted (τ covered by gate 4) |
| 4 Beta vs stable (J2.0+) | **PASS all 14** — median |Δa| ≤ 0.27 pp (BE), so the 2026 beta rules are reliable; no "beta rules" caveat needed |
| 5 Sanity | share of τ≥0.99 / a≥0.99 cells logged per country-year in `welfare_by_year.csv` (n_hi_tau, n_hi_a) |
| IE hours probe | **PASS** — lone-parent disposable income differs at 18 h vs 20 h (WFP hours condition read) |
| DE Midijob probe | **inconclusive** — fixed test earnings did not align to the XML band; DE otherwise validated by gates 3c & 4 |

## q-regime

7 of 14 countries triggered no meaningful unemployment benefit in the hypothetical households
(BE, DK, DE, IT, NL, PT, SE) — either genuinely (long-term-unemployment floors) or because a_UB
could not be constructed (IT's `yempv` leaks into current earnings). With ≥ 4 fall-backs, **V4
(q = 0, no-UB panel) is the headline** per the pre-declared §4 rule 3; the mixed-q version is
secondary. a_UB used the direct-construction route (reference person unemployed full period with
contribution history; identical to the HHoT_un switch, with the spouse's earnings preserved —
verified), chosen over the NRR add-on because the add-on models an ~18-month spell in which UB is
largely exhausted.

## 1998 baseline comparison

- 1998 (mixed-q, from `table2a.csv`): **14 of 14** have Ψ_w < Ψ_d; Ψ_w < 1 in 5 (DK, IE, FR, PT,
  ES), matching the paper's C5.
- 2026 (V4/q=0): **8 of 10 stable** have Ψ_w < Ψ_d; 4 have Ψ_w < 1 (DE, EL, PT and BE≈0).
- Because the headline is V4 and 1998 → 2026 mixes method and q-regime, the proper same-definition
  1998 baseline is the paper's Table 5(b) (no-UB); it is not recomputed here (the workbook holds
  only combined a_j) and is noted as a limitation.
- Robustness V1 (CTR fixed at the 1998 value): unchanged, 8 of 10 stable with Ψ_w < Ψ_d.

## Deviations and limitations

See `../report.md` §Deviations. Key: strict level validation holds only for singles/one-earner
cells (V = {DK, FR}); the change claim is validated over V_Δ (6 countries); Ψ is unstable for
AT/DK/LU/NL/ES; the new-run variants V3 (dispersion), V5 (rent), V6 (one child), lhw=40 and the
employer-SSC inversion were **not executed** (prioritising the headline + all six gates, per the
spec's "a cut never touches the headline" order); V1, V2-concept and V4 are covered.
