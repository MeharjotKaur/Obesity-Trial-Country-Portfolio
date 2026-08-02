USE obesity_trial_portfolio;

-- Country footprint with rank; validates the Python aggregation logic.
SELECT iso3, relevant_studies, unique_facilities, active_trials, lead_sponsors,
       DENSE_RANK() OVER (ORDER BY relevant_studies DESC) AS study_rank
FROM vw_country_trial_footprint
ORDER BY study_rank, iso3;

-- Facilities with repeat experience.
WITH facility_experience AS (
    SELECT l.iso3, l.facility_key, MAX(l.facility_name) AS facility_name,
           COUNT(DISTINCT l.nct_id) AS relevant_studies
    FROM study_locations l
    JOIN studies s ON s.nct_id = l.nct_id AND s.final_included = 1
    WHERE l.iso3 IS NOT NULL
    GROUP BY l.iso3, l.facility_key
)
SELECT iso3, facility_name, relevant_studies,
       ROW_NUMBER() OVER (PARTITION BY iso3 ORDER BY relevant_studies DESC, facility_name) AS country_facility_rank
FROM facility_experience
WHERE relevant_studies >= 2
ORDER BY iso3, country_facility_rank;

-- Scenario membership and Monte Carlo stability.
SELECT country_name, balanced, patient_reach, execution_readiness,
       competition_averse, selection_frequency_pct
FROM vw_portfolio_scenario_comparison
ORDER BY selection_frequency_pct DESC, country_name;

-- Stable core under the pre-specified 80% threshold.
SELECT country_name, region, selection_frequency_pct
FROM country_selection_frequency
WHERE selection_frequency_pct >= 80
ORDER BY selection_frequency_pct DESC, country_name;
