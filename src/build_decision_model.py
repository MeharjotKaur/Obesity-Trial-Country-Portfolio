"""Build the Group 2 country evidence table and transparent MCDA score."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from common import ROOT, atomic_json_write, utc_now

OFF_TARGET_TITLE_TERMS = (
    "hiv", "cystic fibrosis", "anaesthesia", "anesthesia", "kidney transplant",
    "endometrial", "psoriasis", "psoriatic", "polycystic", "bariatric surgery",
    "sleeve gastrectomy", "gastric bypass", "arrhythmia", "albuminuria",
    "brown adipose", "laser treatment", "neurostimulation", "microbiome changes",
)
PEDIATRIC_OR_RARE_TERMS = (
    "children", "adolescent", "pediatric", "paediatric", "prader-willi",
    "bardet-biedl", "alström", "alstrom", "gene mutation", "gene variant",
    "hypothalamic obesity", "craniopharyngioma",
)
WEIGHT_INTENT_TERMS = (
    "weight loss", "weight reduction", "weight management", "maintain weight",
    "maintenance of weight", "treatment of obesity", "obesity treatment",
    "overweight or obesity", "overweight and obesity", "overweight or obese",
    "obesity or overweight", "living with obesity", "excess body weight",
    "body weight above", "above a healthy weight", "adults with obesity",
    "participants with obesity", "subjects with obesity", "individuals with obesity",
)


def minmax(series: pd.Series, inverse: bool = False) -> pd.Series:
    x = pd.to_numeric(series, errors="coerce").astype(float)
    lo, hi = x.min(), x.max()
    out = pd.Series(0.5, index=x.index) if hi == lo else (x - lo) / (hi - lo)
    return 1 - out if inverse else out


def log_minmax(series: pd.Series, inverse: bool = False) -> pd.Series:
    return minmax(np.log1p(pd.to_numeric(series, errors="coerce").clip(lower=0)), inverse)


def final_cohort(studies: pd.DataFrame) -> pd.DataFrame:
    """Conservative adult, general-obesity pharmacotherapy cohort.

    Group 1 rules are the first gate. This second gate removes studies whose
    therapeutic intent is another disease and rare/pediatric obesity programmes.
    """
    s = studies.copy()
    title = (s.brief_title.fillna("") + " " + s.official_title.fillna("")).str.lower()
    s["g2_off_target"] = title.apply(lambda x: any(t in x for t in OFF_TARGET_TITLE_TERMS))
    s["g2_special_population"] = title.apply(lambda x: any(t in x for t in PEDIATRIC_OR_RARE_TERMS))
    s["g2_weight_intent"] = title.apply(lambda x: any(t in x for t in WEIGHT_INTENT_TERMS))
    s["final_included"] = s.included.astype(bool) & s.g2_weight_intent & ~s.g2_off_target & ~s.g2_special_population
    s["g2_decision_reason"] = np.select(
        [~s.included.astype(bool), s.g2_off_target, s.g2_special_population, ~s.g2_weight_intent],
        ["GROUP1_EXCLUDED", "OFF_TARGET_PRIMARY_INTENT", "SPECIAL_OR_PEDIATRIC_POPULATION", "INSUFFICIENT_GENERAL_WEIGHT_INTENT"],
        default="INCLUDED_GENERAL_ADULT_PHARMACOTHERAPY",
    )
    return s


def build(root: Path = ROOT) -> dict:
    cfg = yaml.safe_load((root / "config/scoring.yaml").read_text())
    interim, processed, reports = root / "data/interim", root / "data/processed", root / "outputs/reports"
    processed.mkdir(parents=True, exist_ok=True); reports.mkdir(parents=True, exist_ok=True)

    studies = final_cohort(pd.read_csv(interim / "studies.csv"))
    locations = pd.read_csv(interim / "study_locations_harmonised.csv")
    sponsors = pd.read_csv(interim / "sponsors.csv")
    countries = pd.read_csv(interim / "countries.csv")
    obesity = pd.read_csv(interim / "country_obesity_who.csv")
    obesity = obesity[obesity.sex_code.eq("SEX_BTSX")][["iso3", "year", "obesity_prevalence_pct"]].drop_duplicates("iso3")

    studies.to_csv(processed / "trial_taxonomy_final.csv", index=False)
    included = studies[studies.final_included].copy()
    included_ids = set(included.nct_id)
    loc = locations[locations.nct_id.isin(included_ids) & locations.iso3.notna()].copy()
    lead = sponsors[(sponsors.nct_id.isin(included_ids)) & sponsors.sponsor_role.eq("LEAD")].copy()
    status_map = included.set_index("nct_id").overall_status
    year_map = included.set_index("nct_id").start_year
    loc["overall_status"] = loc.nct_id.map(status_map)
    loc["start_year"] = loc.nct_id.map(year_map)
    loc["is_active"] = loc.overall_status.isin(cfg["active_statuses"])
    loc["is_recent"] = loc.start_year.ge(cfg["recent_start_year"])

    # A facility is repeat-experienced only when its harmonised key appears in >=2 included studies.
    facility_studies = loc.groupby(["iso3", "facility_key"], dropna=False).nct_id.nunique().rename("facility_study_count").reset_index()
    repeat = facility_studies.assign(repeat=lambda x: x.facility_study_count.ge(2)).groupby("iso3").agg(
        unique_facilities=("facility_key", "nunique"), repeat_facilities=("repeat", "sum")
    )
    base = loc.groupby("iso3").agg(
        relevant_studies=("nct_id", "nunique"),
        active_trials=("nct_id", lambda x: x[loc.loc[x.index, "is_active"]].nunique()),
        recent_trials=("nct_id", lambda x: x[loc.loc[x.index, "is_recent"]].nunique()),
        location_rows=("location_id", "count"),
        geocoded_rows=("latitude", "count"),
    ).join(repeat)
    sponsor_country = loc[["iso3", "nct_id"]].drop_duplicates().merge(lead[["nct_id", "sponsor_name"]], on="nct_id", how="left")
    sponsor_metrics = sponsor_country.groupby("iso3").agg(
        sponsor_diversity=("sponsor_name", "nunique"),
        active_sponsor_count=("sponsor_name", lambda x: x[sponsor_country.loc[x.index, "nct_id"].map(status_map).isin(cfg["active_statuses"])].nunique()),
    )
    base = base.join(sponsor_metrics).reset_index()
    base = base.merge(countries, on="iso3", how="left").merge(obesity, on="iso3", how="left")
    base["obese_population_proxy"] = base.population_2023 * base.obesity_prevalence_pct / 100
    base["active_trials_per_10m_proxy"] = base.active_trials / (base.obese_population_proxy / 10_000_000)
    base["location_completeness"] = base.geocoded_rows / base.location_rows
    base["indicator_recency"] = 1 / (1 + (2026 - base.year).clip(lower=0))
    base["evidence_depth"] = np.log1p(base.relevant_studies) / np.log1p(base.relevant_studies.max())

    gate = cfg["candidate_screen"]
    base["screen_pass"] = (
        base.relevant_studies.ge(gate["minimum_relevant_studies"])
        & base.unique_facilities.ge(gate["minimum_unique_facilities"])
        & base.population_2023.notna() & base.obesity_prevalence_pct.notna()
    )
    base["screen_exclusion_reason"] = np.select(
        [base.population_2023.isna(), base.obesity_prevalence_pct.isna(), base.relevant_studies.lt(gate["minimum_relevant_studies"]), base.unique_facilities.lt(gate["minimum_unique_facilities"])],
        ["MISSING_POPULATION", "MISSING_OBESITY_PREVALENCE", "INSUFFICIENT_STUDY_EVIDENCE", "INSUFFICIENT_FACILITY_EVIDENCE"], default="PASSED"
    )

    cand = base[base.screen_pass].copy().reset_index(drop=True)
    cand["opportunity_score"] = 100 * log_minmax(cand.obese_population_proxy)
    cand["infrastructure_score"] = 100 * (
        .45 * log_minmax(cand.unique_facilities) + .25 * log_minmax(cand.repeat_facilities)
        + .20 * log_minmax(cand.relevant_studies) + .10 * log_minmax(cand.sponsor_diversity)
    )
    cand["competitive_headroom_score"] = 100 * (
        .65 * log_minmax(cand.active_trials_per_10m_proxy, inverse=True)
        + .35 * log_minmax(cand.active_sponsor_count, inverse=True)
    )
    cand["data_confidence_score"] = 100 * (
        .45 * cand.location_completeness + .35 * cand.evidence_depth + .20 * cand.indicator_recency
    )
    w = cfg["weights"]
    cand["attractiveness_score"] = sum(cand[f"{k}_score"] * v for k, v in w.items())
    cand["rank"] = cand.attractiveness_score.rank(method="min", ascending=False).astype(int)
    cand = cand.sort_values(["rank", "country_name"])

    base.to_csv(processed / "country_screening_funnel.csv", index=False)
    cand.to_csv(processed / "country_features_scored.csv", index=False)
    summary = {
        "generated_at_utc": utc_now(), "group1_rule_included": int(studies.included.sum()),
        "final_cohort_studies": int(included.shape[0]), "final_cohort_countries": int(loc.iso3.nunique()),
        "candidate_countries": int(cand.shape[0]), "candidate_regions": int(cand.region.nunique()),
        "top_five_by_score": cand.head(5).country_name.tolist(),
        "screen_exclusion_counts": base.screen_exclusion_reason.value_counts().to_dict(),
        "guardrail": "Obese population is total-population x adult-obesity-prevalence proxy; it is not an eligible-patient estimate.",
    }
    atomic_json_write(summary, reports / "group2_decision_model_summary.json")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=ROOT)
    print(json.dumps(build(parser.parse_args().root), indent=2))
