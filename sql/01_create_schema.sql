CREATE DATABASE IF NOT EXISTS obesity_trial_portfolio
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE obesity_trial_portfolio;

CREATE TABLE IF NOT EXISTS studies (
  nct_id VARCHAR(11) PRIMARY KEY,
  brief_title TEXT NOT NULL,
  official_title TEXT,
  overall_status VARCHAR(40) NOT NULL,
  start_date VARCHAR(10),
  completion_date VARCHAR(10),
  enrollment INT,
  enrollment_type VARCHAR(20),
  sex VARCHAR(20),
  minimum_age VARCHAR(30),
  maximum_age VARCHAR(30),
  lead_sponsor VARCHAR(500),
  lead_sponsor_class VARCHAR(40),
  included BOOLEAN NOT NULL,
  exclusion_reasons VARCHAR(500),
  review_flags VARCHAR(500),
  intervention_types VARCHAR(100),
  modality VARCHAR(30),
  minimum_age_years DECIMAL(8,3),
  maximum_age_years DECIMAL(8,3),
  start_year SMALLINT,
  g2_off_target BOOLEAN NOT NULL DEFAULT 0,
  g2_special_population BOOLEAN NOT NULL DEFAULT 0,
  g2_weight_intent BOOLEAN NOT NULL DEFAULT 0,
  final_included BOOLEAN NOT NULL DEFAULT 0,
  g2_decision_reason VARCHAR(100),
  INDEX idx_studies_included_status (included, overall_status),
  INDEX idx_studies_final_status (final_included, overall_status),
  INDEX idx_studies_start_year (start_year)
);

CREATE TABLE IF NOT EXISTS countries (
  iso3 CHAR(3) PRIMARY KEY,
  country_name VARCHAR(150) NOT NULL,
  region VARCHAR(150),
  population_2023 BIGINT
);

CREATE TABLE IF NOT EXISTS study_locations (
  location_id CHAR(20) PRIMARY KEY,
  facility_key CHAR(20) NOT NULL,
  nct_id VARCHAR(11) NOT NULL,
  facility_name VARCHAR(500),
  city VARCHAR(200),
  state VARCHAR(200),
  postal_code VARCHAR(40),
  country_raw VARCHAR(150),
  iso3 CHAR(3),
  latitude DECIMAL(10,7),
  longitude DECIMAL(10,7),
  CONSTRAINT fk_location_study FOREIGN KEY (nct_id) REFERENCES studies(nct_id),
  CONSTRAINT fk_location_country FOREIGN KEY (iso3) REFERENCES countries(iso3),
  INDEX idx_locations_nct (nct_id),
  INDEX idx_locations_country (iso3),
  INDEX idx_locations_facility (facility_key)
);

CREATE TABLE IF NOT EXISTS interventions (
  nct_id VARCHAR(11) NOT NULL,
  intervention_seq SMALLINT NOT NULL,
  intervention_type VARCHAR(40),
  intervention_name VARCHAR(500),
  description TEXT,
  PRIMARY KEY (nct_id, intervention_seq),
  CONSTRAINT fk_intervention_study FOREIGN KEY (nct_id) REFERENCES studies(nct_id)
);

CREATE TABLE IF NOT EXISTS study_conditions (
  nct_id VARCHAR(11) NOT NULL,
  condition_name VARCHAR(500) NOT NULL,
  PRIMARY KEY (nct_id, condition_name),
  CONSTRAINT fk_condition_study FOREIGN KEY (nct_id) REFERENCES studies(nct_id)
);

CREATE TABLE IF NOT EXISTS study_sponsors (
  sponsor_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  nct_id VARCHAR(11) NOT NULL,
  sponsor_role VARCHAR(20) NOT NULL,
  sponsor_name VARCHAR(500) NOT NULL,
  sponsor_class VARCHAR(40),
  CONSTRAINT fk_sponsor_study FOREIGN KEY (nct_id) REFERENCES studies(nct_id),
  INDEX idx_sponsor_nct (nct_id),
  INDEX idx_sponsor_name (sponsor_name(100))
);

CREATE TABLE IF NOT EXISTS country_obesity (
  iso3 CHAR(3) NOT NULL,
  year SMALLINT NOT NULL,
  sex_code VARCHAR(20) NOT NULL,
  obesity_prevalence_pct DECIMAL(10,5),
  display_value VARCHAR(100),
  PRIMARY KEY (iso3, year, sex_code),
  CONSTRAINT fk_obesity_country FOREIGN KEY (iso3) REFERENCES countries(iso3)
);

CREATE TABLE IF NOT EXISTS country_features (
  iso3 CHAR(3) PRIMARY KEY,
  relevant_studies INT NOT NULL,
  active_trials INT NOT NULL,
  recent_trials INT NOT NULL,
  location_rows INT NOT NULL,
  geocoded_rows INT NOT NULL,
  unique_facilities INT NOT NULL,
  repeat_facilities INT NOT NULL,
  sponsor_diversity INT NOT NULL,
  active_sponsor_count INT NOT NULL,
  country_name VARCHAR(150) NOT NULL,
  region VARCHAR(150),
  population_2023 BIGINT,
  year SMALLINT,
  obesity_prevalence_pct DECIMAL(10,5),
  obese_population_proxy DECIMAL(24,4),
  active_trials_per_10m_proxy DECIMAL(16,6),
  location_completeness DECIMAL(10,8),
  indicator_recency DECIMAL(10,8),
  evidence_depth DECIMAL(10,8),
  screen_pass BOOLEAN NOT NULL,
  screen_exclusion_reason VARCHAR(100),
  opportunity_score DECIMAL(10,6),
  infrastructure_score DECIMAL(10,6),
  competitive_headroom_score DECIMAL(10,6),
  data_confidence_score DECIMAL(10,6),
  attractiveness_score DECIMAL(10,6),
  `rank` INT,
  CONSTRAINT fk_feature_country FOREIGN KEY (iso3) REFERENCES countries(iso3),
  INDEX idx_feature_rank (`rank`)
);

CREATE TABLE IF NOT EXISTS scenario_portfolios (
  scenario VARCHAR(50) NOT NULL,
  iso3 CHAR(3) NOT NULL,
  country_name VARCHAR(150) NOT NULL,
  region VARCHAR(150) NOT NULL,
  model_score DECIMAL(10,6) NOT NULL,
  PRIMARY KEY (scenario, iso3),
  CONSTRAINT fk_scenario_country FOREIGN KEY (iso3) REFERENCES countries(iso3)
);

CREATE TABLE IF NOT EXISTS country_selection_frequency (
  iso3 CHAR(3) PRIMARY KEY,
  country_name VARCHAR(150) NOT NULL,
  region VARCHAR(150) NOT NULL,
  selection_count INT NOT NULL,
  selection_frequency_pct DECIMAL(10,6) NOT NULL,
  CONSTRAINT fk_frequency_country FOREIGN KEY (iso3) REFERENCES countries(iso3)
);
