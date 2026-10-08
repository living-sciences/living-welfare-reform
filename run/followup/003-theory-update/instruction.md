# LAUNCH SCOPE: Execute ONLY Study B (the 002 theory-update study). Study A sections are context; its completed artifacts are inputs, do not re-run them.

# Follow-up studies: Welfare reform in Europe, updated to 2026 policy rules

DRAFT for the 2b judge gate, **revision 1** (2026-10-05) against judge items I1-I10 in `verdicts/phase2b-judge.md`; the changelog is at the bottom. Written 2026-10-05 from `recency-research.md` (same directory). Every source below was verified live on 2026-10-05 unless marked UNVERIFIED.

**Launch parameters** (cross-cutting requirement 1):
- `001-living-update`: `veritas followup <run_dir> --instruction-file <001.md> --name living-update --timeout 43200`.
- Continuation, only if 001's session ends before its deliverables are complete: `--name living-update-cont --timeout 43200` → `003-living-update-cont` (§10).
- `002-theory-update`: `--name theory-update --timeout 7200`, launched only after 001 (or its continuation) has finished.

This file holds the standard pair:
- **Study A, `001-living-update`**: §§0-10;
- **Study B, `002-theory-update`**: §11.

Each is launched with its own instruction file cut from this spec.

---

## Workspace staging (orchestrator does this before launch; the study agent does its first action)

**Orchestrator.** Copy (do not symlink across mounts) `corpus/immervoll-etal-2007-welfare-reform/extension-assets/` into the run directory as `run/followup_staging/shared-data/`, so it is visible in the container at `/workspace/eval/followup_staging/shared-data/`. Also copy `data/EUROMOD_RELEASES_J2.0+.zip` (the stable model, for gate 4) and `data/EM_statistics_I5.0+.xlsx`. Total is about 430 MB. **Do not unzip anything into the corpus**: /data is at 99%.

**Study agent, FIRST action:**
1. Hardlink or symlink `shared-data/` into your `workspace/`.
2. Verify every line of `shared-data/SHA256SUMS.txt` with `sha256sum -c`.
3. Spot-load one file per subfolder.

Do not read other studies under `followup/`; this study stands alone.

**EUROMOD extraction rule.**
- Extract the model **per country, at run time, to container-local scratch** (`/tmp/em/`), never into the workspace: `unzip <zip> "EUROMOD_RELEASES_J2.54+/XMLParam/Countries/<CC>/*" "EUROMOD_RELEASES_J2.54+/XMLParam/Config/*" "EUROMOD_RELEASES_J2.54+/XMLParam/AddOns/MTR/*" "EUROMOD_RELEASES_J2.54+/XMLParam/AddOns/NRR/*" "EUROMOD_RELEASES_J2.54+/Input/<CC>_training_data.txt"`, then `mkdir Output`.
- Delete each country's extraction when that country is done.
- Never write EUROMOD output .txt files into the workspace. Aggregate to CSV in memory.

## 1. The question and the design

The paper (EJ 2007) computed effective marginal tax rates τ and participation tax rates a with EUROMOD under **1998** tax-benefit rules, for 10 earnings deciles × 10 family types in the EU-15. Plugged into closed-form formulas, it found:
- a revenue-neutral **working-poor (in-work) transfer** is far cheaper than a **demogrant**;
- the working-poor transfer is Pareto-improving in Denmark, with Ψ_w < 1 in DK, IE, FR, PT and ES.

Since then most of these countries have built in-work benefits (FR prime d'activité, SE jobbskatteavdrag, NL arbeidskorting, BE work bonus, FI, DK and IT credits, DE Midijob, ES IMV disregard). The question:

> **Under each year's actual tax-benefit rules from 2009 to 2026, does the paper's ranking still hold? How large is each reform's equity-efficiency trade-off now, and how did the bottom-decile participation tax rates that drive it move?**

Design: a **policy-rules-only update**. Hold the paper's 1998 cell structure fixed and change only the rules.
- **Fixed from 1998** (`EUROMOD.xls`, via the replication's loader): wage shares s_j, employment shares e_j, the participation rate P, and each cell's relative earnings position r_j = s_j/e_j.
- **Recomputed for each policy year t**: τ_j,t and a_j,t, from EUROMOD **J2.54+ (beta, Sept 2026)** run on **hypothetical households** written directly in EUROMOD hhot input format.
- **Then**: the replication's own formula layer, eqs (15), (16), (18), (19).

What moves in the results is therefore the effect of tax-benefit rules, not of changing populations.

- **Policy years**: **2009-2026**, 18 years. 2009 is the first year with `<CC>_YYYY_hhot` dataset configs. Ireland has no 2021 hhot config: leave it **missing**, never interpolate.
- **Countries**: the 14 pre-2004 members still in EUROMOD: AT, BE, DK, FI, FR, DE, EL (paper "GR"), IE, IT, LU, NL, PT, ES, SE. Paper codes in the workbook: GE = DE, IR = IE, SP = ES, SW = SE.
- **UK is out of scope** (§9).

**HARD PROHIBITIONS:**
1. No EU-SILC or other representative microdata. EUROMOD `training_data` is synthetic and may be used **only** for the gate-0 smoke test, never as evidence.
2. No change to the paper's formulas or benchmark elasticities in the headline. Alternatives belong only in the pre-declared variants (§5) and in Study B.
3. No hand-typed tax rates, benefit amounts or tax parameters. Every τ and a comes from a EUROMOD run in this session.
4. Do not edit anything in `run/replication/`. Copy the code you reuse into `workspace/` and fix the two audited defects there (§2.2).
5. No fetches beyond the endpoints in §7, and those only if a staged file fails its checksum. **Exception, the gate-0 install endpoints only**, which are fetched once to install the toolchain and for nothing else:
   - `https://dot.net/v1/dotnet-install.sh` and the .NET download hosts that script pulls the runtime from (`builds.dotnet.microsoft.com`, `dotnetcli.azureedge.net`);
   - PyPI, for `euromod==0.4.0` and `pandas` and their dependencies (`pypi.org`, `files.pythonhosted.org`).

## 2. Claims being updated (paper values; read the replicated values from disk, never from memory)

Original-side numbers must be read from `run/replication/codebase/results/table2a.csv`, `table2b.csv`, `table3.csv` and `figures/tax_rates_by_decile.csv`. The values below are for orientation only.

- **C2 (PTR/MTR profiles, Figs 1-2).** Consumption-adjusted PTR is highest at the bottom in DK (84% in decile 1) and SE (74%), low at the bottom in GR (33%), LU (40%) and ES (45%), and flat at 57-62% in NL.
  - Note the replication's Figure-1 bug (A1): use the **With Consumption Taxes** columns 5/6 of the `Tax-Benefit Data_1998` sheet.
- **C4 (Table 2a, demogrant)**: Ψ_d is 2-4 for most countries, DK 25.25, SE 8.35, FI 6.17; efficiency between −0.19 (ES) and −0.82 (DK).
- **C5 (Table 2a, working-poor)**: Ψ_w ≈ 1; Pareto-improving in DK (efficiency +1.65); Ψ_w < 1 in DK, IE (0.39), FR (0.76), PT (0.99) and ES (0.99); FI 4.93 and SE 4.36 are the exceptions.
- **C6 (Table 2b, η = 0)**: the ranking flips toward the demogrant.
- **C7 (Table 3)**: critical average η for (a) Ψ_w = Ψ_d is 0.03-0.18; for (b) Ψ_w = 1 it is 0.10-0.45; for (c) Pareto it is DK 0.20 … GR 1.15.
- **C12 (qualitative)**: in-work benefits are desirable for a wide range of elasticities.

**Not updated, listed as caveats:**
- C1/Table 1 (benefit shares of income);
- C3/Fig 3 (P90/P10 from microdata);
- C8 with-microdata no-UB rates. V4 (§5) gives a hypothetical-household analogue, labelled as such;
- C10 dispersion-based gainer shares by family-income decile (Table 7 cols 3-12);
- C9 hours-elasticity table: recomputed for 2026 only, as a robustness row.

## 3. Constructing τ_j,t and a_j,t (the EUROMOD step)

### 3.1 Households for the 10 paper groups

The groups (paper fn. 10):
1. singles, no children;
2. lone parents;
3. married men, no children, working spouse;
4. married men, no children, non-working spouse;
5. married men, children, working spouse;
6. married men, children, non-working spouse;
7. married women, no children, working spouse;
8. married women, no children, non-working spouse;
9. married women, children, working spouse;
10. married women, children, non-working spouse.

Pre-declared conventions:
- **Ages**: reference person 40, spouse 38. **Children**: two, aged 4 and 6 (the OECD TaxBEN convention, so gate 3 compares like with like). Sensitivity V6: one child aged 6.
- **Gender**: group 1 is evaluated twice (male and female) and averaged by ratio of sums; group 2 is female.
- **Marital status**: married for groups 3-10 (dms married code, cohabiting partner linked by idpartner).
- **Working spouse's earnings**: the spreadsheet's group-level mean relative earnings of the opposite-sex working-spouse groups, matched on children:
  - for groups 3/5, use the group 7/9 mean r̄ = Σ_d s / Σ_d e;
  - for groups 7/9, use the group 3/5 mean.
  - The spouse's earnings are held fixed while the reference person's earnings are perturbed.
- **Non-working spouse**: no earnings, inactive status, not eligible for UB.
- **Housing**: rent `xhcrt` = 0 in the headline. V5: rent = 20% of AW_t (the OECD convention).
- **Work history** (needed for UB eligibility): liwwh = 180; liwwh12_h = 12; liwwh24_h = 24; liwwhny10_h = 120; liwwhny15_h = 180; lim_h = 1 where defined. Start from the full list of `_h` variables in `XMLParam/Config/VARCONFIG.xml` and `HHoT_baseline.xml` (staged) and record what you set.
- **Start every row** from the country's `training_data` column set, zero-filled, plus all `_h` extension variables. HHoT itself is a Windows UI plug-in and is not used.

### 3.2 Earnings placement (pre-declared)

y_{g,d,t,k} = r_{g,d} × AW_t × k, with grid k ∈ {0.8, 0.9, 1.0, 1.1, 1.2}. All amounts are monthly: annual ÷ 12.
- r_{g,d} = s_{g,d}/e_{g,d} comes from the 1998 workbook. Empty cells (e = 0) get weight 0 and are not simulated.
- AW_t = Eurostat `earn_nt_net` GRS, P1_NCH_AW100, national currency, staged: `shared-data/earnings/earn_nt_net_AW100_GRS_NAC.json`. It covers 2000-2025 for all 14 countries.
- **2026** = AW_2025 × the J2.54+ 2026/2025 uprating index for employment income, read from the country XML's uprating factors (log the factor). If it cannot be identified, use AW_2025 and flag it.
- The paper's deciles include employer SSC. We treat r as a gross-earnings ratio, an approximation where employer SSC is non-proportional (FR/BE low-wage relief, caps). **Sensitivity for 2025 only:** invert so that gross + employer SSC = r × (AW + employer SSC at AW).

**Hours**: lhw = clamp(40 × y/(0.5 × AW_t), 8, 40). Rationale: decile-1 workers are full-year but mostly part-time (r ≈ 0.2). Hours matter for WFP-type rules (IE 19 h) and Midijob. Sensitivity: lhw = 40.

**Country input conventions** (silent failure risk, proven in Phase 2a):
- Earnings go in the variable the country's `ils_earns` actually reads. **FR uses `yem00`**; `yem` alone gives zero earnings. EL may use `yemre` (UNVERIFIED).
- Before any production run, for each country, probe one household: ils_earns must equal the input earnings. Log the mapping in `results/input_conventions.csv`.
- AT irregular pay (13th/14th salary): headline puts all earnings in `yem`; the split yem 12/14 + yemxp 2/14 is logged as a probe. In Phase 2a it moved AT PTR by about 1 pp.

### 3.3 Rates (the paper's definitions, labour-cost basis)

For each household, run (same system, same dataset `<CC>_YYYY_hhot`):
- **base**;
- **+3%**: the reference person's earnings × 1.03;
- **zero, no UB**: reference person's earnings 0, status inactive, no unemployment history;
- **zero, with UB**: via the **NRR add-on**, `addons=[('NRR','NRR_<CC>')]`. For J2.54+ this is the preferred route. `HHoT_un` (switch) is the fallback where NRR yields no UB.
  - **Required semantics (the paper's a_UB):** only the **reference person's** earnings are zeroed and only the reference person is simulated as a UB claimant. A working spouse keeps her or his earnings.
  - **Couples probe, before any production run, one per country** (2025 system, and 2009 for countries where 2025 yields no UB): one two-earner household, group 5 (reference person at 1.0 × AW_t, spouse at the §3.1 working-spouse earnings). Read the NRR output per person. Pass if (i) the spouse's `ils_earns` in the a_UB scenario equals the base-run value, and (ii) the spouse's UB (`bunct*`) is zero while the reference person's is not (or both are zero, which is the separate "no UB" case below).
  - **If NRR zeros both earners or simulates UB for both**: use the NRR add-on's per-person scenario outputs and keep only the reference person's scenario; if the add-on does not expose per-person scenarios, build the a_UB row with the `HHoT_un` route (reference person unemployed, spouse unchanged). Apply the choice to **all years** of that country.
  - Log, per country: the route used, the spouse's earnings before/after, and both persons' UB, in `results/input_conventions.csv` (columns `nrr_route`, `nrr_spouse_earns_base`, `nrr_spouse_earns_ub`, `nrr_ub_ref`, `nrr_ub_spouse`).

Then:
- τ = 1 − ΣΔ(ils_dispy) / ΣΔ(ils_earns + ils_sicer)
- a_noUB = 1 − Σ(dispy_base − dispy_zeroNoUB) / Σ(earns + sicer)
- a_UB likewise.

The sums run over the 5-point grid: the cell value is a **ratio of sums**, which avoids the τ ≥ 1 kinks the paper warns about in fn. 11.

**Employer-SSC probe (the labour-cost basis divides by earns + sicer).** Before production, for each country and for 2009 and 2025, run S_C0 at 0.67 and 1.0 × AW_t and log `ils_sicer / ils_earns` in `results/input_conventions.csv` (`sicer_ratio_AW67`, `sicer_ratio_AW100`).
- Plausible means 0 < ratio < 0.45. **Denmark is the one expected exception**: its employer contributions are near zero by design, so DK passes with any ratio in [0, 0.03] and that is noted.
- A zero ratio outside DK, or any ratio ≥ 0.45, means the employer-SSC output is not being produced as assumed. Check the variable mapping and fix it **uniformly across years**. If it cannot be fixed, compute that country's τ and a on the **gross basis** (sicer dropped from both formulas), flag every row of that country `gross_basis`, and say so in findings.md.

Combine: a = q × a_UB + (1 − q) × a_noUB, with **q fixed at paper Table A3 col 2** (1998): AT 9.0, BE 21.1, DK 21.4, FI 28.1, FR 31.4, DE 13.8, GR 9.7, IE 8.8, IT 7.3, LU 4.3, NL 12.7, PT 14.1, ES 23.1, SE 19.0.

Consumption adjustment: (TR + CTR_t)/(1 + CTR_t), where CTR_t = CTR_1998,xls + (F_t − F_1998), and
- CTR_1998,xls is the workbook value (AT 20.12, BE 17.35, DK 35.96, FI 29.90, FR 19.90, DE 15.61, GR 16.31, IE 26.12, IT 15.42, LU 23.74, NL 19.39, PT 22.70, ES 14.66, SE 20.53);
- F is the Mendoza ratio (D211 + D214)/(P31_S14 + P3_S13 − D1PAY_S13 − D211 − D214) from the staged Eurostat files.

The level formula does **not** reproduce the workbook (AT 24.2 vs 20.1), hence the additive splice. For 2025-2026, if national accounts stop at 2024 or 2025, carry the last value forward and flag it.

**MTR add-on cross-check**: now **gate 3c** (§6), run for all 14 countries in 2010 and 2025. The conversion arithmetic is written out there.

### 3.4 Formula layer

Copy `welfare_core.py` and the Table-3 driver into `workspace/`. Feed:
- **fixed 1998**: s_j, e_j, P;
- **new**: τ_j,t and a_j,t.

Benchmark: ε = 0.1, η = [.4, .4, .3, .3, .2, .2, .1, .1, 0, 0] by decile. Fix audit A2 in your copy: when the demogrant has no gainers (den ≤ 0) print "No Gainers" (null), as the paper does.

## 4. Headline estimands (pre-declared)

For each country c and policy year t ∈ 2009…2026:
- **E1**: decile profiles of τ_d,t and a_d,t, employment-weighted over groups with the 1998 e_j. Plus the bottom-quintile PTR a_{1-2},t.
- **E2**: Ψ_d,t, Ψ_w,t, efficiency −D_d,t and −D_w,t at the benchmark elasticities; the Pareto flag (no losers) and No-Gainers flags.
- **E3**: the cross-country count of {Ψ_w < Ψ_d}, {Ψ_w < 1} and {Pareto}, per year, over the **gate-3 validated set** V (countries passing the no-UB leg, §6), always printed as "k of n" with n = |V|. Reported twice: under the mixed-q headline (a = q·a_UB + (1−q)·a_noUB, with q = 0 only for countries that failed the UB leg) and under V4 (q = 0 for all countries in V).
- **E4**: Table-3 critical average η, all three columns, per country × year.
- **E5**: change 2009 → 2026 in a_{1-2}, Ψ_w and Ψ_d, with the countries ranked, over the **change-gate set** V_Δ ⊆ V (countries passing gate 3b). Countries in V but not V_Δ keep their levels in E1-E4 and are listed beside E5 as "level-validated, change not validated".

**Denominator and baseline rules (pre-declared):**
1. **1998 baseline on the same set.** Every 1998 comparison number (from `table2a.csv`, `table3.csv`, `figures/tax_rates_by_decile.csv`) is computed on exactly the countries of the set it is compared with: V for E2-E4 counts, V_Δ for E5. Map paper codes GE→DE, IR→IE, SP→ES, SW→SE, GR→EL; **UK is never in the baseline**. Print both sides as "k of n", e.g. "1998: 5 of 13 with Ψ_w < 1; 2026: k of 13". The paper's own 15-country statements may be quoted only as the paper's statements, never as the comparison.
2. **Minimum coverage.** If |V| < 10, the headline becomes an honest partial: "validated in n of 14", and E3 counts are **not** compared with the paper's 15-country statements anywhere (report, card, figures); only the same-set 1998 baseline of rule 1 is shown.
3. **Which q regime is the headline.** If **4 or more** countries in V fall back to q = 0 (failed UB leg or no UB simulated by any route), **V4 becomes the headline** for E2-E5 and for the card, and the mixed-q version moves to the secondary table, because a count mixing q regimes is not comparable across countries. With 3 or fewer fallbacks, the mixed-q version is the headline and V4 is printed next to it. The 1998 baseline follows the same regime. `EUROMOD.xls` holds only the combined (mixed-q) a_j, so under a V4 headline the 1998 Ψ baseline is the paper's own **Table 5(b)** ("without benefits") Ψ_d/Ψ_w, transcribed into `results/baseline_1998_noUB.csv` with page reference (read signs from `paper.pdf`: `paper.txt` drops the minus signs) and labelled "paper-reported, not recomputed", restricted to the same set V. The 1998 bottom-quintile PTR has no q = 0 version in the workbook; under a V4 headline the card says "no same-definition 1998 baseline" for that metric instead of pairing it with the mixed-q level.

The 1998 paper values appear as a **separately marked point**, never joined by a line to 2009. The 1998 rates came from survey microdata averaged within cells, while 2009+ rates come from hypothetical households, so the 1998 → 2009 step mixes method and rules. Say so in findings.md. The headline over-time claim is the 2009 → 2026 change.

## 5. Pre-declared variants (secondary, labelled)

- **V1**: CTR fixed at the 1998 workbook value (isolates income-tax-and-benefit rules).
- **V2**: q_t and P_t from Eurostat LFS: `lfsa_ugadra` × `lfsa_ugad` / non-employed from `lfsa_pganws`, ages 20-59 = Y20-24 + Y25-59. IE has no benefit-receipt data before 2024, so it stays at 1998 q, flagged. This q_t counts benefits *or* assistance and so overstates the paper's UB-entitled concept; say so.
- **V3**: dispersion update. Stretch log r_d around the median so that the implied P90/P10 equals the SES vintage nearest t (2006/2010/2014/2018/2022, staged `earn_ses*_adeci`; hold the last vintage forward). Report SES P90/P10 by country as the public analogue of the blocked Fig 3.
- **V4**: no-UB panel (q = 0), the hypothetical-household analogue of paper Table 5b. It is reported for every country that passes the gate-3 no-UB check, even if the UB leg fails.
- **V5**: rent = 20% AW.
- **V6**: one child.
- **V7**: 2025 computed on J2.0+ stable instead of the J2.54+ beta (also gate 4).

**Which variants need new EUROMOD runs, and for which years (pre-declared).**
- Formula-layer only, all 18 years, no new runs: V1, V2, V4.
- Already a gate: V7 (gate 4, 2025 only).
- **New EUROMOD runs, restricted to t ∈ {2009, 2015, 2020, 2026}**: V3 (dispersion), V5 (rent), V6 (one child), and the lhw = 40 hours sensitivity. Each is shown as four points beside the 18-year headline line, never as its own line.
- **Employer-SSC inversion**: 2025 only, as before.

## 6. Validation gates (in order; a failure stops or downgrades as stated, never silently)

0. **Environment.** The container has no Mono and no .NET (verified 2026-10-05).
   - Install the .NET 8 runtime in user space (`curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --runtime dotnet --channel 8.0 --install-dir $HOME/.dotnet`).
   - Set `DOTNET_ROOT` and `PYTHONNET_RUNTIME=coreclr`.
   - `uv venv` + `uv pip install euromod==0.4.0 pandas`.
   - Smoke test: AT_2025 on `AT_training_data` must finish "with 0 errors", with about 7,482 persons and 436 variables. It took 13.5 s in Phase 2a. The recipe is staged as `prototype/gate0_container_recipe.sh`.
   - If the install fails (no network, glibc mismatch), try Mono only if it is installable without root. Otherwise **stop and report gate 0 failed**. Do not substitute any other model.
1. **Anchor.** Reproduce paper Table 2(a), all 15 countries × 4 columns to 2 decimals, from the workbook through your copied `welfare_core.py`. Compare with `run/replication/codebase/results/table2a.csv` and with the paper values in §2. Must be exact. This passed in the replication and in the Phase-0 prep check.
2. **Plumbing anchor.** Pass the workbook's 1998 τ/a arrays through your *new* aggregation code path (the one that will receive EUROMOD rates). It must reproduce gate 1 identically.
3. **Input-convention gate, levels (OECD TaxBEN benchmark).** Staged: `benchmarks/oecd_taxben_DF_PTRSA_EU15.csv` and `…DF_PTRUB_EU15.csv`. Columns: `REF_AREA` (ISO3), `INCOME_CURR` (earnings of the person taking up work: `AW67`, `AW100`, `MINW`), `HOUSEHOLD_TYPE` (`S_C0`, `S_C2`, `C_C0`, `C_C2`; children aged 4 and 6), `INCOME_PART` (partner's earnings: `_Z` for singles, `NOEARN_UNEMP_WO_CONBEN`, `AW67`, `AW100`, `MINW`), `UNEMP_DURATION`, `SOC_ASS_BENEFIT`, `HOUSE_BENEFIT`, `TEMP_INTOWORK_BENEFIT`, `TIME_PERIOD`, `OBS_VALUE` (PTR, %).
   - **Gate years** t_G ∈ {2010, 2015, 2020, 2025}. **DK and NL have no 2025 rows in either file** (both end in 2024, verified 2026-10-05), so for DK and NL the last gate year is **2024**. Never fill a missing benchmark year.
   - **Cells**, computed on a **gross-earnings basis** with households built exactly as in §3.1 (ages, children 4 and 6, history variables, earnings variable from `input_conventions.csv`):

     | Cell | `HOUSEHOLD_TYPE` | `INCOME_PART` | Our household |
     |---|---|---|---|
     | single | S_C0 | `_Z` | group 1 (male; female logged) |
     | lone parent | **S_C2** | `_Z` | group 2 (female) |
     | one-earner couple | C_C2 | `NOEARN_UNEMP_WO_CONBEN` | group 6 (spouse inactive, no UB) |
     | **two-earner couple** | C_C2 | **`AW67`** | group 5, spouse at 0.67 × AW_t held fixed |

     each at `INCOME_CURR` ∈ {AW67, AW100, **MINW**}.
   - **MINW earnings.** Minimum-wage rows exist only for **BE, EL, ES, FR, IE, LU, PT (2010-2025), DE (2015-2025 only; no 2010 row) and NL (through 2024)**. **AT, DK, FI, IT and SE have no MINW rows** (no statutory minimum wage). Log the missing (country, year) MINW comparisons in `results/gate3_taxben.csv` with status `no_benchmark_row`. The MINW earnings level comes from the newly staged `earnings/earn_mw_cur_EU14.json` (Eurostat `earn_mw_cur`, monthly gross statutory minimum wage, currency `NAC`, semesters S1/S2, 2008-S1…2026-S2). Use the mean of S1 and S2 of the gate year; log S2 alone as a sensitivity. Eurostat already converts 14-payment countries (EL, ES, PT) to a 12-month basis, which matches our all-in-`yem` convention.
   - **Hours at MINW** follow the §3.2 hours rule at that wage, lhw = clamp(40 × MINW/(0.5 × AW_t), 8, 40), and are logged. Where MINW ≥ 0.5 × AW_t this is 40 h, the full-time convention TaxBEN uses. Where the rule gives fewer than 40 h, also log a 40 h diagnostic run beside it. The gated number is the hours-rule run.
   - **Comparison count.** 4 cells × 3 earnings levels × 4 years = 48 per country per leg where all MINW rows exist; 32 for AT, DK, FI, IT, SE; 44 for DE (no 2010 MINW).
   - **Housing variant rule**: per country, choose the OECD `HOUSE_BENEFIT` variant (NO/YES) closest **on the S_C0 AW67 cell in 2015 only**, then keep it fixed for all cells, years and both legs. Log the choice. In Phase 2a, AT matched the YES variant and DK/FR the NO variant.
   - **No-UB leg** vs DF_PTRSA (TEMP_INTOWORK_BENEFIT = NO). Pass only if **both** hold (pre-registered before any run):
     - (i) |Δ| ≤ 5 pp in **≥ 75%** of that country's available comparisons; **and**
     - (ii) **no MINW comparison and no S_C2 comparison** is off by more than 10 pp.
   - **UB leg** vs DF_PTRUB (UNEMP_DURATION = M2, SOC_ASS_BENEFIT = YES, TEMP_INTOWORK_BENEFIT = NO, same housing rule), over the same enlarged cell set: pass if |Δ| ≤ 7.5 pp in ≥ 75% of the available comparisons. (Unchanged threshold, now over more cells.)
   - Phase-2a dry run, no-UB single at 67% AW: DK 2015 70.7 vs 71.6; FR 2015 48.3 vs 50.8; FR 2025 47.8 vs 49.1; AT 2015 66.7 vs 67.1 (housing YES).
   - **What TaxBEN cannot test, stated as a limit.** TaxBEN's lowest earnings level is MINW, a full-time wage that is roughly 0.4-0.6 × AW, so decile-1 cells (r ≈ 0.2, hours near the 8-16 h range of the hours rule) have no external benchmark in any country, and in AT, DK, FI, IT and SE the lowest benchmarked level is 67% AW. Two internal probes cover the hours and part-time paths instead (pass/fail logged in `input_conventions.csv`; failure means a mapping error, fixed uniformly across years, and if unfixable the country is flagged `hours_rule_unvalidated` in every output):
     - **IE hours probe**: a lone parent (group 2) at decile-1 earnings, run at lhw = 18 and lhw = 20 under 2015 and 2025 rules. In-work family support has an hours condition in IE, so disposable income must differ between the two runs. Identical outputs mean EUROMOD is not reading our hours variable.
     - **DE Midijob probe**: a single (group 1) at three monthly earnings, below, inside and above the reduced-contribution band as defined in the DE system's own parameters (read from the country XML, logged, not typed). For 2015 and 2025 the employee SSC rate `ils_sicee/ils_earns` inside the band must be strictly below the rate above the band.
   - **Consequences**:
     - fails no-UB → the country is "unvalidated": dropped from V, the headline and E3 counts, shown in an appendix;
     - passes no-UB but fails UB → headline uses a = a_noUB, i.e. q = 0, for that country, flagged. **Also report the headline with q = 0 for all countries (V4)** so the comparison stays apples to apples; §4 rule 3 decides which is the headline.
   - Report every comparison in `results/gate3_taxben.csv` (columns: c, t, leg, household_type, income_curr, income_part, house_benefit, lhw, ours, taxben, delta, status). Fix input conventions (variable mapping, history variables) **uniformly across all years** before declaring failure. Never tune per year or per cell.

3b. **Change gate (the headline is a change).** For each country in V, compare the TaxBEN no-UB PTR change between the first and last gate year with ours, over the fixed housing variant:
   - Cells: S_C0 at AW67, **plus** S_C0 at the lowest available earnings level (MINW where the row exists in both years; otherwise only the AW67 comparison exists, and that is logged).
   - Years: 2010 → 2025; **DK and NL 2010 → 2024**; **DE MINW 2015 → 2025** (no 2010 MINW row).
   - Pass, per comparison: sign(ΔPTR_ours) = sign(ΔPTR_TaxBEN) **and** |ΔPTR_ours − ΔPTR_TaxBEN| ≤ 5 pp. Where |ΔPTR_TaxBEN| < 1 pp the sign is not defined meaningfully, so only the 5 pp condition applies, and that is logged.
   - A country passes 3b only if every one of its comparisons passes. Passers form V_Δ.
   - A country that fails is **kept in the levels** (E1-E4) and **dropped from E5** and from the card's PTR-change metric, disclosed in findings.md and on the card.
   - Gate span 2010-2025 sits inside the headline span 2009-2026; say so.
   - Results to `results/gate3b_change.csv`.

3c. **MTR gate (τ enters D_d and D_w through the intensive term).** No fetch needed.
   - For **all 14 countries, in 2010 and 2025**, run the MTR add-on, `addons=[('MTR','MTR')]`, on the production households of groups 1 (S_C0 analogue) and 6 (one-earner C_C2 analogue), all deciles and grid points. Read `mtrpc` for the reference person. Read the add-on's earnings increment from `AddOns/MTR` and log it.
   - **Conversion to the labour-cost basis.** `mtrpc` is on gross earnings without employer SSC: m_g = mtrpc/100 = 1 − Δdispy/Δearns. Ours is τ = 1 − Δdispy/Δ(earns + sicer). With the marginal employer-SSC rate σ = Δsicer/Δearns taken from our own +3% run of the same household, 1 − τ = (1 − m_g)/(1 + σ), so the add-on's labour-cost MTR is **τ_addon = 1 − (1 − m_g)/(1 + σ)**. Worked example to print in the log for one AT cell: m_g = 0.45, σ = 0.21 gives τ_addon = 1 − 0.55/1.21 = 0.545.
   - Pass, per country: median over that country's (cell, grid point, year) of |τ_ours − τ_addon| ≤ 5 pp. If the medians differ by more than 5 pp, the country's **E2 and E4 numbers are flagged "τ unvalidated"** in every table, figure and the card. They stay in the E3 counts, since τ is not what the no-UB gate validates, but the flag is printed beside the count.
   - Differences in the add-on's increment size (it may not be +3%) are reported with the result; they are not a reason to tune.
   - Results to `results/gate3c_mtr.csv`, with the arithmetic columns m_g, σ, τ_addon, τ_ours.
4. **Beta vs stable.** For 2025, compute all cells on both J2.54+ and J2.0+ (staged). If the median |Δa| > 1 pp for a country, use J2.0+ for 2009-2025 for that country and label its 2026 point "beta rules".
5. **Sanity.**
   - Report the share of grid points with τ ≥ 0.99 or a ≥ 0.99.
   - Cell rates outside [−0.5, 1.0] after aggregation are logged and truncated at 0.95 **only** in a labelled sensitivity.
   - Ψ cells with non-positive denominators follow the paper's "No Gainers / No Losers" convention.

## 7. Pre-verified sources (all verified 2026-10-05)

| Variable | Source / ID | Coverage verified | Staged file (`shared-data/…`) |
|---|---|---|---|
| Tax-benefit rules | EUROMOD **J2.54+ beta** (Sept 2026), CC BY 4.0. https://euromod-web.jrc.ec.europa.eu/sites/default/files/2026-09/EUROMOD_RELEASES_J2.54%2B.zip | systems ≤2026, all 14; hhot configs 2009-2026 (IE no 2021) | `euromod/EUROMOD_RELEASES_J2.54+.zip` (222.7 MB) |
| Rules, stable | EUROMOD J2.0+ (Feb 2026) | systems ≤2025 | `EUROMOD_RELEASES_J2.0+.zip` (copied from `data/`) |
| Python connector | `euromod` 0.4.0, PyPI (2026-09-30) | runs in container with .NET 8 coreclr | install at run time |
| HHoT defaults template | ec-jrc/JRC-EUROMOD-software-source-code `EM_Plugins/Hypothetical Household/data/HHoT_baseline.xml` (EUPL-1.2) | commit 2021-01-29 | `euromod/HHoT_baseline.xml` |
| Average wage | Eurostat `earn_nt_net` (GRS, P1_NCH_AW100, NAC), updated 2026-10-01 | 2000-2025, all 14 | `earnings/earn_nt_net_AW100_GRS_NAC.json` |
| Statutory minimum wage (gate-3 MINW level) | Eurostat `earn_mw_cur` (monthly, bi-annual; EUR/PPS/NAC), updated 2026-07-31; staged 2026-10-05 for this revision | 2008-S1 to 2026-S2; values for BE, DE (2015+), EL, ES, FR, IE, LU, NL, PT; none for AT, DK, FI, IT, SE | `earnings/earn_mw_cur_EU14.json` |
| Earnings quantiles (V3, Fig-3 analogue) | Eurostat `earn_ses_adeci` (2006), `earn_ses10/14/18/22_adeci` | P10/MED/S2/P90 | `earnings/earn_ses*_adeci.json` |
| CTR inputs | Eurostat `gov_10a_taxag` (D211, D214, S13_S212), `nama_10_gdp` (P31_S14, P3_S13), `gov_10a_main` (D1PAY, S13) | 1995-2024/25 | `ctr/*.json` |
| P_t, q_t (V2) | Eurostat `lfsa_pganws`, `lfsa_ugad`, `lfsa_ugadra` (updated 2026-09-10) | 1998-2025; IE benefit receipt missing pre-2024 | `labour/*.json` |
| External PTR benchmark | OECD TaxBEN `OECD.ELS.JAI,DSD_TAXBEN_PTR@DF_PTRSA` and `@DF_PTRUB` (SDMX, keyless) | 2001-2025 for 12 of 14; **DK and NL 2001-2024** (no 2025 rows; re-checked 2026-10-05). MINW rows only for BE, EL, ES, FR, IE, LU, PT, DE (2015+), NL (≤2024) | `benchmarks/oecd_taxben_*_EU15.csv` |
| 1998 cells, formula layer | `EUROMOD.xls` (authors, Oct 2005) and `run/replication/codebase/welfare_core.py` | — | in run dir |

Endpoints for refetch (only on checksum failure):
- `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<id>?format=JSON&...` (for the minimum wage: `earn_mw_cur?format=JSON&lang=EN&geo=<each of the 14>&sinceTimePeriod=2008`)
- `https://sdmx.oecd.org/public/rest/data/OECD.ELS.JAI,DSD_TAXBEN_PTR@DF_PTRSA,/all?startPeriod=2001&dimensionAtObservation=AllDimensions&format=csvfilewithlabels`

## 8. Deliverables (Study A)

**Required:**
- `report.md`;
- `followup_summary.json`, updated incrementally;
- `result_card.json` (schema `sai.followup.result_card/v1`). Headline: the 2026 count of countries with Ψ_w < Ψ_d, "k of n" over V, plus the median 2009 → 2026 change in bottom-quintile PTR over V_Δ. Each metric is paired with its 1998 baseline computed **on the same country set and under the same q regime** (§4 denominator rules 1-3), read from `run/replication/codebase/results/table2a.csv` (and recomputed through the workbook only for the q = 0 regime). The card states n, the q regime of the headline, and the minimum-coverage status.

`results/findings.md` opens with a plain METHOD paragraph: paper's formulas and 1998 cell weights held fixed; only tax-benefit rules change; hypothetical households; 2009-2026; 14 countries; the 1998 point is a different method.

**Results files:**
- `results/rates_cells.csv`: c, t, g, d, τ, a_noUB, a_UB, a, flags;
- `results/rates_deciles.csv`;
- `results/welfare_by_year.csv`: c, t, Ψ_d, Ψ_w, eff_d, eff_w, flags, for the headline and each variant;
- `results/critical_eta_by_year.csv`;
- `results/gate3_taxben.csv`, `results/gate3b_change.csv`, `results/gate3c_mtr.csv`;
- `results/input_conventions.csv` (earnings variable, NRR route and couples probe, employer-SSC ratios, hours/Midijob probes);
- `results/baseline_1998_noUB.csv` (only if V4 becomes the headline);
- `results/compute_log.csv` (seconds per run, projected core-hours at the §10 checkpoint, any variant cut);
- `results/headline_scalars.json`.

**Figures** (PNG + PDF, big fonts):
1. **Per-country ladder**: decile PTR profile for 1998 (paper), 2009 and 2026.
2. **Over-time figure**: Ψ_d,t and Ψ_w,t for 2009-2026, small multiples by country (Nordic / Continental / Southern & Ireland panels, as in the paper), with the 1998 value as a separate marker.

## 9. Out of scope (state each as a limit in report.md and on the card)

- **UK.** It left EUROMOD. UKMOD needs a separate model and a gated FRS licence (CeMPA request plus UK Data Service EUL). The 15-country tables become 14-country tables.
- **Representative-data claims** C1/Table 1, C3/Fig 3 (only the SES public analogue in V3), C8 with microdata, and Table 7 cols 3-12. They need EU-SILC EUROMOD input data behind a Eurostat RPP, about 2-3 months (Phase-0 briefing §5).
- **Policy years 2005-2008.** There are no hhot configs. An optional attempt pairing a 2007 system with a cloned 2009 hhot config is allowed only if it runs cleanly; otherwise state the gap.
- The 12 post-2004 member states.
- Re-estimating elasticities from data. That belongs to Study B, calibrated from literature, not estimated.
- Any change in population composition. The design deliberately holds the 1998 cell weights fixed.
- **Bottom-decile external validation.** Bottom-decile (r ≈ 0.2, part-time) rates have no external benchmark in any country; they rest on internal probes (IE hours, DE Midijob) only. In AT, DK, FI, IT and SE the lowest benchmarked level is 67% AW.

## 10. Execution rules and compute budget

- **FOREGROUND ONLY.** Never launch EUROMOD loops with `&`, `nohup`, `setsid`, a background task facility, or by ending your turn "to wait". A backgrounded job dies with the session.
  - Run country by country in foreground calls of under about 10 minutes each.
  - Checkpoint each finished country-year to `workspace/checkpoints/<variant>/<CC>_<YYYY>.csv` (`<variant>` = `headline`, `V3`, …), so a re-invocation or the continuation study skips completed work.
- **Parallelism**: at most **4 concurrent EUROMOD processes** (e.g. `concurrent.futures.ProcessPoolExecutor(max_workers=4)` inside one foreground call). Other heavy jobs share this box.
- **Budget, re-estimated with every re-running variant included** (one dataframe per run: all cells × grid points of a country-year go in one frame):

  | Block | Runs |
  |---|---|
  | Headline: 14 countries × 18 years × 4 runs (base, +3%, zero, NRR), less IE 2021 | ≈ 1,004 |
  | Gate 3/3b TaxBEN households: 14 × 4 gate years × 3 runs (base, zero, NRR) | 168 |
  | Gate 3c MTR add-on: 14 × 2 years | 28 |
  | Gate 4, J2.0+ for 2025: 14 × 4 | 56 |
  | Probes (earnings variable, NRR couples, employer SSC, IE hours, DE Midijob) | ≈ 60 |
  | V3, V5, V6, lhw = 40: 4 variants × 14 × 4 years {2009, 2015, 2020, 2026} × 4 runs | 896 |
  | Employer-SSC inversion: 14 × 2025 × 4 runs | 56 |
  | **Total** | **≈ 2,270** |

  At the Phase-2a-informed 10-60 s per run that is **about 6-38 core-hours**, or about 1.6-9.5 hours of wall-clock at 4 workers. The cap is **40 core-hours**.
- **Order of work** (so that a cut never touches the headline): gates 0-2 → probes → gate 3/3b/3c → headline 2009-2026 → gate 4 → V1, V2, V4 (no runs) → V3 → V5 → V6 → lhw = 40 → employer-SSC inversion.
- **Budget checkpoint.** After the headline is done for the first two countries, compute the mean seconds per run, project the total, and write both to `results/compute_log.csv`.
  - If the projection exceeds 40 core-hours, cut V3, V5, V6 and lhw = 40 to t ∈ {2009, 2026}.
  - If it still exceeds 40, drop lhw = 40, then V6, in that order.
  - Every cut is logged and stated in report.md and on the card. The headline and the gates are never cut.
- **Continuation rule.** Every finished country-year (headline and each variant) is checkpointed to `workspace/checkpoints/<variant>/<CC>_<YYYY>.csv`. If the session ends before the deliverables are complete, the orchestrator launches **`003-living-update-cont`** with this same instruction plus one header line: "Continuation of `followup/001-living-update/`. Copy or link its `workspace/checkpoints/`, `results/` and `results/input_conventions.csv` into your workspace first; skip every country-year that has a checkpoint; do not re-run gates that have a results row; finish the remaining work and write the deliverables." It runs with an explicit `--timeout 43200`. Study B then reads its inputs from whichever of 001 or 003 holds the complete results.
- **Memory**: about 1-3 GB per process. Delete per-country extractions after use; container `/tmp` only.
- **Model pinning**: the orchestrator exports `ANTHROPIC_MODEL` explicitly (econ batch convention).
- **Honesty rules**: every number comes from this session's execution. Divergent honest numbers are findings. Gaps (IE 2021, AW 2026 extrapolation, CTR carry-forward, countries dropped at gate 3) are disclosed in the study, the report, and the card.

---

## 11. Study B: `002-theory-update` (after 001 completes)

Seeded from `followup/001-living-update/` (or `followup/003-living-update-cont/` if a continuation completed the work). Launched with `--timeout 7200`. Use only countries in 001's validated set V and respect its q-regime headline rule (§4) and "τ unvalidated" flags. Read its report.md, result_card.json and results/*.csv first. **Fetch nothing new.** Reuse 001's `rates_cells.csv`, `welfare_by_year.csv` and code.

**Task.** Write the "Theory, updated to 2026" section the paper would carry today, **as a model**, starting from the paper's own framework (Section 1: the discrete participation + intensive model, eqs 15-19, with the Table-3 logic).

1. **Inverse-optimum reading of each era's tax-benefit system** [ESTIMATED from 001 rates, CALIBRATED elasticities]. This is a **[CONSISTENCY CHECK]**, not a test: g is built from the same τ, a and formulas that produce 001's Pareto flags, so agreement is close to mechanical and must be labelled that way everywhere.
   - **The equation.** The paper (EJ 2007) derives Ψ, not an inverse optimum; the inverse-optimum formula is Saez (2002), "Optimal Income Transfer Programs: Intensive versus Extensive Labor Supply Responses", *QJE* 117(3):1039-1073, the mixed extensive + intensive model, **eq. (16) of NBER WP 7708** (verified 2026-10-05 from the NBER PDF; the QJE print may number it differently, so cite both). With occupations i = 1…I ordered by earnings, population shares h_i, normalised density h(w_i) = h_i/(w_i − w_{i−1}):

     τ_i/(1 − τ_i) = [1/(ε_i · w_i · h(w_i))] · Σ_{j ≥ i} h_j · [1 − g_j − η_j · (T_j − T_0)/(c_j − c_0)],

     with the normalisation Σ_{i=0}^{I} h_i g_i = 1 (Saez's eq. (2), no income effects). Since c_j − c_0 = w_j(1 − a_j), the last term is η_j · a_j/(1 − a_j) in the paper's notation.
   - **Inverted for g (what we compute).** Define B_i = ε · [τ_i/(1 − τ_i)] · w_i · h_i/(w_i − w_{i−1}) for i = 1…I and B_{I+1} = 0. Differencing the formula at i and i + 1 gives

     **g_i = 1 − η_i · a_i/(1 − a_i) − (B_i − B_{i+1})/h_i**, for i = 1…I, and **g_0 = [1 − Σ_{i≥1} h_i g_i]/h_0**.

     With ε = 0 this reduces to g_i = 1 − η_i a_i/(1 − a_i), the extensive-only expression.
   - **Mapping to the paper's cells (pre-declared).** Occupations are the paper's 10 earnings deciles (I = 10), not the 100 group × decile cells, because the intensive term needs an earnings ordering and adjacent-occupation gaps.
     - w_d = s_d/e_d (relative earnings, so scale drops out), w_0 = 0;
     - h_d = P · e_d, h_0 = 1 − P;
     - τ_d and a_d are the employment-weighted decile rates (001's E1);
     - η_d is the benchmark profile and ε = 0.1.
     - τ_d is a within-cell MTR, while Saez's τ_i is the implicit rate between adjacent occupations. As a sensitivity, also compute τ_i = (T_i − T_{i−1})/(w_i − w_{i−1}) from decile-mean taxes, and report both.
     - The extensive-only g_j at the 100-cell level is reported as a robustness row.
   - **Reproduction check on the paper's case (must be run first).** Using the 1998 workbook arrays, compute g_d for DK and check that DK has g_d < 0 in at least one decile that receives the working-poor transfer (definition below), which is the paper's 1998 DK Pareto result. Also report all 15 1998 countries against `table2a.csv` (only DK is Pareto there). If DK does not reproduce, say so in the first paragraph of `theory_update.md` and do not use the iff in any later claim.
   - **Which cells "receive the working-poor transfer", as coded in `welfare_core.py`.** The transfer TR goes to every cell with e_j > 0, and the **net gainers** are G_w = {j : e_j > 0 and s_j/e_j < 1 − D_w} (the `gw` mask in `compute()`). The iff is evaluated only over deciles containing at least one G_w cell: "Pareto-improving iff some decile d with a G_w cell has g_d < 0". The all-employed version is reported beside it.
   - Compute g by decile for 1998 (workbook) and each year 2009-2026, for each country in 001's validated set V.
   - Report, per country and era, the share of employment in deciles with g < 0, and the **[CONSISTENCY CHECK]** agreement table against 001's Pareto flags.
2. **Elasticity frontier by era.**
   - From 001's critical η (Table-3 analogue per year), draw for 2009, 2015, 2020 and 2026 the region in (η_avg, ε) space where Ψ_w < Ψ_d, Ψ_w < 1, and Pareto.
   - Overlay the post-2007 evidence as bands, with sources from `recency-research.md` §6.2. **Each band's legend entry names where its evidence comes from.** Kleven (2024) is US EITC evidence: its legend label must read **"Kleven 2024 (US EITC)"**, and the text must not present it as a European elasticity. Chetty et al. (2011) is likewise mostly US evidence and is labelled "(mostly US)".
     - Kleven 2024, EITC participation response ≈ 0 (US EITC);
     - Bartels & Shupe 2023, 0.08 (men) / 0.14 (women);
     - Chetty et al. 2011, ≈ 0.25;
     - Lundberg & Norell 2018, 0.38;
     - Bargain, Orsini & Peichl 2014, extensive larger at the bottom.
   - State for each country and era which literature band the conclusion survives.
3. **One minimal amendment, justified against one rejected alternative.**
   - **Candidate (preferred)**: elasticities concentrated on secondary earners and lone parents. This is paper Table 6b and the authors' own couples extension (Immervoll, Kleven, Kreiner & Verdelin 2011, JPubE). Recompute the frontier with η on groups 2, 7-10 only, and ask whether that explains the countries where in-work dominance weakens by 2026.
   - **Alternative to discuss and reject or keep**: an unemployment/wage-response channel (Kroft, Kucko, Lehmann & Schmieder 2020, AEJ:Policy). It pushes the optimum toward a negative income tax but needs parameters the 001 artefacts cannot calibrate. Label it [PROPOSED].
4. **Linearisation accuracy check** (renamed; it is **not** a validation). Ψ_w is a deterministic function of the rates, so this only measures how well a linear approximation tracks the formula, and no claim of the paper becomes more or less believable either way. Label it **[CONSISTENCY CHECK]**.
   - Using 2009-2017 only, fit the cross-country linear relation between the change in bottom-quintile PTR and the change in Ψ_w implied by the model's linearisation.
   - Predict 2018-2026 changes and report the fit as linearisation accuracy.
   - Also report whether the model "explains" the 1998 → 2026 change for countries with major in-work expansions (FR 2016/2019, DK 2025, FI 2025, ES 2023), clearly marking the 1998 method break.

4b. **External check: cost per additional worker of a marginal in-work transfer, Belgium** [ESTIMATED from 001 rates, CALIBRATED η] vs literature. No fetch is needed: the comparison figures are written here.
   - **Published comparison (verified live 2026-10-05 at https://www.microsimulation.pub/articles/00229).** de Mahieu, A. (2021), "In-work Benefits in Belgium: Effects on Labour Supply and Welfare", *International Journal of Microsimulation* 14(1):43-72.
     - Three Work-Bonus expansions, each costing €300m a year before behavioural responses, on 2016 policy rules and 2017 SILC data.
     - Net budgetary cost after behavioural responses, per additional **full-time-equivalent** worker: **€368.5k (reform 1, higher maximum) to €1,660.1k (reform 2, higher maximum and thresholds)**. Reform 3 creates no FTE gain.
     - Per additional **participant**: €121.1k (reform 1), €195.1k (reform 2), €560.7k (reform 3).
   - **Model analogue (paper's framework, eq. (13)).** An unfunded marginal lump-sum in-work transfer dT to employed cells in BE deciles 1-2 (sensitivity: deciles 1-3), 001's BE rates for policy year **2016**:
     - net cost = dT · Σ_{j∈target} E_j · [1 − η_j · a_j/(1 − a_j)] (the mechanical cost less the revenue from new entrants);
     - additional workers = Σ_{j∈target} η_j · E_j · dT/(w_j(1 − a_j)), with w_j = r_j × AW_2016 in euros (annual, gross, from 001's AW series);
     - additional FTE = the same sum with each cell weighted by lhw_j/40 from the §3.2 hours rule;
     - cost per additional participant = net cost / additional workers; cost per FTE = net cost / additional FTE. dT cancels.
     - E_j = P · e_j × BE working-age population is not needed: the ratio uses only shares.
   - **Report**: the model's two numbers (per participant, per FTE) at the benchmark η and at the Bartels & Shupe (2023) lower elasticities, the published ranges, and whether each model number falls inside the published range, below it or above it.
   - **Why they may differ, stated in advance**: the model transfer is lump-sum (no phase-out, so no intensive-margin cost), while the Work Bonus is phased out (reform 1 raises the withdrawal rate to 29.2%), so the model number is expected to sit **at or below** the published range. A model number above €1.66m per FTE would be informative against the calibrated η.
   - No other study country has a cited cost-per-job estimate in `recency-research.md`; state that the check covers BE only.
   - If the agent cannot see these figures (they are in this spec, so it can), it cites the research note §6.2 row and tags the comparison [CALIBRATED vs literature].
5. **Deliverables**:
   - `results/theory_update.md`, publication-quality prose: original model recap, what the new rates demand (with the inverse-optimum equation written out as in item 1), the updated model, calibration table, the two **[CONSISTENCY CHECK]**s (items 1 and 4) kept separate from the **external check** (item 4b), implications. The word "validation" is used only for item 4b;
   - `results/external_check_be.csv`: model cost per participant and per FTE (benchmark and Bartels-Shupe η; deciles 1-2 and 1-3) beside the de Mahieu (2021) figures;
   - `results/calibration_table.csv`: 1998 vs 2026 parameters and moments, with sources;
   - one figure (frontier by era, PNG + PDF), with the literature bands labelled by origin as in item 2;
   - `result_card.json` with metrics = key shifts (e.g. median critical η for Ψ_w = Ψ_d, 1998 vs 2026; share of employment with g < 0);
   - every claim tagged [ESTIMATED] / [CALIBRATED] / [PROPOSED].
6. **Compute**: CPU only, minutes, no EUROMOD runs, **no fetches**.

## 12. Spec risks for the judge (author's own list)

1. **Hypothetical-household input conventions.** This is the biggest risk. Wrong earnings variable, missing irregular-pay split, housing treatment or UB history change PTRs by more than 10 pp silently. Gate 3 is the mitigation, and its pass thresholds are pre-registered.
2. **UB leg.** UB was not triggered for AT under 2025 rules in Phase 2a by any route tried. It did trigger via NRR under 2009 rules. Several countries may end up q = 0. V4 keeps the comparison honest.
3. **Method break at 1998 → 2009.** The headline is the 2009 → 2026 change.
4. **Beta model.** 2026 rules exist only in a beta. Gate 4 checks 2025 against the stable release.
5. **Fixed 1998 weights.** By design this is a rules-only counterfactual, not "the 2026 economy". The paper's own Table 1 / Fig 3 / Table 7 microdata quantities remain gated.
6. **Coverage the benchmark cannot give** (added in revision 1). TaxBEN has no row below the full-time minimum wage, no MINW row for AT, DK, FI, IT or SE, and no 2025 row for DK or NL. Decile-1 cells are therefore benchmarked nowhere; the IE hours and DE Midijob probes are internal checks only. Stated as a limit, not hidden.

---

## Revision changelog (2026-10-05)

Revision 1 against `verdicts/phase2b-judge.md`, Immervoll items I1-I10. Each line says exactly what changed and where. Nothing else in the spec was changed, apart from factual corrections forced by the staged data (marked "data fact").

**Asset check done before writing gate 3 (data facts, verified on the staged CSVs 2026-10-05):**
- Both TaxBEN files have the columns `REF_AREA, INCOME_CURR, HOUSEHOLD_TYPE, INCOME_PART, UNEMP_DURATION, SOC_ASS_BENEFIT, HOUSE_BENEFIT, TEMP_INTOWORK_BENEFIT, TIME_PERIOD, OBS_VALUE`. `INCOME_CURR` ∈ {AW67, AW100, MINW}; `HOUSEHOLD_TYPE` ∈ {S_C0, S_C2, C_C0, C_C2}; `INCOME_PART` ∈ {_Z, NOEARN_UNEMP_WO_CONBEN, AW67, AW100, MINW}. The judge's description is correct.
- **MINW rows exist only for BE, EL, ES, FR, IE, LU, PT; DE from 2015; NL through 2024. None for AT, DK, FI, IT, SE.**
- **DK and NL have no 2025 rows at all** in either file (both end in 2024). The original spec's "2001-2025, all 14" was wrong for these two.
- The CSVs hold PTRs only, not the minimum-wage amount, so a MINW household could not be built from staged data. **Staged** `extension-assets/earnings/earn_mw_cur_EU14.json` (Eurostat `earn_mw_cur`, fetched 2026-10-05, dataset updated 2026-07-31) and appended its line to `extension-assets/SHA256SUMS.txt` (all lines re-verified OK).

| Item | What changed |
|---|---|
| **I1** (a) | §6 gate 3: added **S_C2 lone parent** (group 2) and **two-earner C_C2 with spouse at AW67** (`INCOME_PART = AW67`, group 5) to both legs, alongside S_C0 and one-earner C_C2. Cell table written against the actual CSV columns. |
| **I1** (b) | §6 gate 3: added `INCOME_CURR = MINW` wherever TaxBEN has a row; MINW earnings from the newly staged Eurostat file (S1/S2 mean; S2 sensitivity); hours from the §3.2 hours rule at that wage (40 h diagnostic logged where the rule gives < 40 h); countries/years without a MINW row logged as `no_benchmark_row`. Gate years for DK and NL end in 2024 (data fact). Housing variant still chosen on 2015 only, now pinned to the S_C0 AW67 cell. |
| **I1** (c) | §6 gate 3: pre-registered no-UB pass = \|Δ\| ≤ 5 pp in ≥ 75% of available comparisons **and** no MINW or S_C2 comparison off by > 10 pp. UB-leg threshold unchanged (7.5 pp, ≥ 75%, i.e. the old 12 of 16) but now over the enlarged cell set. Added the stated limit that decile-1 (r ≈ 0.2) cells have no external benchmark, with two internal probes for the paths the judge named: **IE hours probe** (lhw 18 vs 20) and **DE Midijob probe** (employee SSC rate inside vs above the band, band read from the DE XML). §12 risk 6 added. |
| **I2** | New §6 **gate 3b (change gate)**: S_C0 AW67 plus lowest available earnings level (MINW where it exists in both years), 2010 → 2025 (DK/NL → 2024; DE MINW 2015 → 2025); pass = sign match and \|Δchange\| ≤ 5 pp; sign condition waived only where \|ΔTaxBEN\| < 1 pp (logged). Failers stay in levels, leave E5 and the card's PTR-change metric, and are disclosed. §4 E5 now defined over V_Δ. |
| **I3** | §3.3 cross-check replaced by pointer; new §6 **gate 3c (MTR gate)**: all 14 countries, 2010 and 2025, groups 1 and 6 (S_C0 / C_C2 analogues), all deciles and grid points. Conversion written out: τ_addon = 1 − (1 − m_g)/(1 + σ), σ = Δsicer/Δearns from our +3% run, with a worked example. Median \|τ_ours − τ_addon\| > 5 pp → that country's E2/E4 flagged "τ unvalidated". |
| **I4** | §3.3 "zero, with UB": removed "for each earner"; stated the required semantics (reference person only); added a pre-production **couples probe** per country (group 5 household; spouse earnings unchanged and spouse UB zero); fallback to per-person NRR scenarios or `HHoT_un`; choice applied to all years and logged in `input_conventions.csv` (named columns). |
| **I5** (a) | §4 denominator rule 1: 1998 baseline computed on exactly the validated set V (V_Δ for E5), paper codes mapped, UK never in the baseline, both sides printed "k of n". §8 card text updated to match. |
| **I5** (b) | §4 rule 2: if \|V\| < 10, headline is "validated in n of 14" and E3 is never compared with the paper's 15-country statements. |
| **I5** (c) | §4 E3 reported under both mixed-q and V4; rule 3: **4 or more q = 0 fallbacks in V → V4 is the headline**. Baseline follows the same regime: paper Table 5(b) Ψ values (paper-reported, not recomputed, since `EUROMOD.xls` has no no-UB arrays) and "no same-definition 1998 baseline" for the bottom-quintile PTR under V4. |
| **I6** | §5: re-running variants (V3, V5, V6, lhw = 40) restricted to t ∈ {2009, 2015, 2020, 2026}; SSC inversion stays 2025 only. §10: budget re-estimated with all of them included (≈ 2,270 runs, about 6-38 core-hours; cap 40), order of work, a budget checkpoint after two countries with a pre-declared cut order (variants → {2009, 2026}, then drop lhw = 40, then V6; never the headline or gates). **Continuation rule**: `003-living-update-cont` reuses `workspace/checkpoints/<variant>/`, `results/` and `input_conventions.csv`, with the instruction header written out. Explicit `--timeout` values at the top (43200 for 001 and 003, 7200 for 002). |
| **I7** (a) | §1 hard prohibition 5: the gate-0 install endpoints are listed explicitly (`dot.net/v1/dotnet-install.sh`, `builds.dotnet.microsoft.com`, `dotnetcli.azureedge.net`, `pypi.org`, `files.pythonhosted.org`). |
| **I7** (b) | §3.3: **employer-SSC probe** per country (2009, 2025; 0.67 and 1.0 AW): 0 < sicer/earns < 0.45, DK accepted in [0, 0.03]; failures fixed uniformly or the country falls back to a flagged gross basis. |
| **I8** (a) | §11 item 1: inverse-optimum equation written out from Saez (2002) QJE 117(3), eq. (16) of NBER WP 7708 (checked against the NBER PDF 2026-10-05), with the normalisation, and the explicit inversion g_i = 1 − η_i a_i/(1 − a_i) − (B_i − B_{i+1})/h_i plus g_0; mapping to deciles pre-declared, with the within-cell vs between-occupation τ sensitivity. |
| **I8** (b) | §11 item 1: DK 1998 reproduction from the workbook is run first; if it fails, it is stated up front and the iff is not used. |
| **I8** (c) | §11 item 1: iff restricted to deciles containing a working-poor net-gainer cell, G_w = {e_j > 0, s_j/e_j < 1 − D_w}, the `gw` mask in `welfare_core.compute()`; the all-employed version is shown beside it. |
| **I8** (d) | §11 item 1 and deliverables: agreement table labelled **[CONSISTENCY CHECK]**. |
| **I9** | §11 item 4 renamed "linearisation accuracy check", labelled [CONSISTENCY CHECK]. New item **4b, external check**: model cost per additional participant and per FTE of a marginal lump-sum in-work transfer in BE (2016 rules, deciles 1-2; sensitivity 1-3; benchmark and Bartels-Shupe η), formulas written out from eq. (13), compared with **de Mahieu (2021), IJM 14(1):43-72: €368.5k-€1,660.1k per FTE; €121.1k-€560.7k per participant**, verified live 2026-10-05 (the research note's €368k-€1.66m range is correct). Direction of expected disagreement declared in advance. New `results/external_check_be.csv`. BE is the only country with a cited estimate. |
| **I10** | §11 item 2: Kleven (2024) legend label must read "Kleven 2024 (US EITC)" and the text may not present it as a European elasticity; Chetty et al. (2011) labelled "(mostly US)". Deliverables figure line references this. |
| (consequential, I5/I6) | §11 preamble: Study B may be seeded from `003-living-update-cont`, runs with `--timeout 7200`, and inherits 001's set V, q-regime headline rule and "τ unvalidated" flags. §8 results list gains `gate3b_change.csv`, `gate3c_mtr.csv`, `baseline_1998_noUB.csv`, `compute_log.csv`. |