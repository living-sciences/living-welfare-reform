# Welfare Reform in European Countries (Immervoll, Kleven, Kreiner and Saez, EJ 2007)

This repository holds the working directory of an AI-agent replication of the
paper, together with the extension studies that carry its analysis forward to
the tax-benefit rules of 2009 through 2026. It backs the living-paper page:

**https://livingscience.ai/econ/living-welfare-reform**

## The paper

Immervoll, H., Kleven, H. J., Kreiner, C. T., and Saez, E. (2007). Welfare
Reform in European Countries: A Microsimulation Analysis. *The Economic
Journal* 117 (January), 1-44. https://doi.org/10.1111/j.1468-0297.2007.02000.x

## What is here

- `run/replication/` is the replication run. The paper's numbers come from the
  authors' own simulation spreadsheet, `EUROMOD.xls` (the October 2005
  "Simulation File in Excel format" recovered from Emmanuel Saez's website,
  https://eml.berkeley.edu/~saez/EUROMOD.xls), and `codebase/` holds that
  workbook, CSV exports of each of its sheets, the shipped prep check, and the
  scripts the agent wrote to re-implement the paper's closed-form formulas and
  rebuild Tables 2a, 2b, 3, 4 and 6 and Figures 1 and 2 (outputs in
  `codebase/results/` and `codebase/figures/`). `replication_log.json` and
  `evidence_summary.json` record each step, and `suspicions.json` lists the
  points where the agent's numbers and the paper's text did not line up.
- `run/followup/` holds the extension studies, numbered in the order they ran.
  Each has its `instruction.md` (the study's specification), `workspace/`
  (code and checkpoints), `results/`, `report.md`, `results/findings.md` and
  `result_card.json`:
  - `001-living-update` recomputes the paper's participation and marginal tax
    rates under EUROMOD's 2009-2026 rules for 14 countries, holding the
    paper's 1998 cell weights and formulas fixed, and asks whether the
    in-work-transfer-beats-demogrant ranking still holds.
  - `002-living-update-cont` is the continuation of 001: it reuses 001's
    headline runs unchanged and completes the five pre-declared sensitivity
    variants (earnings dispersion, hours, children, rent, social-contribution
    base).
  - `003-theory-update` reads the updated rates through optimal-transfer
    theory, asking how the paper's result depends on the participation
    elasticity; it runs no new simulations.
  - `004-gate-conformance` re-cuts the 001-003 cards to the study
    specification's own validation rules, after an internal audit found that
    the rates were computed correctly but the headlines were reported over
    country sets that had not passed the OECD validation gates. Its corrected
    headline is an honest partial: only Denmark, France and the Netherlands
    pass the level gate, and among them the ranking holds in France, while
    the Danish and Dutch trade-offs are numerically undefined in 2026.
  - `005-presentation-fixes` closes six presentation items raised on 004
    (the full corrected 14-country trade-off table, completed card
    corrections, figure relabelling and wording), recomputing nothing.

  **004 and 005 supersede the earlier cards.** The 001, 002 and 003 studies
  stay here untouched because their numbers trace and are reused, but their
  headline claims (in particular the "8 of 10 countries" result) are
  descriptive statistics over an unvalidated country set, and
  `005-presentation-fixes/result_card.json` is the current card.
  `004-gate-conformance/results/card_corrections.csv`, re-issued and completed
  in 005, maps each old claim to its corrected form.

The internal audit and study-specification files that 004 and 005 cite
(`gate-conformance-inputs/immervoll-provenance.md`, `spec-living-update.md`)
are part of our review process and are not shipped; the specification's
content appears in the 001-003 `instruction.md` files.

## Re-running

The replication needs only Python 3 with `numpy`, `scipy`, `matplotlib` and
`xlrd` (see `run/replication/installed_packages.txt`) and the workbook that is
already in `run/replication/codebase/`.

The extension studies also need the EUROMOD tax-benefit model, J2.54+ (and
J2.0+ for the beta-versus-stable check), published by the European
Commission's Joint Research Centre under CC BY 4.0 at
https://euromod-web.jrc.ec.europa.eu/download-euromod, plus the `euromod`
Python connector (0.4.0) and a .NET 8 runtime, and the Eurostat and OECD
TaxBEN series named in each study's sources. These inputs were staged
read-only for the runs and are not in this repository; `LARGE_FILES_OMITTED.md`
lists every one of them with its source and the SHA-256 of the exact bytes
used. Paths in the scripts and in `workspace/env.sh` are the container paths
the runs used (`/workspace/eval/...`), so point them at your own copies.

## Terms

`EUROMOD.xls` and the CSV exports of its sheets in
`run/replication/codebase/cached_values/` are the authors' material (copyright
Immervoll, Kleven, Kreiner and Saez, October 2005), and the copies of the
workbook under `run/followup/*/workspace/` are byte-identical to it
(SHA-256 `810743354f155dfe5d2b3c258db4969740f1f966327433ba94bf8f4b03533e6c`).
They are included so the replication can be read and re-run, and they remain
under the authors' and their publishers' terms. The EUROMOD model and the
Eurostat and OECD data are subject to their publishers' licences. Everything
else in this repository is output of the AI-agent pipeline.

## Caveats

These are automated runs reviewed by people, not the authors' own work. The
extension studies are policy-rules-only updates on hypothetical households:
the 1998 point comes from the paper's microsimulation and the 2009-2026 points
from a different method, the UK is out of scope (it left EUROMOD), and the
2026 rules come from a beta release. Read each study's `report.md` and the
Notes on the living page before quoting a number.
