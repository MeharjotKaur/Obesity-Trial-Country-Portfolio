# Final validation report

Validated on 31 July 2026 against the included dated snapshot.

## Passed

- Raw ClinicalTrials.gov JSON parses and contains 717 unique study identifiers.
- Relational transformation preserves study-location integrity.
- 21,635 of 21,636 registered location rows map to ISO3; the one unresolved historical label is disclosed.
- Final therapeutic-intent cohort contains 117 studies across 53 countries.
- Forty-five countries pass the pre-specified evidence and indicator gates.
- All country scores are complete and bounded from 0 to 100.
- PuLP/CBC returns an optimal five-country base portfolio satisfying every constraint.
- Leave-one-out optimisation changes the portfolio for every selected country.
- All 2,000 seeded sensitivity runs are feasible and reproduce the published frequencies.
- 11/11 automated tests pass in a clean Python 3.12 virtual environment using pinned dependencies.
- Seven-slide executive deck renders without detected overflow and has been visually reviewed.
- Archive integrity and file-path hygiene checked before packaging.
- MySQL 8.0.46 live validation completed on 1 August 2026: all 10 table counts reconciled to CSV, all six SQL quality checks returned zero failures, and the validator ended with `STATUS: PASS`.

## MySQL validation

The schema, loader, checks, views and analytical queries were executed against MySQL 8.0.46. The loader populated all 10 relational tables; database row counts matched the packaged CSVs; referential-integrity, mapping, prevalence, scenario-size and selection-frequency checks all passed. The one unresolved historical label, `Serbia and Montenegro` for `NCT01272219`, remains deliberately unmapped and is narrowly documented in the SQL check rather than assigned an unsupported modern ISO3 code.

## Resume-claim status

The three proposed resume bullets in `docs/resume_and_project_pitch.md` are supported by reproduced Python outputs. The project may also accurately claim a locally executed and validated MySQL 8 relational layer.
