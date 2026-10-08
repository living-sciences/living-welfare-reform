# 005-presentation-fixes — report

## Question

Close exactly the **six presentation items** the audit re-check raised against study 004's
deliverables for the Immervoll et al. (2007) living-update. All underlying numbers in 004 were
verified correct, so nothing is recomputed except item 1's trade-off table, which is *assembled*
from existing CSVs. The six items: (1) produce the corrected 14-country trade-off table 004's
findings claim exists; (2) complete `card_corrections.csv` with rows for the 002 and 003 cards;
(3) relabel Fig 1 to the gate-3b single-adult-67%-AW change; (4) label Portugal
"contradicted by the OECD change benchmark" like ES and IT; (5) fix two card fields (move the
−1.2 pp all-14 figure to a note; metric-1 gate years 2010–2025); (6) fix wording (core-hours
0.48; audit citation §2–§3 and §7). 004's own files must not be edited in place — the corrected
`findings.md`, `card_corrections.csv` and `Fig 1` are re-issued in this study, which supersedes
004's versions.

## Approach

Read-only inputs: the staged audit (`gate-conformance-inputs/immervoll-provenance.md`, §2–§3
and §7), 004's `findings.md` / `card_corrections.csv` / `result_card.json` / `recut.py` /
`make_corrections.py`, the 002 and 003 result cards (for the exact stale claims), and
`001/results/welfare_by_year.csv` and `gate3b_change.csv` (byte-identical in 002-cont). A fresh
container meant the venv was gone; I rebuilt a minimal one with only **matplotlib 3.11.2 / numpy
2.5.3** — enough to re-render Fig 1. **No EUROMOD run, no fetch, no recomputation** of any rate.

A single assembly script (`workspace/build.py`) produced the new table (read
`welfare_by_year.csv` 2026/V4, classified stability, flagged DK/ES), re-issued
`card_corrections.csv` (004's 12 rows + 6 new), and re-rendered Fig 1 (relabelled y-axis/title,
PT recoloured to "contradicted"). The card, findings, fix_log and this report were edited to
apply items 3–6.

## Results

### Item 1 — corrected trade-off table (new artifact + rendered)
`results/tradeoff_table_corrected.csv`, all 14 countries (2026, V4), incl. **EL and LU**.
Among the 10 Ψ-stable countries: **Ψ_w < Ψ_d in 8** (all but IE and SE, which flip to the
demogrant), **Ψ_w < 1 in 4** (BE, DE, LU, PT). **DK** carries the beta-step-dependent note
(−18.0 of the −24.3 pp fall is the 2025→26 beta step); **ES** carries the OECD-contradicted
note. The four Ψ-unstable countries (AT, DK, NL, ES) are n/a for the trade-off (≈100%
bottom-decile traps). Full table rendered in `results/findings.md`.

### Item 2 — card_corrections.csv completed (18 rows)
Carried 004's 12 rows (compute row updated per item 6); added 6:
4 for the **002 card** ("8 of 10", "−3.2 pp", "Denmark change-validated", the FI/LU/SE V_Δ
table) and 2 for the **003 card** (the "/14" denominators, the "0.22→0.13" headline over the
level-unvalidated frontier panel).

### Items 3 & 4 — Fig 1 re-rendered
Y-axis/title/caption now say **gate-3b PTR change for a single adult at 67% AW**, not
"bottom-quintile PTR change". **Portugal** is recoloured to the orange "contradicted by the OECD
change benchmark" group with ES and IT (PT: ours −11.2 vs +16.6 at AW67, −9.9 vs +9.4 at MINW —
opposite sign at both levels).

### Items 5 & 6 — card fields and wording
Metric 3 baseline is now "no same-definition 1998 baseline (V4 headline, q=0)" with the −1.2 pp
all-14 figure moved to its note; metric 1 is "(gate 3, 2010–2025)". Core-hours corrected to
**0.48** (001+002 combined); the audit defect-list citation is **§2–§3 and §7**.

### Comparison against 004 (what changed, numbers unchanged)

| Item | 004 (superseded) | 005 (corrected) | Source of truth |
|---|---|---|---|
| Trade-off table | claimed in findings, **file absent** | `tradeoff_table_corrected.csv`, 14 rows (8/10 Ψ_w<Ψ_d) | `001/results/welfare_by_year.csv` |
| card_corrections rows | 12 (001 + one 003 row) | 18 (+4 for 002 card, +2 for 003 card) | 002/003 result cards |
| Fig 1 y-axis | "bottom-quintile PTR change … AW67" | "PTR change, single adult at 67% AW … gate 3b" | gate-3b is a hypothetical-household change |
| Portugal | "fails 3b" (grey) | "contradicted by OECD change" (orange) | `001/results/gate3b_change.csv` PT rows |
| Metric 3 baseline | "-1.2 pp (all 14, UNVALIDATED)" | "no same-definition 1998 baseline (V4)"; −1.2 pp → note | spec §4 (no V4 1998 baseline) |
| Metric 1 label | "(gate 3, 2026)" | "(gate 3, 2010–2025)" | gate-3 window |
| Core-hours | "0.22 (prior studies)" | "0.48 (001+002 combined)" | 002 card "0.30 / 0.48"; `compute_log.csv` |
| Audit citation | "§4–§5 and §7" | "§2–§3 and §7" | `immervoll-provenance.md` section map |

No scientific quantity changed; this is a presentation correction only.

## Deviations & limitations

1. **No appended re-check section on disk.** `gate-conformance-inputs/immervoll-provenance.md`
   ends at §7 (the original audit, dated 2026-10-05); there is no dated re-check section at the
   end as the instruction describes. Impact: none — the six items are fully specified in the
   instruction itself, and I cross-checked each against §2–§3 and §7 of the staged file. This is
   the only substantive deviation.
2. **Fig 2 copied, not modified.** It is not one of the six items; it was copied unchanged into
   `005/results` so the superseding card is self-contained.
3. **004's numeric artifacts unchanged.** `baseline_1998_noUB.csv`, `findings_addendum_003.md`,
   `recut_values.json`, gate-completion CSVs and all values are left as-is in 004 (read-only);
   005 supersedes only the three presentation artifacts named in the instruction.
