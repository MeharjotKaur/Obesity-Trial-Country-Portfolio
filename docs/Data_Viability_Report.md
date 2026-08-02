# T0000 Data Viability Report

Audit run date: 2026-07-19

## Decision

**GO**, with a narrowed and explicitly labelled scope.

The verified data support a preliminary five-country portfolio screen for a hypothetical Phase III oral obesity drug programme. They do not support country-specific recruitment-rate or cost claims.

## ClinicalTrials.gov audit

The live API returned 713 interventional Phase III obesity records.

| Field | Present | Coverage |
|---|---:|---:|
| NCT ID | 713 | 100.00% |
| Overall status | 713 | 100.00% |
| Start date | 710 | 99.58% |
| Completion date | 693 | 97.19% |
| Enrollment | 708 | 99.30% |
| Lead sponsor | 713 | 100.00% |
| Interventions | 713 | 100.00% |
| Eligibility criteria | 713 | 100.00% |
| Locations | 644 | 90.32% |

Additional evidence:

- 74 unique location countries in the broad extract
- 170 multinational studies
- 404 completed, 80 recruiting, 55 active-not-recruiting, 49 terminated
- 325 unique lead sponsors
- 10,862 location records across 57 countries after the conservative relevance funnel

## Relevance funnel

| Filter | Remaining studies |
|---|---:|
| Phase III, interventional, obesity | 713 |
| Drug or biological intervention | 512 |
| Not exclusively paediatric | 490 |
| Title/condition does not identify diabetes | 364 |
| Start year 2010 or later | 281 |

This funnel proves sufficient volume but is not the final clinical taxonomy. Eligibility criteria must be checked because some non-diabetes obesity trials mention diabetes only as an exclusion, while some overlapping cardiometabolic trials may still be relevant competitors.

## External source audit

### NCD-RisC

- Download succeeded from the official country CSV.
- 13,200 country-year-sex rows.
- Includes obesity prevalence and lower/upper 95% uncertainty intervals.

### WHO Global Health Observatory

- Live endpoint returned 630 rows for 2022.
- 210 country codes.
- Both-sex, female, and male categories are present.

### World Bank

- Live population query returned 265 entities.
- 264 contained a non-null 2023 population value.

## Confirmed analytical uses

- Estimate population opportunity with uncertainty bounds.
- Quantify active relevant trial and location saturation.
- Identify historically experienced countries and facilities.
- Measure sponsor concentration and country trial footprint.
- Create a transparent multi-criteria country score.
- Select a constrained five-country portfolio.
- Test recommendation stability under alternate weights and prevalence uncertainty.

## Prohibited analytical claims

- Country-specific recruitment rate: enrollment is trial-level.
- Trial activation time by country: start dates are study-level.
- Country trial cost: not publicly available consistently.
- Causal country performance: multinational trials confound attribution.
- Final site selection: investigator capacity and contracting data are absent.
- Market demand for an approved drug: prevalence is not treated-patient demand.

## Scope lock

- Product archetype: oral obesity therapy
- Population: adults with obesity, without diabetes
- Phase: Phase III
- Historical window: 2010 onward
- Candidate set: 15–20 countries selected through explicit coverage thresholds
- Decision: select five countries
- Output label: preliminary country-portfolio screen

## Remaining gate before modelling

Manually validate a stratified sample of trial records and finalise inclusion/exclusion rules. No portfolio score will be calculated until that review is documented.
