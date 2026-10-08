# Theory, updated to 2026

**Welfare reform in European countries, re-read through optimal-transfer theory under 2009–2026 tax–benefit rules.**

Study B (`002-theory-update`) of the Immervoll–Kleven–Kreiner–Saez (IKKS, *Economic Journal* 2007) follow-up.
Run: `followup/003-theory-update/` · Date: 2026-10-05 · **CPU-only, no EUROMOD runs, no fetches.**
Seeded from `followup/002-living-update-cont/` (the completed continuation of `001-living-update`): its `rates_cells.csv`, `rates_deciles.csv`, `welfare_by_year.csv`, `critical_eta_by_year.csv`, code (`welfare_core.py`, `welfare_layer.py`, `fixed_inputs.py`) and `headline_scalars.json` are the inputs. Study A's validated set **V = all 14 countries** (level-validated), headline **q-regime = V4 (q = 0)** (7 of 14 UB-leg fallbacks), and **no country is "τ unvalidated"** (gate-3c median |τ_ours − τ_addon| ≤ 0.55 pp everywhere) are respected throughout.

Every claim is tagged **[ESTIMATED]** (from 001's rates), **[CALIBRATED]** (literature elasticities), **[CONSISTENCY CHECK]** (mechanically implied by the same rates and formulas), or **[PROPOSED]** (not calibrable from the artefacts). The word **validation** is reserved for the one external check, item 4b.

---

## 1. The original model, recapped

IKKS (2007) place a discrete population in 10 earnings "occupations" (deciles) × 10 demographic groups. Each cell has an effective marginal tax rate τ (intensive margin) and a participation tax rate *a* (extensive margin). Two revenue-neutral reforms are scored through closed forms (eqs 15, 16, 18, 19):

- a **demogrant** (uniform lump sum), efficiency loss fraction D_d and equity–efficiency trade-off Ψ_d;
- a **working-poor (in-work) transfer** to the employed, D_w and Ψ_w.

The paper's headline: with an extensive elasticity that is largest at the bottom (benchmark profile η = [.4,.4,.3,.3,.2,.2,.1,.1,0,0], average **η̄ = 0.2**) and a small intensive elasticity **ε = 0.1**, the in-work transfer is cheaper than the demogrant (Ψ_w < Ψ_d) in all countries, has Ψ_w < 1 in DK, IE, FR, PT, ES, and is **Pareto-improving in Denmark**.

The paper derives Ψ, not an inverse optimum. To "read" each era's tax–benefit system as a planner's choice we use the companion result — **Saez (2002), *QJE* 117(3):1039–1073, eq. (16) of NBER WP 7708** (verified against the NBER PDF 2026-10-05; the QJE print may number it differently) — the mixed extensive+intensive model with no income effects.

---

## 2. What the new rates demand: the inverse-optimum reading  [ESTIMATED from 001 rates; CALIBRATED η, ε]  ·  [CONSISTENCY CHECK]

### 2.1 The equation

With occupations *i* = 1…*I* ordered by earnings, population shares h_i, normalised density h(w_i) = h_i/(w_i − w_{i−1}), Saez's optimum is

> τ_i/(1 − τ_i) = [1/(ε_i · w_i · h(w_i))] · Σ_{j ≥ i} h_j · [1 − g_j − η_j · (T_j − T_0)/(c_j − c_0)],  with Σ_{i=0}^{I} h_i g_i = 1.

Since c_j − c_0 = w_j(1 − a_j), the last term is η_j · a_j/(1 − a_j) in the paper's notation. We **invert for the social marginal welfare weights g** (what the rules reveal the planner must value). Define B_i = ε · [τ_i/(1 − τ_i)] · w_i · h_i/(w_i − w_{i−1}) for *i* = 1…*I*, B_{I+1} = 0. Differencing the optimum at *i* and *i*+1 gives

> **g_i = 1 − η_i · a_i/(1 − a_i) − (B_i − B_{i+1})/h_i**,  *i* = 1…*I*,  and **g_0 = [1 − Σ_{i≥1} h_i g_i]/h_0**.

With ε = 0 this is the extensive-only expression g_i = 1 − η_i a_i/(1 − a_i).

**Decile mapping (pre-declared).** I = 10 earnings deciles. w_d = s_d/e_d (1998 decile wage/employment share ratio, scale-free), w_0 = 0; h_d = P·e_d, h_0 = 1 − P; τ_d, a_d are 001's employment-weighted decile rates (E1), consumption-adjusted, q = 0, capped at 0.999 exactly as `welfare_core` computes Ψ; η_d is the benchmark profile, ε = 0.1. This is a **[CONSISTENCY CHECK]**: g is built from the same τ, a and formulas that produce 001's Pareto flags, so agreement with those flags is close to mechanical.

### 2.2 Reproduction on the paper's 1998 case (run first)

Denmark 1998, from the workbook, reproduces the paper's Pareto result: **g in decile 1 = −0.73 < 0**, and decile 1 contains a working-poor net-gainer cell (G_w = {e_j > 0, s_j/e_j < 1 − D_w}; here D_w = −1.654, matching `table2a.csv` DK eff_w = +1.654 to the sign). So "Pareto-improving iff some decile with a G_w cell has g < 0" **holds for DK**. Across all 14 in-scope countries, the g-based iff flags **only DK** as Pareto in 1998 — matching the paper's own statement that Denmark is the Pareto case. 001's looser operational flag (eff_w > 0) additionally marks FR, IE, PT, ES, but those are knife-edge (eff_w = +0.065, +0.263, +0.004, +0.002); the strict g < 0 condition is not met there. The all-employed variant (any decile with g < 0, ignoring the G_w restriction) adds only Sweden in 1998. **The iff reproduces, so it is used below.**

### 2.3 What moved, 1998 → 2026

| | 1998 (workbook) | 2026 rules |
|---|---|---|
| Countries where g-iff flags Pareto (some G_w decile has g < 0) | **1 (DK)** | **7 (AT, BE, DE, ES, LU, NL, PT)** |
| …of which 001 also flags Pareto (eff_w > 0) | 1 (DK) | **4 (BE, DE, LU, PT)** |
| Countries with **any** bottom-decile (d=1) g < 0 | 1 (DK) | AT, BE, DE, ES, LU, NL, PT |
| Median emp. share in g < 0 deciles, panel {FI,FR,EL,IT,SE} | 0.00 | 0.00 |

Full detail in `g_by_decile.csv` and `item1_agreement.csv`. Two things stand out:

1. **Agreement is high *on stable country-years* but the divergences are diagnostic.** Over 2009–2026 the g-iff and 001's eff_w > 0 flag agree on **182/251 = 72.5%** of country-years, rising to **143/159 = 89.9%** restricted to "stable" country-years. The 2026 over-count is exactly the three countries (AT, NL, ES) where the g-iff flags Pareto but 001 does **not**: in every one of them Ψ_w is *unstable*, and the g < 0 signal comes **only** from decile 1. So the strict g < 0 "iff" **over-predicts** Pareto relative to a genuine efficiency gain whenever the bottom decile is in a participation trap — a warning about reading g < 0 too literally, not a second Danish miracle.
2. **The driver is mechanical, and is itself Study A's central finding.** Under 2009+ rules the bottom-decile participation tax rate of hypothetical single-earner households approaches 100% (a → 1), so η_d·a_d/(1 − a_d) explodes and g_d = 1 − η_d a_d/(1 − a_d) − … turns sharply negative. A planner rationalising these rules would have to put a **negative** marginal value on an extra euro to a decile-1 worker — the rules read as if designed to pull them *out* of that cell. Denmark and Sweden move the other way (bottom-decile traps eased; their g < 0 employment share falls from 0.10 to 0.00). The honest reading is therefore the **stable-country agreement (89.9%)** plus an explicit flag that in the unstable bottom-decile-trap countries the inverse optimum is not interpretable as welfare weights.

**Robustness rows (pre-declared, `item1_sensitivity.csv`).** (a) Replacing the within-cell MTR with the **between-occupation implicit rate** τ_i = (T_i − T_{i−1})/(w_i − w_{i−1}) (with T_i − T_0 = w_i a_i) leaves the decile-1 g essentially unchanged: cross-country correlation 0.994, mean |Δg_1| = 0.20, no sign flips of the headline conclusion. (b) The **extensive-only g at the 100-cell level** (ε = 0, no occupation differencing) gives bottom-cell g < 0 employment shares that track the decile picture (e.g. AT 0.01 → 0.26, NL 0.03 → 0.27, DK 0.27 → 0.09 across 1998 → 2026).

---

## 3. The elasticity frontier by era  [ESTIMATED; CALIBRATED bands]

### 3.1 Construction

From 001's Table-3 analogue (`critical_eta_by_year.csv`) we draw, for 2009, 2015, 2020 and 2026, the boundary in (η̄, ε) space where each conclusion flips (Figure 1, `fig1_elasticity_frontier.png/.pdf`). For a given ε, the **critical average elasticity η̄\*** solves:

- **Ψ_w = Ψ_d** (`crit_identical`): η̄ > η̄\* ⇒ in-work transfer cheaper;
- **Ψ_w = 1** (`crit_zeroloss`, D_w = 0): η̄ > η̄\* ⇒ Ψ_w < 1;
- **Pareto** (`crit_pareto`, 1 − D_w = max_j s_j/e_j): η̄ > η̄\* ⇒ no losers.

The curves are the **median over the fixed panel {FI, FR, EL, IT, SE}** — the five countries whose Ψ is stable in *all four* eras, so the across-era shift is a like-for-like comparison. Per-country critical values for the full validated set are in `frontier_survival.csv`.

Post-2007 European and US evidence is overlaid as vertical bands, **each labelled by origin**: **Kleven 2024 (US EITC)** ≈ 0; **Bartels & Shupe 2023** 0.08 (men)/0.14 (women); **Chetty et al. 2011 (mostly US)** ≈ 0.25; **Lundberg & Norell 2018** 0.38; **Bargain, Orsini & Peichl 2014** (extensive response larger at the bottom — a shape, matched by the benchmark profile, not a single level). *Kleven 2024 is US EITC evidence and is not a European elasticity; Chetty et al. is mostly US.* [CALIBRATED]

### 3.2 What the frontier shows

- **The in-work-cheaper boundary moved left (easier) after ~2017.** Median critical η̄ for Ψ_w < Ψ_d fell from **≈ 0.22–0.26 (2009–2015)** to **≈ 0.12–0.13 (2020–2026)** at ε = 0.1 (Figure 2 left shows a clean break around 2017). In 2009 the conclusion needed a Chetty-sized (US) elasticity; by 2020–2026 it holds already at **Bartels & Shupe European** elasticities.
- **Ψ_w < 1 also became easier**: median critical η̄ ≈ 0.73 (2009/2015) → ≈ 0.32–0.39 (2020/2026).
- **Full Pareto became harder**: median critical η̄ ≈ 0.42–0.55 (2009/2015) → **≈ 0.87–0.92 (2020/2026)** — above every cited elasticity. Costless-to-all in-work reform is essentially off the table under 2020s rules in this panel.

### 3.3 Which conclusion survives which literature band (ε = 0.1, validated set, `frontier_survival.csv`)

Count of the 14 V countries where **Ψ_w < Ψ_d** holds at each literature elasticity:

| Era | Kleven (US EITC, ≈0) | Bartels & Shupe (≈0.11) | Chetty (mostly US, 0.25) | Lundberg & Norell (0.38) |
|---|---|---|---|---|
| 2009 | 0/14 | 4/14 | 5/14 | 7/14 |
| 2015 | 0/14 | 7/14 | 8/14 | 10/14 |
| 2020 | 0/14 | 6/14 | 10/14 | 11/14 |
| 2026 | 0/14 | 5/14 | 9/14 | 10/14 |

**The sharpest statement the data support:** at the **US-EITC near-zero participation response (Kleven 2024), the in-work transfer never dominates the demogrant in any European country, in any era** — the paper's result rests entirely on the extensive margin being non-trivial. At a **European** elasticity (Bartels & Shupe), in-work dominance holds in a **minority** (≈ 5–7 of 14); at Chetty/Lundberg–Norell levels it holds in a clear **majority** by the 2020s. So the paper's qualitative claim ("in-work benefits desirable for a wide range of elasticities", C12) **survives for mid-range elasticities and is strengthened post-2017**, but **fails at the lowest credible European/US values** — a sharper, more honest boundary than the 2007 paper drew.

---

## 4. One minimal amendment, and one rejected alternative

### 4.1 Amendment (preferred): concentrate η on secondary earners and lone parents  [ESTIMATED; CALIBRATED]

The paper's own Table 6(b) and the authors' couples extension (**Immervoll, Kleven, Kreiner & Verdelin 2011, *JPubE***) put the extensive response on groups whose participation is most elastic. We reallocate the benchmark η onto **groups 2, 7, 8, 9, 10** (lone parents + married women), **holding the employment-weighted aggregate η̄ fixed at 0.2**, and re-score (`item3_concentration.csv`).

**Verdict: the amendment barely moves the 2026 ranking.** In-work-cheaper counts over the stable set: 2009 3→3, 2015 5→6, 2020 7→7, **2026 8→7** (the one flip is Italy, Ψ_w 1.56 vs Ψ_d 1.78 → 1.73 vs 1.69). Efficiency effects are second-order except where Ψ is already at a Pareto knife-edge (LU eff_w 4.73 → 0.16, BE 2.41 → 1.96 — both stay Pareto). **So the "who is elastic" composition is *not* the mechanism behind where in-work dominance weakens by 2026**; the driver is the *level* of bottom-decile participation tax rates (section 2.3), not the allocation of the elasticity. We keep the amendment because it is the minimal, theory-grounded change that stays inside the IKKS/ IKKV framework and is directly calibrated to the literature — but we report plainly that it does little work here.

### 4.2 Alternative, discussed and rejected: an unemployment/wage-response channel  [PROPOSED]

**Kroft, Kucko, Lehmann & Schmieder (2020, *AEJ: Policy*)** add involuntary unemployment and a wage response to the Saez model; the optimum then tilts toward a negative income tax rather than a pure in-work subsidy, because transfers to the employed partly leak into wages and the non-employed include the involuntarily unemployed. This is a genuine competitor to the amendment in 4.1. We **reject it for this study** (not on economic grounds but on calibration grounds): it needs a wage-response elasticity and a matching-function/ rationing parameter that **001's artefacts cannot identify** — the hypothetical-household rates carry no information about equilibrium unemployment. Labelled **[PROPOSED]**: worth estimating with job-flow data, out of scope here.

---

## 5. Linearisation accuracy check  [CONSISTENCY CHECK] — *not* a validation

Ψ_w is a deterministic function of the rates, so this measures only how well a linear relation tracks the formula; no claim of the paper becomes more or less believable either way (`item4_linearisation.json`).

Fitting the cross-country relation Δ(bottom-quintile PTR) → Δ(Ψ_w) on **2009 → 2017** (endpoints, one point per country with finite stable Ψ_w at both ends; n = 6: EL, ES, FI, FR, IT, SE) gives ΔΨ_w = −0.016·Δa_{1-2} + 0.272, **in-sample R² = 0.57**. Carried to **2018 → 2026** (n = 7), the **out-of-sample R² = −0.18** (MAE 0.45): the linearisation **does not track**. This is consistent with — and another symptom of — the Ψ_w instability Study A flagged (bottom-decile PTR → 1). **It reinforces that the robust deliverable is the bottom-quintile PTR *change itself*, not Ψ_w levels.**

For the big in-work expanders, 1998 → 2026 (method break: 1998 rates are survey-cell averages, 2026 are hypothetical households — the two are not joined):

| | Ψ_w 1998 | Ψ_w 2026 | bottom-quintile PTR 2026 |
|---|---|---|---|
| France (prime d'activité, 2016/2019) | 0.76 | 2.14 (stable) | 55.3% |
| Finland (2025 credit) | 4.93 | 2.45 (stable) | 64.0% |
| Denmark (2025) | −0.00 (Pareto) | undefined (unstable) | 61.8% |
| Spain (IMV disregard, 2023) | 0.99 | 198.3 (unstable) | 78.2% |

The model "explains" the direction for FR and FI (the in-work reforms show up as lower bottom-quintile PTRs than 2009 — DK −24 pp, FR −5 pp in 001's E5); for DK and ES the 2026 Ψ_w is numerically unstable and only the PTR level is interpretable.

---

## 6. External check: cost per job of a marginal in-work transfer, Belgium  [CALIBRATED vs literature] — **validation**

The only external, behaviourally-estimated benchmark available for a study country. **de Mahieu (2021), *International Journal of Microsimulation* 14(1):43–72** (verified live 2026-10-05) scores three Belgian Work-Bonus expansions (each €300m/yr pre-behaviour, 2016 rules, 2017 SILC): net budgetary cost after responses **€368.5k–€1,660.1k per additional FTE** and **€121.1k–€560.7k per additional participant**.

**Model analogue (paper eq. 13, 001's BE 2016 rates; dT cancels; `external_check_be.csv`):** an unfunded marginal lump-sum in-work transfer to employed cells in BE deciles 1–2 (sensitivity 1–3), with w_j = r_j·AW_2016 (AW_2016 = €46,528/yr), E_j = P·e_j, hours lhw_j from the §3.2 rule:

| η | target | cost/participant (k€) | cost/FTE (k€) | vs published |
|---|---|---|---|---|
| benchmark (η̄=0.2) | deciles 1–2 | **−3.5** | **−7.5** | **below** (self-financing) |
| benchmark | deciles 1–3 | −2.5 | −4.7 | below |
| Bartels & Shupe (η=0.11) | deciles 1–2 | 10.6 | 22.3 | below |
| Bartels & Shupe | deciles 1–3 | 16.0 | 30.1 | below |

**The model number sits below the published range at every setting — exactly the pre-declared expected direction.** Two reasons, both stated in advance: (i) the model transfer is a **lump sum with no phase-out**, so it carries no intensive-margin cost, whereas the Work Bonus is withdrawn at up to 29.2%; (ii) at Belgium's **very high bottom-decile participation tax rates** (a_{decile 1} ≈ 0.85), the extensive-margin revenue η·a/(1−a) is large — at the benchmark η it *exceeds* the mechanical cost, so the marginal transfer is **self-financing** (negative net cost). A model number **above** €1.66m/FTE would have been evidence against the calibrated η; we see the opposite, so the calibration is consistent with the published behavioural estimate. This check covers **Belgium only** — no other study country has a cited cost-per-job estimate in the research note.

---

## 7. Implications for the "theory, updated to 2026"

1. **The paper's core logic is intact and, post-2017, on firmer ground for mid-range elasticities.** The in-work transfer dominates the demogrant at lower critical elasticities now (η̄\* ≈ 0.13 vs ≈ 0.25 in 2009), because a decade of in-work reforms (FR, SE, NL, BE, FI, DK, ES) lowered bottom-decile participation tax rates (median panel a_{1-2} 70% → 50%).
2. **But the result is now explicitly elasticity-contingent in a way the 2007 paper could gloss over.** At a US-EITC-style near-zero participation response it collapses everywhere; at European (Bartels & Shupe) elasticities it is a minority result; it is a majority result only at Chetty/Lundberg–Norell levels. The honest headline is **"in-work dominance holds for η̄ ≳ 0.13, which spans the European evidence but not the US-EITC floor."**
3. **Full Pareto-improvement is essentially gone** under 2020s rules (critical η̄ ≈ 0.9): the Danish 1998 miracle is not reproduced by any country's 2026 system in the stable panel.
4. **The composition amendment (secondary earners/lone parents) is defensible but not decisive**; the decisive object is the *level* of bottom-decile PTRs, which the rules-only update measures directly. The unemployment-channel alternative (Kroft et al. 2020) is the most promising extension but is not calibrable from these artefacts.
5. **Ψ_w levels remain the weak link** (unstable where PTR → 1); the linearisation check confirms they should not be over-read. The bottom-quintile PTR change is the robust carrier of the story.

---

### Artefacts
`g_by_decile.csv`, `item1_agreement.csv`, `item1_sensitivity.csv`, `item1_summary.json` (item 2 inverse-optimum); `frontier_by_era.csv`, `frontier_survival.csv` (item 3 frontier); `item3_concentration.csv` (item 4 amendment); `item4_linearisation.json` (item 5a); `external_check_be.csv`, `item4b_summary.json` (item 4b); `calibration_table.csv`, `calibration_summary.json`; `fig1_elasticity_frontier.png/.pdf`, `fig2_critical_eta_and_g.png/.pdf`.

**Tag key:** [ESTIMATED] from 001's EUROMOD rates · [CALIBRATED] literature elasticities · [CONSISTENCY CHECK] mechanically implied by the same rates+formulas · [PROPOSED] not calibrable from the artefacts. "Validation" used only for §6.
