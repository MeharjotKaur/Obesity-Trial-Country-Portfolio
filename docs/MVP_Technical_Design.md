# MVP Technical Design

## Pipeline

1. Extract versioned source snapshots.
2. Validate schemas and required fields.
3. Transform nested trial records into relational tables.
4. Normalise countries, sponsors, interventions, and study populations.
5. Load MySQL staging and analytical tables.
6. Produce country-level features with SQL views.
7. Calculate transparent pillar scores in Python.
8. Run five-country binary optimisation in PuLP.
9. Run Monte Carlo robustness analysis.
10. Publish decision views to Power BI and an executive deck.

## Proposed MySQL tables

| Table | Grain | Key |
|---|---|---|
| `studies` | One row per trial | `nct_id` |
| `study_conditions` | One condition per trial | `nct_id`, `condition_name` |
| `interventions` | One intervention per trial | surrogate ID |
| `sponsors` | One lead/collaborating sponsor per trial | surrogate ID |
| `facilities` | One normalised facility | `facility_id` |
| `study_locations` | One trial-facility record | surrogate ID |
| `countries` | One country | `iso3` |
| `country_obesity` | Country-year-sex estimate | composite key |
| `country_indicators` | Country-year-indicator value | composite key |
| `country_features` | One country per model version | composite key |
| `scenario_parameters` | One parameter per scenario | composite key |
| `portfolio_results` | One country per optimisation run | composite key |

## Analytical pillars

1. Patient opportunity
2. Relevant trial saturation
3. Experienced-site availability
4. Basic healthcare/research readiness
5. Geographic diversification
6. Data confidence

## Optimisation

Binary decision variable `x[country]` equals 1 when a country is selected.

Base objective: maximise portfolio utility across country opportunity and execution-readiness measures while penalising competition and low-confidence data.

Required constraints:

- exactly five countries
- minimum combined patient opportunity
- minimum experienced-site threshold
- at least two geographic regions
- maximum number of low-confidence countries

Every constraint must have a business explanation and a sensitivity test.

## Validation

- Source and schema tests
- Primary-key and relationship tests
- Missingness thresholds
- Manual clinical-taxonomy audit
- Score direction and monotonicity tests
- Optimisation feasibility tests
- Alternative-weight scenarios
- Monte Carlo selection frequency
- Leave-one-pillar-out analysis
