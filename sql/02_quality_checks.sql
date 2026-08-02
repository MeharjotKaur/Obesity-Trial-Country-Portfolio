USE obesity_trial_portfolio;

SELECT 'duplicate_nct_id' AS check_name, COUNT(*) AS failures
FROM (SELECT nct_id FROM studies GROUP BY nct_id HAVING COUNT(*) > 1) d
UNION ALL
SELECT 'orphan_locations', COUNT(*)
FROM study_locations l LEFT JOIN studies s ON l.nct_id=s.nct_id WHERE s.nct_id IS NULL
UNION ALL
SELECT 'unmapped_location_countries', COUNT(*)
FROM study_locations
WHERE country_raw IS NOT NULL
  AND iso3 IS NULL
  AND NOT (
      nct_id = 'NCT01272219'
      AND country_raw = 'Serbia and Montenegro'
  )
UNION ALL
SELECT 'invalid_prevalence', COUNT(*)
FROM country_obesity WHERE obesity_prevalence_pct < 0 OR obesity_prevalence_pct > 100
UNION ALL
SELECT 'scenario_not_five_countries', COUNT(*)
FROM (SELECT scenario FROM scenario_portfolios GROUP BY scenario HAVING COUNT(*) <> 5) p
UNION ALL
SELECT 'invalid_selection_frequency', COUNT(*)
FROM country_selection_frequency WHERE selection_frequency_pct < 0 OR selection_frequency_pct > 100;
