USE obesity_trial_portfolio;

CREATE OR REPLACE VIEW vw_country_trial_footprint AS
SELECT
    l.iso3,
    COUNT(DISTINCT l.nct_id) AS relevant_studies,
    COUNT(DISTINCT l.facility_key) AS unique_facilities,
    COUNT(DISTINCT CASE WHEN s.overall_status IN
        ('RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING','ENROLLING_BY_INVITATION')
        THEN l.nct_id END) AS active_trials,
    COUNT(DISTINCT sp.sponsor_name) AS lead_sponsors
FROM study_locations l
JOIN studies s ON s.nct_id = l.nct_id AND s.final_included = 1
LEFT JOIN study_sponsors sp ON sp.nct_id = s.nct_id AND sp.sponsor_role = 'LEAD'
WHERE l.iso3 IS NOT NULL
GROUP BY l.iso3;

CREATE OR REPLACE VIEW vw_repeat_facilities AS
WITH facility_experience AS (
    SELECT l.iso3, l.facility_key, COUNT(DISTINCT l.nct_id) AS study_count
    FROM study_locations l
    JOIN studies s ON s.nct_id = l.nct_id AND s.final_included = 1
    WHERE l.iso3 IS NOT NULL
    GROUP BY l.iso3, l.facility_key
)
SELECT iso3,
       COUNT(*) AS unique_facilities,
       SUM(study_count >= 2) AS repeat_facilities
FROM facility_experience
GROUP BY iso3;

CREATE OR REPLACE VIEW vw_portfolio_scenario_comparison AS
SELECT
    sp.country_name,
    MAX(sp.scenario = 'balanced') AS balanced,
    MAX(sp.scenario = 'patient_reach') AS patient_reach,
    MAX(sp.scenario = 'execution_readiness') AS execution_readiness,
    MAX(sp.scenario = 'competition_averse') AS competition_averse,
    csf.selection_frequency_pct
FROM scenario_portfolios sp
LEFT JOIN country_selection_frequency csf ON csf.iso3 = sp.iso3
GROUP BY sp.iso3, sp.country_name, csf.selection_frequency_pct;
