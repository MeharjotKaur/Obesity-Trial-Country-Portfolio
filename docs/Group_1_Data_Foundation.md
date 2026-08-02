# Group 1 — Data Foundation Checkpoint

Run date: 2026-07-31

## Status

**Superseded checkpoint.** Extraction, relational flattening, country harmonisation and preliminary taxonomy rules passed at this stage. The final deterministic cohort and its clinical-review limitation are documented in `Group_2_Decision_Model.md`; the completed portfolio is documented in `Group_3_Portfolio_Recommendation.md`.

## Verified production extract

- 717 Phase III interventional obesity records from ClinicalTrials.gov API v2.
- Eight API pages retrieved with a stable NCT ID check.
- 717 unique NCT IDs and no missing IDs.
- Atomic JSON write, parse-before-promotion validation, SHA-256 checksum, timestamp, query, and record count in the snapshot manifest.
- 21,636 study-location rows in the broad extract.

The source count increased from 713 in the 2026-07-19 viability audit to 717 on 2026-07-31. This is expected for a live registry and is why all reported results use a dated snapshot.

## Preliminary clinical taxonomy

After the first audit-driven revision, the deterministic rules retain 178 records and exclude 539. This is **not yet the final competitor cohort**.

| Exclusion reason | Records flagged |
|---|---:|
| No drug or biological intervention | 201 |
| Outside 2010+ window | 205 |
| No evidence of obesity-treatment intent | 360 |
| Non-pharmacological primary intent | 141 |
| Diabetes-primary overlap | 69 |
| Exclusively paediatric | 43 |
| Off-target therapeutic intent | 62 |

Reasons overlap, so counts do not sum to 539. Of the 178 rule-included records, 153 carry at least one review flag, commonly because diabetes appears only in eligibility text. That is often an exclusion criterion rather than evidence of a diabetes-primary trial, so those records are not automatically discarded.

A reproducible 70-record stratified audit sheet contains:

- 20 clean rule-included records.
- 25 rule-included records with review flags.
- 25 rule-excluded records.

No accuracy or precision claim will be made until a human reviewer completes `manual_label` and `reviewer_rationale`.

## Country and external-data validation

- 21,635/21,636 location rows mapped to ISO3 (reported as 100.00% after rounding).
- The only unresolved row is the historical entity `Serbia and Montenegro`; it is deliberately not forced into a modern country.
- 217 World Bank countries have 2023 population data in the reference table.
- The raw WHO response contains 630 sex-specific rows across 210 country codes for 2022. After excluding regional/income aggregates and entities without matching World Bank population data, 588 rows across 196 countries remain in the relational table.

The prior NCD-RisC file was found to be truncated (3,019 women-only rows across 92 ISO codes) and is excluded from production. It will be reinstated only after a fresh file passes completeness tests. Therefore, uncertainty intervals are not yet part of the production model.

## MySQL status

The MySQL 8 schema and transactional loader include primary keys, foreign keys, indexes, relationship tables, batch loading, rollback on failure and SQL data-quality queries. The complete layer was subsequently executed on MySQL 8.0.46; all 10 table counts reconciled and validation ended with `STATUS: PASS`.

## Historical gate to Group 2

This gate is retained as checkpoint history. The final build froze a conservative, fully inspectable 117-study deterministic cohort and completed the MySQL, scoring and optimisation layers. It does not claim independent clinical validation of the taxonomy.
