# Source register

| Source | Production use | Snapshot/period | Access | Key limitation |
|---|---|---|---|---|
| ClinicalTrials.gov API v2 | Trial metadata, interventions, sponsors, enrollment metadata and registered locations | Retrieved 31 Jul 2026 | <https://clinicaltrials.gov/data-api/api> | Registration practices vary; locations are not proof of current site capacity; enrollment is study-level |
| WHO Global Health Observatory | Adult obesity prevalence used in country opportunity proxy | 2022 estimate | <https://www.who.int/data/gho> | Modelled country estimate; not programme-specific eligibility |
| World Bank Indicators API | 2023 population and country/region reference | 2023 | <https://api.worldbank.org/> | National population is broader than the adult target population |
| NCD Risk Factor Collaboration | Considered for uncertainty enrichment | Not used | <https://www.ncdrisc.org/> | Available saved extract failed completeness checks and was excluded |

The API query and exact extraction metadata are recorded in `data/raw/clinical_trials_2026-07-31_manifest.json`. Raw snapshots are included to preserve the published result even when live sources change.

No source supplies country-level recruitment speed, trial cost, investigator availability or probability of success. The project does not infer those outcomes.
