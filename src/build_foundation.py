"""Flatten trial data, apply transparent taxonomy, and publish Group 1 tables."""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from common import ROOT, atomic_json_write, nested, read_json, utc_now

AGE_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(year|month|week|day)", re.I)


def age_years(value: str | None) -> float | None:
    if not value:
        return None
    match = AGE_RE.search(value)
    if not match:
        return None
    number, unit = float(match.group(1)), match.group(2).lower()
    return number / {"year": 1, "month": 12, "week": 52.1429, "day": 365.25}[unit]


def text_join(values: list[Any]) -> str:
    return " | ".join(str(x).strip() for x in values if x not in (None, "", []))


def classify(study: dict[str, Any], rules: dict[str, Any], minimum_year: int) -> dict[str, Any]:
    ps = study.get("protocolSection", {})
    ident = ps.get("identificationModule", {})
    conditions = ps.get("conditionsModule", {}).get("conditions", [])
    interventions = ps.get("armsInterventionsModule", {}).get("interventions", [])
    types = sorted({i.get("type") for i in interventions if i.get("type")})
    names = [i.get("name", "") for i in interventions]
    descriptions = [i.get("description", "") for i in interventions]
    eligibility = ps.get("eligibilityModule", {})
    min_age = age_years(eligibility.get("minimumAge"))
    max_age = age_years(eligibility.get("maximumAge"))
    start = nested(ps, "statusModule", "startDateStruct", "date", default="") or ""
    year = int(start[:4]) if start[:4].isdigit() else None
    title_text = text_join([ident.get("briefTitle"), ident.get("officialTitle")]).lower()
    primary_text = text_join([ident.get("briefTitle"), ident.get("officialTitle"), *conditions]).lower()
    intervention_name_text = text_join(names).lower()
    intervention_text = text_join(names + descriptions).lower()

    reasons: list[str] = []
    review: list[str] = []
    if not set(types).intersection({"DRUG", "BIOLOGICAL"}):
        reasons.append("NO_DRUG_OR_BIOLOGICAL")
    if max_age is not None and max_age < 18:
        reasons.append("EXCLUSIVELY_PEDIATRIC")
    if year is None or year < minimum_year:
        reasons.append("OUTSIDE_RECENCY_WINDOW")
    diabetes_primary = any(term in title_text for term in rules["exclude_primary_condition_terms"])
    diabetes_negated = any(term in title_text for term in ["without diabetes", "non-diabetic", "nondiabetic", "without type 2 diabetes"])
    if diabetes_primary and not diabetes_negated:
        reasons.append("DIABETES_PRIMARY_OVERLAP")
    if any(term in title_text for term in rules["exclude_title_terms"]):
        reasons.append("OFF_TARGET_THERAPEUTIC_INTENT")
    has_weight_intent = any(term in title_text for term in rules["therapeutic_intent_terms"])
    has_known_therapy = any(term in intervention_name_text for term in rules["known_obesity_therapy_terms"])
    if not has_weight_intent and not has_known_therapy:
        reasons.append("NO_OBESITY_TREATMENT_INTENT")
    if any(term in title_text for term in rules["exclude_intervention_terms"]):
        reasons.append("NON_PHARMACOLOGICAL_PRIMARY_INTENT")
    locations = nested(ps, "contactsLocationsModule", "locations", default=[]) or []
    if min_age is None:
        review.append("MISSING_OR_UNPARSED_MINIMUM_AGE")
    elif min_age < 18 and not (max_age is not None and max_age < 18):
        review.append("INCLUDES_MINORS_AND_ADULTS")
    if not locations:
        review.append("MISSING_LOCATIONS")
    if "diabetes" in (eligibility.get("eligibilityCriteria") or "").lower() and "DIABETES_PRIMARY_OVERLAP" not in reasons:
        review.append("DIABETES_IN_ELIGIBILITY_ONLY")

    modality = "UNKNOWN"
    if any(t in intervention_text for t in rules["oral_terms"]): modality = "ORAL"
    if any(t in intervention_text for t in rules["injectable_terms"]):
        modality = "MIXED_OR_AMBIGUOUS" if modality == "ORAL" else "INJECTABLE"
    return {
        "included": not reasons,
        "exclusion_reasons": ";".join(reasons),
        "review_flags": ";".join(review),
        "intervention_types": ";".join(types),
        "modality": modality,
        "minimum_age_years": min_age,
        "maximum_age_years": max_age,
        "start_year": year,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)
    tmp.replace(path)


def build(snapshot: Path, config_path: Path, rules_path: Path) -> dict[str, Any]:
    studies = read_json(snapshot)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    out = ROOT / config["paths"]["interim"]
    study_rows, intervention_rows, location_rows, condition_rows, sponsor_rows = [], [], [], [], []
    exclusions: Counter[str] = Counter(); modalities: Counter[str] = Counter()
    for study in studies:
        ps = study.get("protocolSection", {}); ident = ps.get("identificationModule", {})
        nct = ident.get("nctId"); result = classify(study, rules, config["taxonomy"]["minimum_start_year"])
        status = ps.get("statusModule", {}); design = ps.get("designModule", {}); elig = ps.get("eligibilityModule", {})
        lead = nested(ps, "sponsorCollaboratorsModule", "leadSponsor", default={}) or {}
        study_rows.append({
            "nct_id": nct, "brief_title": ident.get("briefTitle"), "official_title": ident.get("officialTitle"),
            "overall_status": status.get("overallStatus"), "start_date": nested(status,"startDateStruct","date"),
            "completion_date": nested(status,"completionDateStruct","date"), "enrollment": nested(design,"enrollmentInfo","count"),
            "enrollment_type": nested(design,"enrollmentInfo","type"), "sex": elig.get("sex"),
            "minimum_age": elig.get("minimumAge"), "maximum_age": elig.get("maximumAge"),
            "lead_sponsor": lead.get("name"), "lead_sponsor_class": lead.get("class"), **result,
        })
        modalities[result["modality"]] += 1
        for reason in filter(None, result["exclusion_reasons"].split(";")): exclusions[reason] += 1
        for condition in ps.get("conditionsModule", {}).get("conditions", []): condition_rows.append({"nct_id":nct,"condition_name":condition})
        for idx, item in enumerate(ps.get("armsInterventionsModule", {}).get("interventions", []),1):
            intervention_rows.append({"nct_id":nct,"intervention_seq":idx,"intervention_type":item.get("type"),"intervention_name":item.get("name"),"description":item.get("description")})
        sponsors = [("LEAD", lead)] + [("COLLABORATOR", x) for x in ps.get("sponsorCollaboratorsModule", {}).get("collaborators", [])]
        for role, item in sponsors:
            if item.get("name"): sponsor_rows.append({"nct_id":nct,"sponsor_role":role,"sponsor_name":item.get("name"),"sponsor_class":item.get("class")})
        for idx, loc in enumerate(nested(ps,"contactsLocationsModule","locations",default=[]) or [],1):
            key = "|".join(str(loc.get(k) or "").strip().lower() for k in ["facility","city","state","zip","country"])
            location_rows.append({"location_id":hashlib.sha1(f"{nct}|{idx}|{key}".encode()).hexdigest()[:20],"facility_key":hashlib.sha1(key.encode()).hexdigest()[:20],"nct_id":nct,"facility_name":loc.get("facility"),"city":loc.get("city"),"state":loc.get("state"),"postal_code":loc.get("zip"),"country_raw":loc.get("country"),"latitude":nested(loc,"geoPoint","lat"),"longitude":nested(loc,"geoPoint","lon")})

    write_csv(out/"studies.csv",study_rows,list(study_rows[0]))
    write_csv(out/"conditions.csv",condition_rows,["nct_id","condition_name"])
    write_csv(out/"interventions.csv",intervention_rows,["nct_id","intervention_seq","intervention_type","intervention_name","description"])
    write_csv(out/"sponsors.csv",sponsor_rows,["nct_id","sponsor_role","sponsor_name","sponsor_class"])
    write_csv(out/"study_locations.csv",location_rows,["location_id","facility_key","nct_id","facility_name","city","state","postal_code","country_raw","latitude","longitude"])
    included_ids={r['nct_id'] for r in study_rows if r['included']}
    summary={"generated_at_utc":utc_now(),"source_snapshot":snapshot.name,"all_studies":len(study_rows),"included_by_rules":len(included_ids),"excluded_by_rules":len(study_rows)-len(included_ids),"included_location_rows":sum(r['nct_id'] in included_ids for r in location_rows),"included_countries":len({r['country_raw'] for r in location_rows if r['nct_id'] in included_ids and r['country_raw']}),"review_required_in_included":sum(bool(r['review_flags']) for r in study_rows if r['included']),"exclusion_reason_counts":dict(exclusions),"modality_counts_all_records":dict(modalities),"warning":"Rule inclusion is preliminary until the manual audit sample is labelled."}
    atomic_json_write(summary, ROOT/config["paths"]["reports"]/"group1_foundation_summary.json")
    return summary


if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--snapshot",type=Path,required=True); p.add_argument("--config",type=Path,default=ROOT/"config/pipeline.yaml"); p.add_argument("--rules",type=Path,default=ROOT/"config/taxonomy_rules.yaml"); a=p.parse_args()
    print(build(a.snapshot,a.config,a.rules))
