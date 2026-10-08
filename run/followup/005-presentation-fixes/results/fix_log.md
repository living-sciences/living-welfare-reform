# fix_log.md — 005-presentation-fixes

Maps each of the six audit re-check items to the exact change made. **005 supersedes
004's `findings.md`, `card_corrections.csv` and `Fig 1`**: those are re-issued (corrected)
in `005/results/`; 004's own files are left untouched on disk. No recomputation was done
except item 1's table, which is assembled from existing CSVs (no EUROMOD run, no fetch).

Source of the six items: the 005 instruction (itself the audit re-check). Note: the staged
`gate-conformance-inputs/immervoll-provenance.md` on disk ends at §7 and has **no appended
dated re-check section** (see report.md, Deviations); the enumerated six items were taken
from the instruction and cross-checked against §2–§3 and §7 of that file.

| # | Item | File(s) changed | Exact change |
|---|---|---|---|
| **1** | Produce the corrected trade-off table 004 claimed exists | `results/tradeoff_table_corrected.csv` (new); `results/findings.md` (Item-1 section) | Assembled all 14 countries (incl. **EL, LU**) from `001/results/welfare_by_year.csv` 2026, V4 — columns `country, regime, Psi_d_2026, Psi_w_V4_2026, Psi_w_lt_Psi_d, Psi_w_lt_1, Psi_stable, note`. Ψ_w<Ψ_d counted only where Ψ is stable (10 stable → 8 Ψ_w<Ψ_d, 4 Ψ_w<1). **DK note = beta-step-dependent** (−18.0 of −24.3 pp is the 2025→26 beta step); **ES note = contradicted by the OECD change benchmark**. Rendered as a Markdown table in findings.md. |
| **2** | Complete `card_corrections.csv` | `results/card_corrections.csv` (12 carried rows + 6 new = 18) | Carried 004's 12 rows unchanged except the compute row (updated to 0.48, see item 6). **Added 4 rows for the 002 card**: (a) "8 of 10"/"14 of 14" (same defect as 001 — descriptive unvalidated set, cross-regime baseline); (b) "−3.2 pp" (non-conforming V_Δ dropped → −5.2 pp over {DK,FR,NL}); (c) "Denmark change-validated at gate 3b" (3b covers only 2010→2024 AW67, not the 2026 beta step); (d) the V_Δ table listing **FI/LU/SE** (not in the subset V_Δ={DK,FR,NL}; they failed the level gate). **Added 2 rows for the 003 card**: (e) the **"/14" denominators** (14 ≠ V; counts Ψ-unstable country-years; forbidden comparison with the paper's "14 of 14"); (f) the **"0.22→0.13" headline** (panel {FI,FR,EL,IT,SE} is post-hoc and level-unvalidated — 4 of 5 failed the level gate, EL/IT gross-basis, FR/EL no gate-3c; the headline stands only as a descriptive statistic). |
| **3** | Fix Fig 1's label | `results/fig1_gate3b_change_validation.png` (re-rendered); card fig1 caption/alt | Y-axis label changed from `"bottom-quintile PTR change\n2010->2025 ... AW67 (pp)"` to **`"PTR change, single adult at 67% AW\n2010->2025 (DK/NL ->2024), gate 3b (pp)"`**. Title now names the gate-3b single-adult-67%-AW change. Card fig1 caption/alt rewritten to say it is the gate-3b hypothetical-household change, not a bottom-quintile rate. |
| **4** | Portugal consistency | `results/fig1_gate3b_change_validation.png`; card fig1 caption + gate-table row "3b" + metric 3 note; `results/findings.md` (E5 section) | PT moved from the grey "not level-validated / fails 3b" group to the **orange "contradicted by the OECD change benchmark"** group (with ES, IT), with the "contradicted" annotation. Rationale recorded everywhere: PT ours **−11.2 vs +16.6 (AW67)** and **−9.9 vs +9.4 (MINW)** — opposite OECD sign at **both** earnings levels (verified in `001/results/gate3b_change.csv`). |
| **5** | Card field fixes | `result_card.json` | (a) Metric 3 (PTR change): the **"−1.2 pp (all 14)" string moved from the `baseline` field to the `note`**; `baseline` now reads **"no same-definition 1998 baseline (V4 headline, q=0)"** (the V4 headline has no same-definition 1998 baseline). (b) Metric 1 label changed from "OECD level-validated countries **(gate 3, 2026)**" to **"(gate 3, 2010–2025)"**; gate-table row 3 likewise annotated "(2010–2025)". |
| **6** | Wording | `result_card.json`; `results/findings.md`; `results/card_corrections.csv` (compute row) | (a) Core-hours corrected to **0.48** = 001+002 combined (001 0.22 + 002 0.30; the 002 card already reported "0.30 / 0.48"), replacing 004's "0.22, prior studies" (0.22 is 001 alone). (b) Audit defect-list citation corrected from "**§4–§5** and §7" to **"§2–§3 and §7"** (findings.md intro and card note: "provenance audit §2–§3, §7"). |

## Deliverables produced by 005

- `results/tradeoff_table_corrected.csv` — item 1 (new)
- `results/card_corrections.csv` — item 2 (re-issued, 18 rows)
- `results/fig1_gate3b_change_validation.png` — items 3,4 (re-rendered)
- `results/fig2_headline_by_cut.png` — copied unchanged from 004 so the superseding card is self-contained (not one of the six items)
- `results/findings.md` — re-issued, supersedes 004's
- `result_card.json`, `report.md`, `followup_summary.json`, `results/fix_log.md`

## Not changed (out of the six items, left untouched in 004, read-only)

`baseline_1998_noUB.csv`, `findings_addendum_003.md`, `recut_values.json`, `gate_completions.json`,
`gate3_NL_completion.csv`, `gate3c_FR_EL_completion.csv`, and the numeric values anywhere — all
verified correct by the audit re-check.

## Orchestrator correction (2026-10-07, audit final-check items A & B)
Applied by the orchestrating session per the provenance auditor's prescriptions, after the
auditor verified all underlying numbers; no values recomputed.
- A: tradeoff_table_corrected.csv gained in_V_level_validated and tau_unvalidated columns
  (V={DK,FR,NL}; FR/EL tau-unvalidated) and IT/PT now carry the same OECD-change-contradicted
  note as ES; same flags added to the findings.md table.
- B: core-hours arithmetic corrected to 001 0.22 logged + 002 0.26 logged = 0.48 (0.30 was
  002's self-reported figure) in findings.md, card_corrections.csv and result_card.json.
