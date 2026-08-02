"""Harmonise ClinicalTrials.gov country names to ISO3 and publish indicator tables."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import yaml

from common import ROOT, atomic_json_write, utc_now


def normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    tmp.replace(path)


def main() -> None:
    aliases = yaml.safe_load((ROOT/"config/country_aliases.yaml").read_text(encoding="utf-8"))
    wb_payload = json.load((ROOT/"data/raw/world_bank_population_2023.json").open())
    wb_rows = wb_payload[1]
    wb_reference = json.load((ROOT/"data/raw/world_bank_country_reference.json").open())[1]
    metadata = {r["id"]: r for r in wb_reference if r.get("region", {}).get("id") != "NA"}
    countries = {}
    name_lookup = {}
    for row in wb_rows:
        iso3 = row.get("countryiso3code")
        if len(iso3 or "") != 3 or iso3 not in metadata:
            continue
        record = {"iso3":iso3,"country_name":metadata[iso3]["name"],"region":metadata[iso3]["region"]["value"].strip(),"population_2023":row.get("value")}
        countries[iso3] = record; name_lookup[normalise(record["country_name"])] = iso3

    # WHO uses ISO3 SpatialDim and contains three sex categories per country.
    who = json.load((ROOT/"data/raw/who_obesity_2022.json").open())["value"]
    who_rows = []
    for row in who:
        if row.get("SpatialDim") not in countries:
            continue  # Exclude WHO regions/income groups and entities lacking population data.
        who_rows.append({"iso3":row.get("SpatialDim"),"year":row.get("TimeDim"),"sex_code":row.get("Dim1"),"obesity_prevalence_pct":row.get("NumericValue"),"display_value":row.get("Value")})
    write_csv(ROOT/"data/interim/country_obesity_who.csv",who_rows,["iso3","year","sex_code","obesity_prevalence_pct","display_value"])

    locations = list(csv.DictReader((ROOT/"data/interim/study_locations.csv").open(encoding="utf-8")))
    unresolved = Counter(); mapped = 0
    for row in locations:
        raw = row["country_raw"]
        iso3 = aliases["aliases"].get(raw) or name_lookup.get(normalise(raw))
        row["iso3"] = iso3 or ""
        if iso3: mapped += 1
        elif raw: unresolved[raw] += 1
    write_csv(ROOT/"data/interim/study_locations_harmonised.csv",locations,list(locations[0]))
    write_csv(ROOT/"data/interim/countries.csv",sorted(countries.values(),key=lambda x:x["iso3"]),["iso3","country_name","region","population_2023"])
    summary={"generated_at_utc":utc_now(),"location_rows":len(locations),"mapped_location_rows":mapped,"mapping_rate_pct":round(100*mapped/len(locations),2),"unresolved_location_rows":sum(unresolved.values()),"unresolved_countries":dict(unresolved),"world_bank_countries":len(countries),"who_rows":len(who_rows),"who_country_codes":len({r['iso3'] for r in who_rows if r['iso3']})}
    atomic_json_write(summary,ROOT/"outputs/reports/country_harmonisation_summary.json")
    print(summary)


if __name__ == "__main__": main()
