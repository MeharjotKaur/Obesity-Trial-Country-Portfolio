# Group 2 — Country Decision Model

Run date: 2026-07-31

## Status

**Passed for portfolio modelling, subject to stated clinical-review limitation.** The country feature pipeline, screening funnel, four-pillar score, MySQL analytical layer, figures and automated tests run reproducibly from the frozen Group 1 tables.

## Cohort freeze

The broad API query returned 717 Phase III interventional records associated with obesity. Group 1 retained 178 records after drug/biological, age, recency and therapeutic-intent rules. Group 2 adds a conservative title-level adjudication for the intended decision: a general adult obesity pharmacotherapy programme.

- Final analytical cohort: **117 studies**.
- Countries with at least one mapped location: **53**.
- Removed from the 178 preliminary records: off-target primary-disease studies, rare/genetic obesity programmes, paediatric programmes and records without explicit general weight-management intent.

This is a deterministic public-data taxonomy, not a clinical systematic review. The complete 717-record decision ledger is published in `data/processed/trial_taxonomy_final.csv`, so every decision is inspectable. No sensitivity, specificity or clinical-validation claim is made.

## Candidate screening

Countries must have:

1. At least two final-cohort studies.
2. At least five unique registered facility keys.
3. World Bank population coverage.
4. WHO both-sex obesity-prevalence coverage.

Result: **45 candidate countries across seven World Bank regions**.

The gate is an evidence-quality screen, not a claim that excluded countries are operationally infeasible. The full funnel and one exclusion reason per country are in `data/processed/country_screening_funnel.csv`.

## Features and score

| Pillar | Weight | Inputs | Interpretation |
|---|---:|---|---|
| Opportunity | 30% | population × adult-obesity prevalence | burden proxy; not eligible patients |
| Infrastructure | 30% | facilities, repeat facilities, studies, sponsor diversity | registered historical experience proxy |
| Competitive headroom | 25% | active trials per 10m burden proxy, active sponsors | lower current pressure scores higher |
| Data confidence | 15% | geocoding completeness, evidence depth, indicator recency | confidence in screening evidence |

Skewed count variables use `log(1+x)` before within-candidate min–max scaling. Adverse competition metrics are reverse-scaled. Pillar weights are assumptions stored in `config/scoring.yaml`, not learned parameters.

Base-case score leaders are the United States, China, India, Brazil and Mexico. This is **not yet the recommended portfolio**: Group 3 will apply geographic and portfolio-level constraints, compare the result with the naïve top five, and test robustness.

## Key limitations

- WHO adult obesity prevalence is multiplied by total population, so the result is a relative burden proxy rather than an adult or trial-eligible population estimate.
- A registered location indicates listed participation, not availability, quality, capacity or recruitment speed.
- Study enrollment is never allocated across countries.
- Active registered trials proxy competitive pressure; they do not represent full commercial intelligence.
- Country rankings are relative to the screened candidate set and the declared weights.
- The taxonomy has deterministic auditability but not independent clinician adjudication.

## Reproduction

```bash
python src/build_decision_model.py
python src/create_group2_figures.py
python -m unittest discover -s tests -v
```

The schema, idempotent reload logic, analytical views and queries were subsequently executed on MySQL 8.0.46. All 10 table counts reconciled, all six SQL quality checks returned zero failures, and validation ended with `STATUS: PASS`.
