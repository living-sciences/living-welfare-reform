# Running findings notes (living-update 001)

## Gate 0 — PASSED (2026-10-05)
- .NET 8.0.31 installed to ~/.dotnet; euromod==0.4.0 + pandas via /app/.venv; PYTHONNET_RUNTIME=coreclr.
- Smoke test AT_2025 on AT_training_data: FINISHED 0 errors, 7482 persons, 446 vars, 12.8s (spec ~7482, ~13.5s). ✓

## Engine timing
- First .run() per process = ~13s JIT warmup; subsequent runs on same Model ~1.6–3.2s regardless of df size.
- => reuse one Model per country; batch all scenarios of a country-year into ONE df/run.

## a_UB route decision
- NRR add-on (preferred per spec) models an ~18-month unemployment spell (lunmy_nrr=18) in which UB is
  largely exhausted; for FR/DK/DE 2025 its ils_dispy_nrr == the no-UB social-assistance floor (UB=0).
- Direct construction (ref person les=5 unemployed full period, prev earnings + contribution history;
  == HHoT_un switch, verified identical) gives the paper's SHORT-term a_UB semantics and correct couple
  behaviour (only ref unemployed; spouse keeps earnings — verified: spouse ils_earns preserved).
- UB-triggering survey (single @1.0AW, direct construction): AT2025 YES (bunct 1580), FI2025 YES(weak),
  FR/DK/DE 2025 no, AT/FR/DK/DE/FI 2009 no.
- DECISION: use direct-construction route for a_UB uniformly (controllable, paper-faithful, correct couple
  semantics). Countries whose UB leg fails gate 3 fall to q=0 (flagged); V4 (q=0 everywhere) reported and
  becomes headline if >=4 fallbacks (spec §4 rule 3). This is the spec-anticipated outcome (§12 risk 2).

## Earnings variable
- AT: yem (ils_earns==yem verified). FR: yem00 (verified via NRR base). EL: probe yemre. Probe each country.

## Employer SSC (AT 2025 single @1.0AW): ils_sicer/ils_earns = 332/1200-type ~0.277 (plausible, 0<r<0.45). ✓

## CENTRAL METHODOLOGICAL FINDING (crux)
- Under 2009-2026 rules, hypothetical decile-1 cells (one-earner couples groups 4/6/8/10 and lone
  parent group 2 at r~=0.2*AW) hit genuine inactivity/unemployment traps: PTR a>=1.0 and MTR tau~0.9-1.1.
- The paper's closed-form efficiency/trade-off expressions divide by (1-tau) and (1-a); near rate=1 they
  explode. Ψ_w is cap-dominated and sits on the den_w=0 singularity (AT 2009: Ψ_w=244@cap.999, 29966@.99;
  AT 2025 Ψ_d=nan because Dd>1). This is NOT present in the paper (survey cell-averages kept rates <1).
- => Ψ (E2/E3/E4) is reported WITH a stability flag (agreement across cap in {.999,.99}) and the
  No-Gainers/No-Losers null convention; the ROBUST headline results are the decile PTR/MTR profiles (E1)
  and the bottom-quintile PTR 2009->2026 change (E5). This instability is itself a reported finding and a
  direct answer to "does the ranking still hold?": bottom-decile PTRs have risen toward 100%.
- Rates at 67% AW (the lowest TaxBEN benchmark) are far lower (~50-72%) and are what gate 3 validates;
  decile-1 (20% AW) has no external benchmark (spec §9), consistent with high trap values.

## Gates 3 / 3b (validation)
- Denominator bug fixed: PTR denominator = CHANGE in labour cost (ref person's earns+sicer),
  not total household (affected working-spouse couples 3/5/7/9). Verified: AT two-earner now 41 vs OECD 40.
- Gate 3 no-UB LEVEL leg (strict, pre-registered): PASS only DK, FR. Single (S_C0) cells match well for
  AT/FR/DK (AT 2015 66.7 vs 67.1). Failures concentrated in lone-parent (S_C2) and two-earner cells and
  a ~10pp uniform level offset for EL/PT/ES/SE (family/childcare benefit modelling in hypothetical hh).
- UB leg fails ~everywhere (our full-period UB vs OECD M2 2-month) -> consistent with q=0/V4 headline.
- Gate 3b CHANGE gate (the headline is a change; country-constant level offsets cancel):
  V_delta = {DK, FI, FR, LU, NL, SE} pass (2010->2025 PTR change sign + within 5pp of OECD).
- => E5 (bottom-quintile PTR change) headline reported over V_delta (median -3.2pp); others level-shown,
  change-not-validated. V (level) = {DK,FR}; |V|<10 -> minimum-coverage: "validated in n of 14".
