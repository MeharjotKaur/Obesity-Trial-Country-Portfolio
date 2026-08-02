# Implementation Tickets

## T0000 — Data viability audit

Status: completed

- Live source extraction
- Field completeness profiling
- Relevance funnel
- External source verification
- Scope and non-claim lock

## T0001 — Clinical taxonomy and audit sample

Status: completed with disclosed clinical-review limitation

- Write formal inclusion/exclusion rules
- Draw a stratified manual-review sample
- Label drug modality and population overlap
- Measure rule precision on the reviewed sample

## T0002 — Reproducible source ingestion

Status: completed

- Configuration-driven API client
- Pagination, retries, timestamps, and checksums
- Raw snapshot manifest
- Structured logging

## T0003 — Relational transformation

Status: completed

- Flatten study entities
- Normalise countries and sponsors
- Generate stable facility keys
- Validate row grains and relationships

## T0004 — MySQL analytical layer

Status: completed and live-validated on MySQL 8.0.46

- Create schema and indexes
- Load staging tables
- Add analytical views
- Write SQL data-quality checks

## T0005 — Candidate-country feature mart

Status: completed

- Patient opportunity
- Competition
- Experienced sites
- Readiness
- Data confidence
- Candidate eligibility thresholds

## T0006 — Scoring and uncertainty

Status: completed for assumption sensitivity; prevalence uncertainty excluded after source completeness failure

- Transformation and normalisation rules
- Base weights
- Alternative sponsor scenarios
- Prevalence uncertainty propagation

## T0007 — Portfolio optimisation

Status: completed

- PuLP formulation
- Constraint tests
- Infeasibility diagnostics
- Alternative feasible portfolios

## T0008 — Robustness analysis

Status: completed

- Monte Carlo weight sampling
- Selection frequency
- Rank stability
- Leave-one-pillar-out analysis

## T0009 — Power BI decision dashboard

Status: excluded from the final MVP; the verified seven-slide executive deck is the visual decision deliverable

- Executive overview
- Country comparison
- Competition and site footprint
- Portfolio scenario explorer
- Robustness and confidence page

## T0010 — Consulting deliverables

Status: completed

- Executive deck
- README and methodology
- Data dictionary
- Limitations register
- Interview defence guide

## T0011 — Final verification

Status: completed

- Automated tests
- Re-run from clean environment
- Executive-deck number reconciliation
- Claim and citation audit
