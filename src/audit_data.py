"""T0000 data-viability audit for the obesity trial portfolio project."""

from __future__ import annotations

import csv
import json
import statistics
import subprocess
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "data" / "audit"
RAW_DIR = ROOT / "data" / "raw"

CTG_BASE = "https://clinicaltrials.gov/api/v2/studies"
CTG_QUERY = {
    "query.cond": "Obesity",
    "filter.advanced": "AREA[Phase]PHASE3 AND AREA[StudyType]INTERVENTIONAL",
    "pageSize": "100",
    "countTotal": "true",
    "format": "json",
}
NCD_RISC_URL = (
    "https://www.ncdrisc.org/downloads/bmi-2024/adult/"
    "NCD_RisC_Lancet_2024_BMI_age_standardised_country.csv"
)
WORLD_BANK_URL = (
    "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL"
    "?format=json&date=2023&per_page=400"
)
WHO_URL = "https://ghoapi.azureedge.net/api/NCD_BMI_30A?$filter=TimeDim%20eq%202022"


def fetch_bytes(url: str, timeout: int = 180) -> bytes:
    completed = subprocess.run(
        [
            "curl",
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--max-time",
            str(timeout),
            "--user-agent",
            "obesity-portfolio-audit/0.1",
            url,
        ],
        check=True,
        capture_output=True,
    )
    return completed.stdout


def fetch_json(url: str) -> Any:
    return json.loads(fetch_bytes(url))


def get_nested(record: dict[str, Any], path: Iterable[str]) -> Any:
    value: Any = record
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def fetch_trials() -> tuple[list[dict[str, Any]], int]:
    studies: list[dict[str, Any]] = []
    params = dict(CTG_QUERY)
    total_count = 0
    while True:
        url = f"{CTG_BASE}?{urllib.parse.urlencode(params)}"
        payload = fetch_json(url)
        total_count = payload.get("totalCount", total_count)
        studies.extend(payload.get("studies", []))
        token = payload.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token
    return studies, total_count


def profile_trials(studies: list[dict[str, Any]], total_count: int) -> dict[str, Any]:
    field_paths = {
        "nct_id": ("protocolSection", "identificationModule", "nctId"),
        "status": ("protocolSection", "statusModule", "overallStatus"),
        "start_date": ("protocolSection", "statusModule", "startDateStruct", "date"),
        "completion_date": ("protocolSection", "statusModule", "completionDateStruct", "date"),
        "enrollment": ("protocolSection", "designModule", "enrollmentInfo", "count"),
        "sponsor": ("protocolSection", "sponsorCollaboratorsModule", "leadSponsor", "name"),
        "interventions": ("protocolSection", "armsInterventionsModule", "interventions"),
        "eligibility": ("protocolSection", "eligibilityModule", "eligibilityCriteria"),
        "locations": ("protocolSection", "contactsLocationsModule", "locations"),
    }
    completeness = {}
    for name, path in field_paths.items():
        present = sum(get_nested(study, path) not in (None, "", []) for study in studies)
        completeness[name] = {
            "present": present,
            "missing": len(studies) - present,
            "pct_present": round(100 * present / len(studies), 2) if studies else 0,
        }

    countries: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    sponsors: Counter[str] = Counter()
    enrollments: list[int] = []
    multi_country = 0
    for study in studies:
        statuses[get_nested(study, field_paths["status"]) or "MISSING"] += 1
        sponsors[get_nested(study, field_paths["sponsor"]) or "MISSING"] += 1
        enrollment = get_nested(study, field_paths["enrollment"])
        if isinstance(enrollment, int):
            enrollments.append(enrollment)
        locations = get_nested(study, field_paths["locations"]) or []
        study_countries = {loc.get("country") for loc in locations if loc.get("country")}
        countries.update(study_countries)
        multi_country += len(study_countries) > 1

    return {
        "query_total_count": total_count,
        "records_downloaded": len(studies),
        "field_completeness": completeness,
        "unique_location_countries": len(countries),
        "trials_with_multiple_countries": multi_country,
        "top_location_countries": countries.most_common(25),
        "status_counts": statuses.most_common(),
        "unique_sponsors": len(sponsors),
        "top_sponsors": sponsors.most_common(15),
        "enrollment_median": statistics.median(enrollments) if enrollments else None,
        "enrollment_min": min(enrollments) if enrollments else None,
        "enrollment_max": max(enrollments) if enrollments else None,
        "relevance_funnel": profile_relevance_funnel(studies),
    }


def profile_relevance_funnel(studies: list[dict[str, Any]]) -> dict[str, Any]:
    """Quantify a reproducible adult drug-trial cohort without claiming final taxonomy."""
    drug_trials: list[dict[str, Any]] = []
    adult_drug_trials: list[dict[str, Any]] = []
    non_diabetes_adult_drug_trials: list[dict[str, Any]] = []
    recent_core_trials: list[dict[str, Any]] = []

    for study in studies:
        protocol = study.get("protocolSection", {})
        interventions = (
            protocol.get("armsInterventionsModule", {}).get("interventions", [])
        )
        if not any(item.get("type") in {"DRUG", "BIOLOGICAL"} for item in interventions):
            continue
        drug_trials.append(study)

        eligibility = protocol.get("eligibilityModule", {})
        minimum_age = eligibility.get("minimumAge", "")
        maximum_age = eligibility.get("maximumAge", "")
        combined_age = f"{minimum_age} {maximum_age}".lower()
        exclusively_pediatric = (
            "year" in maximum_age.lower()
            and maximum_age.split()[0].isdigit()
            and int(maximum_age.split()[0]) < 18
        )
        if exclusively_pediatric or "child" in combined_age and "adult" not in combined_age:
            continue
        adult_drug_trials.append(study)

        identification = protocol.get("identificationModule", {})
        conditions = protocol.get("conditionsModule", {}).get("conditions", [])
        searchable = " ".join(
            [
                identification.get("briefTitle", ""),
                identification.get("officialTitle", ""),
                *conditions,
            ]
        ).lower()
        if "diabetes" in searchable or "diabetic" in searchable:
            continue
        non_diabetes_adult_drug_trials.append(study)

        start_date = (
            protocol.get("statusModule", {}).get("startDateStruct", {}).get("date", "")
        )
        if start_date[:4].isdigit() and int(start_date[:4]) >= 2010:
            recent_core_trials.append(study)

    countries = set()
    location_records = 0
    for study in recent_core_trials:
        locations = (
            study.get("protocolSection", {})
            .get("contactsLocationsModule", {})
            .get("locations", [])
        )
        location_records += len(locations)
        countries.update(loc.get("country") for loc in locations if loc.get("country"))

    return {
        "all_phase3_obesity_interventional": len(studies),
        "drug_or_biological": len(drug_trials),
        "not_exclusively_pediatric": len(adult_drug_trials),
        "title_condition_not_diabetes": len(non_diabetes_adult_drug_trials),
        "core_started_2010_or_later": len(recent_core_trials),
        "core_location_records": location_records,
        "core_unique_countries": len(countries),
        "note": (
            "This is a conservative audit funnel, not the final clinical taxonomy. "
            "Eligibility-text validation is required before analysis."
        ),
    }


def audit_external_sources() -> dict[str, Any]:
    ncd_bytes = fetch_bytes(NCD_RISC_URL)
    ncd_rows = list(csv.DictReader(ncd_bytes.decode("utf-8-sig").splitlines()))
    wb_payload = fetch_json(WORLD_BANK_URL)
    wb_rows = wb_payload[1]
    who_payload = fetch_json(WHO_URL)
    who_rows = who_payload.get("value", [])

    (RAW_DIR / "ncd_risc_obesity_country.csv").write_bytes(ncd_bytes)
    (RAW_DIR / "world_bank_population_2023.json").write_text(
        json.dumps(wb_payload, indent=2), encoding="utf-8"
    )
    (RAW_DIR / "who_obesity_2022.json").write_text(
        json.dumps(who_payload, indent=2), encoding="utf-8"
    )

    return {
        "ncd_risc": {
            "rows": len(ncd_rows),
            "columns": list(ncd_rows[0]) if ncd_rows else [],
        },
        "world_bank_population": {
            "rows": len(wb_rows),
            "non_null_values": sum(row.get("value") is not None for row in wb_rows),
        },
        "who_obesity": {
            "rows": len(who_rows),
            "countries": len({row.get("SpatialDim") for row in who_rows if row.get("SpatialDim")}),
            "sex_categories": sorted({row.get("Dim1") for row in who_rows if row.get("Dim1")}),
        },
    }


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    studies, total_count = fetch_trials()
    (RAW_DIR / "clinical_trials_phase3_obesity.json").write_text(
        json.dumps(studies, indent=2), encoding="utf-8"
    )
    trial_profile = profile_trials(studies, total_count)
    external_profile = audit_external_sources()
    report = {
        "clinicaltrials_gov": trial_profile,
        "external_sources": external_profile,
    }
    (AUDIT_DIR / "data_viability_summary.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    (AUDIT_DIR / "clinical_trials_sample.json").write_text(
        json.dumps(studies[:10], indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
