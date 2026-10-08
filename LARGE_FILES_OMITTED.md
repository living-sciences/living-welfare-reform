# Files used by the runs but not shipped in this repository

The extension studies under `run/followup/` read their inputs from a staged,
read-only folder that the containers saw at
`/workspace/eval/followup_staging/shared-data/` (each study's
`workspace/shared-data` was a symlink to it). That folder is not part of this
repository: the two EUROMOD model archives are far too large for git, and the
rest is third-party data that is better fetched from its publisher. Everything
below can be re-downloaded from the listed source; the SHA-256 values are the
exact bytes the runs used, so you can confirm you have the same files.

To re-run an extension study, recreate this folder (same relative paths) and
point the `J2_54`, `J2_0` and `SHARED` variables in `workspace/env.sh` at it.

## EUROMOD tax-benefit model (EUROMOD, European Commission JRC; CC BY 4.0)

Official download page: https://euromod-web.jrc.ec.europa.eu/download-euromod

| Staged path | Size | SHA-256 | Provenance |
|---|---|---|---|
| `euromod/EUROMOD_RELEASES_J2.54+.zip` | 222,678,380 bytes | `2ec46bc5f13d5007d8b0fb5bf651fd9993fdebdb1ce308bb36cb822ff21aa1ac` | EUROMOD **J2.54+** (beta, September 2026), the headline model for 2009-2026 policy systems. Direct link used: https://euromod-web.jrc.ec.europa.eu/sites/default/files/2026-09/EUROMOD_RELEASES_J2.54%2B.zip (downloaded 2026-10-05). |
| `EUROMOD_RELEASES_J2.0+.zip` | 206,048,247 bytes | `eb30758d9ab26f740818d62024282a9362a8b0b7879e32fb854744cf5e6f2b0a` | EUROMOD **J2.0+** (stable, February 2026), used only for the beta-vs-stable check (gate 4, policy year 2025). Same download page. |
| `euromod/EUROMOD_policy_parameters_all_J2.54+.xlsx` | 3,465,694 bytes | `8186e716217c0d963270e6c08820127d49cab7d54004df3cad87dbe7dbfd400a` | EUROMOD J2.54+ policy-parameter workbook (all countries), from the same release page. |
| `euromod/EM_Whatsnew_J2.54+_beta.pdf` | 341,356 bytes | `0c921f11962fa935249d7f726d62ea8631104ce80aff472c30d049612673aebe` | Release notes, https://euromod-web.jrc.ec.europa.eu/sites/default/files/2026-09/EM_Whatsnew_J2.54%2B_beta.pdf |
| `EM_statistics_I5.0+.xlsx` | 523,996 bytes | `1da1be1ca93c6d73f83d6a5c8d9f309dc93d4e0ffd20567c499c4e454b50d408` | EUROMOD statistics workbook, input data release I5.0+, from the EUROMOD website. |
| `euromod/HHoT_baseline.xml` | 1,155,775 bytes | `2227402a95ac5ca26542b4bb87f2672751d06afddf0d77d10cfc752494ddb3c1` | Hypothetical Household Tool defaults template, https://github.com/ec-jrc/JRC-EUROMOD-software-source-code, `EM_Plugins/Hypothetical Household/data/HHoT_baseline.xml` (commit of 2021-01-29, EUPL-1.2). |

The Python connector (`euromod` 0.4.0 from PyPI) and the .NET 8 runtime were
installed at run time, not staged.

## Eurostat and OECD series (fetched 2026-10-05 from the public APIs)

Eurostat: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<dataset>?format=JSON&...`
OECD: `https://sdmx.oecd.org/public/rest/data/OECD.ELS.JAI,DSD_TAXBEN_PTR@<flow>,/all?startPeriod=2001&dimensionAtObservation=AllDimensions&format=csvfilewithlabels`

| Staged path | Size | SHA-256 | Source dataset |
|---|---|---|---|
| `benchmarks/oecd_taxben_DF_PTRSA_EU15.csv` | 1,731,321 | `4e454222b0724fa55fcb680a5e0127840d53733f904fad5ad21e6fd3e438112a` | OECD TaxBEN participation tax rates, social assistance (`DF_PTRSA`) |
| `benchmarks/oecd_taxben_DF_PTRUB_EU15.csv` | 7,077,656 | `5720f7ea9f6b519282cbe5bbd08bcf542cef65cc4387efe6b7f04e46f1a94a2f` | OECD TaxBEN participation tax rates, unemployment benefit (`DF_PTRUB`) |
| `earnings/earn_nt_net_AW100_GRS_NAC.json` | 8,645 | `418fd127eaa3420e16fc352b81c56f754c90ad136b439771dbcbe7eb7cd5f512` | Eurostat `earn_nt_net` (gross average wage) |
| `earnings/earn_mw_cur_EU14.json` | 21,449 | `f6a53e08abb94b4f649ff1df655dc278a88d70042216995ca13a4828e67dd9ea` | Eurostat `earn_mw_cur` (statutory minimum wages) |
| `earnings/earn_ses_adeci.json` | 3,848 | `e7a9779fc70838d49529f3a7cb3ab558d9c18ebf379ba0a2f7dd1716a91bb4cf` | Eurostat `earn_ses_adeci` (SES 2006 earnings deciles) |
| `earnings/earn_ses10_adeci.json` | 3,856 | `db55c61e73e5657f29f78d68032a0741bf4740acf29078d196b11f13784376c1` | Eurostat `earn_ses10_adeci` |
| `earnings/earn_ses14_adeci.json` | 4,604 | `d9bc48fe2022ddd4f7de78ea83c751fd21c8cc6141b2bc9094d00f59995e9dc7` | Eurostat `earn_ses14_adeci` |
| `earnings/earn_ses18_adeci.json` | 5,761 | `0f4077a45e444934e4ecf097a65f3bc8cab7602e5f49a85a5eee56b686663cf7` | Eurostat `earn_ses18_adeci` |
| `earnings/earn_ses22_adeci.json` | 7,031 | `de55d94b79d5bbc516d789f1d01d85dd656caf81d4f40bffaedfb45050753d77` | Eurostat `earn_ses22_adeci` |
| `ctr/gov_10a_taxag_D211_D214.json` | 15,754 | `7617d3d0aeed151554891bca2cb150e3ba13132d2cad4f873e43995f817cdc93` | Eurostat `gov_10a_taxag` (D211, D214) |
| `ctr/nama_10_gdp_P31S14_P3S13.json` | 17,875 | `5593742dfc4d02152144cc9b4a200a37fa741366d4539fc3f7241a1498653a42` | Eurostat `nama_10_gdp` (P31_S14, P3_S13) |
| `ctr/gov_10a_main_D1PAY.json` | 9,981 | `9944bd5dc10b3da79720d2f7fae228e51ec14bebb9a95dfc97397ec374a67828` | Eurostat `gov_10a_main` (D1PAY) |
| `labour/lfsa_pganws_ages.json` | 135,160 | `e147922bad0dc6353c79182378957743ca146da3d9ab125f5c452761c92b0c41` | Eurostat `lfsa_pganws` |
| `labour/lfsa_ugad_Y15-59_Y15-64.json` | 122,506 | `f234e7ffe052f5149d0a6eb9686689d71637055bd26224cb98fa5eb6195c091f` | Eurostat `lfsa_ugad` |
| `labour/lfsa_ugadra_Y15-59_Y15-64.json` | 272,575 | `56e1c7bc4b7f59828f6b68e2e9dca75dfd4d9d38ace4b85fe45ba61e54034496` | Eurostat `lfsa_ugadra` |

## Pre-run prototypes (written by us before the runs; not part of any study)

`prototype/` held five small planning scripts and inputs (household-builder
prototype for Austria, an add-on probe, a calibration check against OECD
TaxBEN, a container recipe, and `calib_inputs.json`). They were written while
scoping the extension, before any study ran, and are superseded by the
studies' own `workspace/` code, so they are not shipped.

## Not shipped for copyright reasons

The paper itself (The Economic Journal, Wiley) and the CEPR discussion paper
version (CEPR DP4324) are not included; both are available from the
publishers and from https://eml.berkeley.edu/~saez/.
