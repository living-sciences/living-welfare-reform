# Findings — 005-presentation-fixes (supersedes 004-gate-conformance/results/findings.md)

> **This document supersedes `004-gate-conformance/results/findings.md`**, together with
> 004's `card_corrections.csv` and `Fig 1` (which are re-issued in this study's `results/`).
> 004's underlying analysis and numbers were all verified correct by the audit re-check; 005
> changes **only the six presentation items** the re-check flagged, recomputing nothing except
> item 1's trade-off table, which is *assembled* (not re-simulated) from existing CSVs. 004's
> files remain untouched on disk.

## What this study is

An artifact-level correction of the living-update follow-ups (`001-living-update`,
`002-living-update-cont`, `003-theory-update`), continuing 004. The provenance audit found
**data provenance CLEAN, memory CLEAN, and gates 0/1/4 and the continuation handling CLEAN**;
the defect was in the **reporting layer**, which violated the spec's own validation rules
(`spec-living-update.md` §4, §6). The authoritative defect list is the audit **§2–§3 and §7**
(the gate-compliance table, the card-vs-disk table, and the publication checklist). This card
supersedes the 001/002/003/004 cards for publication; the old studies stay on disk untouched.

No new EUROMOD simulations were run in 005. All result CSVs from 001/002/003 (and 004's three
gate completions) are treated as correct computations; the job here is honest presentation.

## Item 1 — the corrected equity-efficiency trade-off table (2026, V4)

004's findings claimed a re-cut trade-off table "adds EL, LU; DK and ES shown separately" but
never wrote the table out. Here it is, **all 14 countries**, assembled from
`followup/001-living-update/results/welfare_by_year.csv` (byte-identical to 002-cont's copy),
2026, V4 (q=0). `Ψ_w < Ψ_d` is counted **only where Ψ is stable**; the four Ψ-unstable
countries (AT, DK, NL, ES — bottom-decile PTR/MTR ≈ 100% participation traps) carry n/a.
**DK is flagged beta-step-dependent; ES, IT and PT are flagged OECD-contradicted.** V (OECD level-validated) = {DK, FR, NL}, marked ✓V below; FR and EL are τ-unvalidated (gate 3c aborted), marked τ?. Flags added per the audit final check (orchestrator correction, see fix_log.md).

| Country | Ψ_d (2026) | Ψ_w (2026, V4) | Ψ_w < Ψ_d | Ψ_w < 1 | Ψ stable | Note |
|---|---|---|---|---|---|---|
| AT | undefined | 52.96 | n/a | n/a | unstable | Ψ unstable (≈100% bottom-decile trap) |
| BE | 4.66 | 0.0001 | yes | yes | stable | |
| DK ✓V | undefined | undefined | n/a | n/a | unstable | **beta-step-dependent**: −18.0 of the −24.3 pp 2009→2026 bottom-q PTR fall is the single 2025→2026 J2.54+ beta step (no gate covers it); Ψ undefined 2026 |
| FI | 4.326 | 2.446 | yes | no | stable | |
| FR ✓V τ? | 3.051 | 2.137 | yes | no | stable | |
| DE | 2.395 | 0.7103 | yes | yes | stable | |
| EL τ? | 1.487 | 1.216 | yes | no | stable | |
| IE | 2.129 | 2.574 | **no** (flips to demogrant) | no | stable | |
| IT | 1.783 | 1.560 | yes | no | stable | **contradicted by OECD change** (3b: ours +22.9 vs −7.4) |
| LU | 9.041 | −0.00 | yes | yes | stable | |
| NL ✓V | undefined | 251.3 | n/a | n/a | unstable | Ψ unstable (≈100% bottom-decile trap) |
| PT | 2.193 | 0.3992 | yes | yes | stable | **contradicted by OECD change** (3b: ours −11.2 vs +16.6 AW67; −9.9 vs +9.4 MINW) |
| ES | undefined | 198.3 | n/a | n/a | unstable | **contradicted by OECD change** (3b: ours +34.7 vs +9.8 AW67; +46.6 vs −1.1 MINW); fails gate-3 levels (0.21); Ψ undefined 2026 |
| SE | 2.896 | 3.113 | **no** (flips to demogrant) | no | stable | |

**Among the 10 Ψ-stable countries: Ψ_w < Ψ_d in 8** (all but IE and SE, which flip to the
demogrant), **Ψ_w < 1 in 4** (BE, DE, LU, PT). This is the descriptive, OECD-**unvalidated**
"8 of 10". The OECD-level-validated set is V = {DK, FR, NL}; on it the trade-off is computable
only for FR (1 of 3; DK & NL Ψ undefined). Machine-readable copy:
`results/tradeoff_table_corrected.csv`.

## The gate-conformant cut (carried from 004, numbers unchanged)

### Validated set and the honest-partial rule
- **V = {DK, FR, NL}** (gate-3 no-UB passers; NL added by 004's gate-3 completion, within-5pp
  0.92). |V| = 3 < 10, so the spec's honest-partial rule applies: headline is **"OECD-validated
  in 3 of 14"**, never compared with the paper's 15-country statements. All-14 numbers appear
  only in a labelled **"unvalidated levels"** panel.
- **V_Δ = {DK, FR, NL}** (gate-3b passers ⊆ V).

### Headline estimand E3 (2026, V4), over V, with the Table 5(b) baseline
- **Ψ_w < Ψ_d: 1 of 3** — France only; **Denmark and the Netherlands have numerically
  undefined Ψ in 2026** (bottom-decile ≈100% participation traps). Same-set **1998 no-UB
  baseline (Table 5b): 3 of 3**.
- **Ψ_w < 1: 0 of 3** well-defined (FR = 2.14). 1998 no-UB baseline: **1 of 3** (DK, Ψ_w 0.36).

### Bottom-quintile PTR change (E5), over V_Δ
- **Median 2009→2026 = −5.2 pp** over V_Δ = {DK, FR, NL} (DK −24.3, FR −5.2, NL −0.2).
- The **{DK, FR}-only** two-country median is **−14.7 pp**, retained as a DK-beta-dominated
  sensitivity.
- **All-14 median = −1.2 pp**, shown only as a labelled **unvalidated** panel. The old
  **−3.2 pp** figure (over the non-conforming V_Δ = {DK,FI,FR,LU,NL,SE}) is **dropped**.
- **ES, IT and PT are removed** from the PTR-change metric: the OECD change benchmark
  **contradicts** them —
  ES AW67 ours **+34.7** vs TaxBEN **+9.8** (MINW +46.6 vs −1.1);
  IT AW67 ours **+22.9** vs **−7.4** (opposite sign);
  **PT ours −11.2 vs +16.6 (AW67) and −9.9 vs +9.4 (MINW) — opposite sign at *both* earnings
  levels** (item 4: PT is therefore "contradicted by the OECD change benchmark", not merely
  "fails 3b", exactly like ES and IT).

### Denmark's fall, attributed correctly
- Denmark −24.3 pp (2009 86.1 → 2026 61.8), **of which −18.0 pp is the single 2025→2026
  beta-rules step** (79.85 → 61.83). Only −6.2 pp is the gradual 2009→2025 move. **No gate
  covers the 2026 beta step** (gate 4 checks 2025; DK's gate 3b covers 2010→2024 AW67 only).

### Same-set 1998 baselines
- Descriptive Ψ-stable-10 vs 1998 **mixed-q** (`table2a.csv`): Ψ_w < Ψ_d **10 of 10**;
  Ψ_w < 1 **3 of 10** (FR, IE, PT). Validated V vs 1998 **no-UB** (Table 5b): as above.
- The old "14 of 14" and "5 of 15" baselines (cross-set / cross-regime) are retired.

### Small-error fixes
- **Ψ_w < 1 (2026) list = {BE, DE, LU, PT}** (the old findings said "DE, EL, PT and BE"; EL =
  1.22 is **not** < 1; LU = −0.00 **is** < 1 and was omitted).
- **Core-hours = 0.48** — the **001+002 combined** logged figure (001 0.22 logged + 002 0.26 logged; 0.30 was the 002 card's self-reported figure). The old "0.7" was untraceable, and 004's "0.22, prior
  studies" understated it (0.22 is 001 alone). 004's three gate completions added ~0.1; 005
  (table assembly only) adds negligible compute.

## The six presentation items closed in 005

| # | Item | Fix |
|---|---|---|
| 1 | Corrected trade-off table missing | Produced `tradeoff_table_corrected.csv` + rendered above: all 14 incl. EL/LU; DK beta-step-dependent; ES OECD-contradicted. |
| 2 | `card_corrections.csv` incomplete | Added 6 rows: 002 card ("8 of 10", "−3.2 pp", "Denmark change-validated", the FI/LU/SE V_Δ table) and 003 card ("/14" denominators, "0.22→0.13" headline). |
| 3 | Fig 1 mislabelled | Y-axis/caption now say **gate-3b PTR change for a single adult at 67% AW**, not "bottom-quintile PTR change". PNG re-rendered. |
| 4 | Portugal mislabelled | PT is now **"contradicted by the OECD change benchmark"** (opposite sign at both levels), like ES and IT — in Fig 1 (orange) and the card. |
| 5 | Card field errors | "−1.2 pp all-14" moved from the PTR-change metric's **baseline** to its **note** (no same-definition 1998 baseline exists under V4); metric 1's gate years corrected to **2010–2025** (not "gate 3, 2026"). |
| 6 | Wording | Core-hours **0.48** (001 0.22 + 002 0.26 logged; 0.30 was 002's self-report); audit defect-list citation **§2–§3 and §7** (not §4–§5). |

A line-by-line map of each item to the exact change is in `results/fix_log.md`.

## Deviations

1. **The staged provenance file has no appended "re-check" section.**
   `gate-conformance-inputs/immervoll-provenance.md` on disk ends at §7 (the original audit,
   dated 2026-10-05); there is no dated re-check section at the end as the instruction
   describes. The six items are, however, fully specified in the 005 instruction itself, so
   scope was unambiguous; I worked from that enumeration and from §2–§3/§7 of the staged file.
2. **No recomputation.** Per the instruction, nothing was re-simulated; item 1's table is
   assembled from `welfare_by_year.csv`. The only compute was installing matplotlib/numpy in a
   fresh container to re-render Fig 1 (no data fetched; no EUROMOD run).
3. **Fig 2 copied unchanged** into 005/results so the superseding card is self-contained; it is
   not one of the six items and was not modified.
