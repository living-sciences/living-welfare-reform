# Findings addendum to 003-theory-update (issued by 004-gate-conformance)

This addendum corrects two false statements in `003-theory-update` (its `result_card.json`
notes and `theory_update.md`), per the provenance audit §2–§3 and §7 item 6. The numbers in
003 trace and are not disputed; the **validation framing** was wrong.

1. **"validated set V = 14 countries" is false.** The spec's gate-3 no-UB check gives
   **V = {DK, FR, NL}** (|V| = 3; NL added by this study's gate-3 completion). 003 inherited
   001's hard-coded `validated_set = all 14` instead of the pre-registered V. Every place 003
   says the panel is drawn from a "level-validated V = 14" is incorrect. Because |V| < 10 the
   honest-partial rule applies and the theory results are **descriptive / elasticity-contingent
   over an unvalidated set**, not validated cross-country counts.

2. **"no τ-unvalidated country (gate-3c medians ≤ 0.55 pp)" is false.** The gate-3c MTR add-on
   **aborted for FR and EL** in the original run and **again on retry in this study**
   (`gate3c_FR_EL_completion.csv`, header only). FR and EL are **τ unvalidated** and must carry
   that flag wherever their MTR/τ-based numbers appear.

3. **Consequence for the elasticity-frontier panel {FI, FR, EL, IT, SE}.** This panel underpins
   003's headline "critical elasticity 0.22 → 0.13" and the survival counts. Of its five
   countries, **only FR is in the validated set V**; FI, EL, IT, SE all **fail the gate-3 level
   test**, **EL and IT are gross-basis**, and **FR and EL have no gate-3c (τ) result**. The
   frontier result is a legitimate descriptive/theoretical exercise but must be labelled as
   computed over an **unvalidated, τ-partly-unvalidated** panel — not presented as validated.

The 003 card's quantitative frontier numbers (0.22 → 0.13; the per-elasticity survival counts)
are unchanged; only their validation status is corrected here.
