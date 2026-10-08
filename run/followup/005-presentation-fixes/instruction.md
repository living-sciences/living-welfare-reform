# 005-presentation-fixes — close the audit re-check's six items on 004's deliverables

Scope: fix exactly the six presentation items from the audit re-check (staged at
`gate-conformance-inputs/immervoll-provenance.md`, dated re-check section at the end —
read it first). All numbers in 004 were verified correct; do NOT recompute anything
except item 1's table, which is assembled from existing CSVs. No fetches, no EUROMOD
runs, foreground only, < 0.5 core-hours, `--timeout 3600`.

1. **Produce the corrected trade-off table** that 004's findings claim exists: all 14
   countries including EL and LU, from `followup/001-living-update/results/welfare_by_year.csv`
   (and 002-cont's identical CSVs), with DK marked beta-step-dependent and ES marked
   OECD-contradicted. Write `results/tradeoff_table_corrected.csv` + render it in findings.md.
2. **Complete `results/card_corrections.csv`**: add rows covering the 002 card's stale
   claims ("8 of 10", "−3.2 pp", "Denmark change-validated", its V_Δ table listing FI/LU/SE)
   and explicit rows for the 003 card's "/14" denominators and its "0.22→0.13" headline
   (correction: the frontier panel {FI, FR, EL, IT, SE} contains level-unvalidated countries;
   the headline stands only as a descriptive statistic).
3. **Fix Fig 1's label**: y-axis/caption must say it shows the gate-3b change for a single
   adult at 67% AW, not "bottom-quintile PTR change". Re-render the PNG.
4. **Portugal consistency**: OECD change has the opposite sign at both earnings levels
   (−11.2 vs +16.6; −9.9 vs +9.4) — label PT "contradicted by the OECD change benchmark"
   exactly like ES and IT, not merely "fails 3b".
5. **Card field fixes**: move the "−1.2 pp all-14" figure from the PTR-change metric's
   baseline field to its note (the V4 headline has no same-definition 1998 baseline);
   metric 1's gate years are 2010–2025, not "gate 3, 2026".
6. **Wording**: core-hours 0.48 (001+002 combined, not "0.22, prior studies"); the audit
   defect-list citation is §2–§3 and §7, not §4–§5.

Deliverables: updated `result_card.json` (status stays partial; summary unchanged unless an
item above touches it), updated findings.md, the new table, re-rendered Fig 1, and
`results/fix_log.md` mapping each of the six items to the exact change. Do not touch
001/002/003 artifacts; everything lands in this study's directory except where 004's own
files are the subject (edit those in place in 004 is NOT allowed — copy the corrected
versions into THIS study and state in fix_log.md that 005 supersedes 004's findings.md,
card_corrections.csv and Fig 1).