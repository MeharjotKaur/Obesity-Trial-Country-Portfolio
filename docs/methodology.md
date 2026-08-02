# Methodology

## Decision question

Which five countries should a sponsor prioritise for further diligence for a hypothetical global Phase III oral obesity-pharmacotherapy programme in general adults without diabetes?

The unit of decision is a country portfolio. The project is a preliminary screen, not a site-feasibility or activation plan.

## Evidence pipeline

1. Query ClinicalTrials.gov API v2 for a broad Phase III interventional obesity universe.
2. Preserve the raw response with retrieval time, query, page count, record count and SHA-256 checksum.
3. Parse studies, interventions, conditions, sponsors and locations into relational tables.
4. Harmonise country names to ISO3 and retain unresolved records for audit.
5. Apply configurable relevance rules, followed by a stratified 70-record review sheet.
6. Freeze a conservative cohort of 117 general-adult obesity-pharmacotherapy studies.
7. Aggregate country evidence and join 2023 World Bank population with 2022 WHO obesity prevalence.
8. Screen countries and create four 0–100 decision pillars.
9. Solve a five-country binary integer programme under exposed portfolio constraints.
10. Re-solve under four strategic scenarios and 2,000 seeded assumption draws.

## Country screening

A country passes when it has at least two retained studies, at least five distinct registered facilities, and complete population and obesity-prevalence inputs. Forty-five countries passed. These thresholds limit extreme small-sample rankings; they do not prove operational readiness.

## Pillars and base weights

| Pillar | Weight | Construction | Attractive direction |
|---|---:|---|---|
| Patient opportunity | 30% | Population × adult obesity prevalence | Higher |
| Historical infrastructure | 30% | Facilities 45%, repeat facilities 25%, studies 20%, sponsor diversity 10% | Higher |
| Competitive headroom | 25% | Active trials per 10M proxy 65%, active sponsor count 35% | Lower raw pressure |
| Data confidence | 15% | Location completeness 45%, evidence depth 35%, indicator recency 20% | Higher |

Skewed count variables are transformed with `log1p`, winsorised at candidate-set tails and min–max normalised. Adverse competition variables are reverse-scored. Exact rules are executable in `src/build_decision_model.py` and configured in `config/scoring.yaml`.

The addressable-population measure is a burden proxy:

`population_2023 × obesity_prevalence_pct / 100`

It is not an estimate of eligible or recruitable patients.

## Optimisation

For candidate country `i`, binary variable `x_i` equals one when selected. For scenario `s`, the objective is:

`maximise Σ score(i, s) × x_i`

Subject to:

- exactly five countries;
- at least four regions;
- at most two countries per region;
- total opportunity score at least 300;
- total infrastructure score at least 250;
- at most one country with confidence below 60.

These are sponsor-planning assumptions. They are not presented as universal clinical-trial rules.

## Robustness

Four scenarios vary pillar priorities. Monte Carlo analysis draws 2,000 weight vectors around the balanced case using a Dirichlet distribution and independently jitters the opportunity and infrastructure thresholds by ±10%. The fixed seed is `20260731`.

This measures sensitivity to stated decision assumptions. It does not simulate future trial outcomes or propagate every source-data uncertainty.
