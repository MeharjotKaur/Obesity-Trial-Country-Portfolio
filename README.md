# Global Phase III Obesity Trial Country-Portfolio Optimisation

Decision-analytics project for selecting a robust five-country portfolio for a hypothetical Phase III oral obesity trial in adults without diabetes.

## Executive result

The production extract contains 717 unique Phase III interventional obesity records from a dated ClinicalTrials.gov snapshot. A conservative, inspectable taxonomy freezes 117 general-adult obesity-pharmacotherapy studies; 45 countries clear the evidence gates and receive four-pillar scores. PuLP/CBC optimisation recommends a balanced screening portfolio of the United States, China, India, Brazil and Mexico. Across 2,000 reproducible assumption-sensitivity runs, the first four were selected in 100% and Mexico in 86.05%.

This is a healthcare strategy analytics and prescriptive-optimisation project. It does not predict trial success, recruitment speed or country-level costs.

## Final build status

The reproducible Python pipeline, relational MySQL 8 layer, SQL checks and views, scoring model, binary optimisation, robustness analysis, saved outputs, automated tests, documentation and seven-slide executive deck are complete. A Power BI dashboard was considered during planning but is explicitly outside the final MVP; the executive deck is the visual decision deliverable. The remaining work for the project owner is understanding and interview practice, not software development.

## Data sources

- ClinicalTrials.gov API v2: trials, sponsors, interventions, enrollment, dates, and locations
- WHO Global Health Observatory: adult obesity prevalence
- NCD Risk Factor Collaboration: considered for uncertainty intervals, but excluded from production because the saved extract failed completeness checks
- World Bank Indicators API: population and health-system indicators

## Guardrails

- This is a preliminary country-screening tool, not a final operational site plan.
- Trial enrollment is study-level, not country-level.
- Public data do not provide true site recruitment rates or country trial costs.
- Scores and optimisation results must expose assumptions and uncertainty.

## Analytical architecture

1. Extract a broad Phase III obesity universe from the ClinicalTrials.gov API.
2. Parse study, sponsor, intervention and location records into relational tables.
3. Apply a documented therapeutic-intent taxonomy and freeze the eligible cohort.
4. Engineer country proxies for patient opportunity, historical infrastructure, competitive headroom and data confidence.
5. Screen countries, normalise features and calculate transparent multi-criteria scores.
6. Select five countries with a binary integer programme under portfolio guardrails.
7. Test alternative priorities and 2,000 Monte Carlo assumption draws.

## Quick start

Use Python 3.12 from the repository root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py --use-snapshot
```

`--use-snapshot` reproduces the published result from the dated source snapshot. Omit it to request a fresh API extract, whose counts may change over time.

## MySQL 8 validation

Do not import the CSV files manually in MySQL Workbench and do not execute the four SQL files one by one. The project loader handles table order, UTF-8 text, missing values and foreign keys.

With MySQL Server 8 running, execute this once from the repository root:

```bash
python src/validate_mysql.py
```

Enter the local MySQL password when prompted (typing is hidden). The command recreates and loads all 10 tables, reconciles every database row count against its source CSV, executes the quality checks, creates the analytical views and writes `outputs/reports/mysql_validation.txt`. It must end with `STATUS: PASS`. MySQL 8 is required because the schema uses `utf8mb4_0900_ai_ci`, CTEs and window functions.

Using `.env` is optional. If preferred, copy `.env.example` to `.env`, replace `replace_locally` with local credentials, and never commit that file.

## Repository map

- `config/`: taxonomy, scoring and optimisation assumptions.
- `data/`: dated raw snapshot, relational interim tables and processed decision table.
- `src/`: extraction, transformation, scoring, optimisation, simulation and database scripts.
- `sql/`: schema, checks, views and analytical queries.
- `outputs/`: verified result tables, figures and machine-readable summaries.
- `docs/`: methodology, sources, assumptions, interview defence and reproduction guide.
- `presentation/`: executive recommendation deck.

## Claim boundary

The recommendation is a preliminary country-screening shortlist for a hypothetical programme, not a final activation plan. Public registered-trial locations are proxies for historical infrastructure; total study enrollment is not allocated to countries. Regulatory timelines, costs, current investigator capacity, sponsor policy and geopolitical feasibility require separate diligence.
