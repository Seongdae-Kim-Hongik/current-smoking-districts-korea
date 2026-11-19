# Current smoking across districts of South Korea, 2011-2024

Analysis code for a manuscript on the district geography of age-sex-standardised current smoking prevalence from the Korea Community Health Survey and its district-level correlates.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24359329 (v1.0.0).

This code is released under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (analytic panel, result tables and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/SMOK/` | Model settings (`sets_SMOK_std3.json`, `config_SMOK_std3.json`), the model chain (`run_fh_chain.sh`) and the district adjacency graph (`graph_593.graph`) |
| `04_분석/SMOK/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Current smoking prevalence, male current smoking prevalence, perceived stress and high-risk drinking among drinkers (age-sex-standardised rates, standard errors and respondent counts by district): Korea Community Health Survey, Korea Disease Control and Prevention Agency (KOSIS).
- Entertainment and singing bars: Ministry of the Interior and Safety local licensing data.
- University-educated share, basic livelihood security recipients, single-person households, crude divorce rate, structural controls and negative controls: Statistics Korea (KOSIS) and local indicators.

## Pipeline

Set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database, then run from the repository root.

| Step | Script | Output |
|---|---|---|
| 1 | `99c_extra_canonical_pool_smok.py` | District covariate pool (welfare recipient correction, education, bar density) |
| 2 | `99SM_smok_fh_prep.py` | Logit outcome and known sampling variance (Fay-Herriot), secondary and survey-operation indicators |
| 3 | `99SM0_smok_sqlite_crosscheck.py` | Cell-by-cell check of inputs against the read-only district database |
| 4 | `80_build_disease_panel_v.py SMOK` (`ST_VER=std3`) | Analytic panel (imputation, standardisation, VIF) |
| 5 | `81fh_smok.R SMOK` via `04_분석/SMOK/run_fh_chain.sh` | Main spatiotemporal Fay-Herriot model, set comparison, multiverse of all covariate subsets, Knorr-Held models (`kh_constraints.R`), decomposition, windows, lags, leave-one-province-out, likelihoods, graph and prior, secondary outcome, RSR, Spatial+, survey-based covariate and survey-operation checks |
| 6 | `99SM3_smok_comparators.py`, `99SM4_smok_maps.py` | Descriptive comparisons and maps |
| 7 | `04_분석/SMOK/MS/build/` | Manuscript numbers, tables, figures and supplementary material |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path. R jobs are wrapped in `rslot.sh` and run with one INLA thread.

## Software

R 4.6.0 with R-INLA, spdep and sf; Python 3.9 with pandas, geopandas, numpy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
