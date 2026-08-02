# Data Dictionary — Group 2 Decision Variables

All country metrics are derived from the dated ClinicalTrials.gov snapshot, World Bank 2023 population and WHO 2022 both-sex adult-obesity prevalence.

| Field | Definition | Direction | Important limitation |
|---|---|---|---|
| `relevant_studies` | Distinct final-cohort studies listing the country | Higher supports infrastructure | Registry history, not performance |
| `active_trials` | Distinct final-cohort studies in an active status | Lower supports headroom | Registry status can lag reality |
| `recent_trials` | Distinct final-cohort studies starting in 2021+ | Context only | Does not measure completion quality |
| `unique_facilities` | Distinct normalised facility keys | Higher supports infrastructure | Names may vary; listing ≠ availability |
| `repeat_facilities` | Facility keys appearing in at least two cohort studies | Higher supports experience | Does not prove current capacity |
| `sponsor_diversity` | Distinct lead sponsors represented | Higher supports ecosystem breadth | Public sponsor names require no ownership inference |
| `active_sponsor_count` | Distinct lead sponsors with active cohort studies | Lower supports headroom | Competition proxy only |
| `population_2023` | World Bank total population | Input | Not adult population |
| `obesity_prevalence_pct` | WHO 2022 adult both-sex obesity prevalence | Input | Estimate, not trial eligibility |
| `obese_population_proxy` | total population × adult prevalence / 100 | Higher supports opportunity | Deliberately labelled proxy |
| `active_trials_per_10m_proxy` | active trials per 10m burden-proxy persons | Lower supports headroom | Denominator is not eligible patients |
| `location_completeness` | location rows with coordinates / all location rows | Higher supports confidence | Geocoding is only one quality dimension |
| `evidence_depth` | log-scaled relevant-study count relative to maximum | Higher supports confidence | Relative to this snapshot |
| `indicator_recency` | `1 / (1 + 2026 - indicator_year)` | Higher supports confidence | Simple transparent decay assumption |
| `opportunity_score` | log-min–max scaled burden proxy | Higher is attractive | Candidate-relative 0–100 scale |
| `infrastructure_score` | weighted infrastructure components | Higher is attractive | Assumption-driven proxy |
| `competitive_headroom_score` | reverse-scaled competition components | Higher is attractive | Not commercial forecast |
| `data_confidence_score` | weighted evidence-quality components | Higher is attractive | Does not eliminate source bias |
| `attractiveness_score` | 30% opportunity + 30% infrastructure + 25% headroom + 15% confidence | Higher is attractive | Not objectively correct or universal |

## Group 3 model outputs

| Field | Definition | Important limitation |
|---|---|---|
| `model_score` | Scenario-specific weighted sum of the four pillar scores | Depends on declared scenario weights |
| `selection_count` | Number of feasible Monte Carlo runs selecting the country | Measures assumption sensitivity only |
| `selection_frequency_pct` | `selection_count / feasible_runs × 100` | Not probability of trial success |
| `portfolio_iso3` | Sorted ISO3 identifiers for one simulated portfolio | Ordering has no priority meaning |
| `objective_value` | Sum of selected scenario-specific model scores | Comparable only under the same score definition |
