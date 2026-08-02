"""Create the MySQL schema and bulk-load the validated Group 1 CSV tables."""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import pymysql

from common import ROOT

TABLE_FILES = [
    ("studies", "data/processed/trial_taxonomy_final.csv"),
    ("countries", "data/interim/countries.csv"),
    ("study_locations", "data/interim/study_locations_harmonised.csv"),
    ("interventions", "data/interim/interventions.csv"),
    ("study_conditions", "data/interim/conditions.csv"),
    ("study_sponsors", "data/interim/sponsors.csv"),
    ("country_obesity", "data/interim/country_obesity_who.csv"),
    ("country_features", "data/processed/country_features_scored.csv"),
    ("scenario_portfolios", "outputs/tables/scenario_portfolios.csv"),
    ("country_selection_frequency", "outputs/tables/country_selection_frequency.csv"),
]

EXPECTED_MINIMUM_ROWS = {
    "studies": 1,
    "countries": 1,
    "study_locations": 1,
    "interventions": 1,
    "study_conditions": 1,
    "study_sponsors": 1,
    "country_obesity": 1,
    "country_features": 1,
    "scenario_portfolios": 1,
    "country_selection_frequency": 1,
}


def statements(sql: str):
    for item in sql.split(";"):
        cleaned = item.strip()
        if cleaned:
            yield cleaned


def normalise(value: str):
    if value == "": return None
    if value == "True": return 1
    if value == "False": return 0
    return value


def validate_foreign_key_inputs() -> None:
    """Fail before loading if harmonised location ISO3 codes lack a country row."""
    countries_path = ROOT / "data/interim/countries.csv"
    locations_path = ROOT / "data/interim/study_locations_harmonised.csv"
    with countries_path.open(encoding="utf-8", newline="") as handle:
        country_codes = {row["iso3"] for row in csv.DictReader(handle)}
    with locations_path.open(encoding="utf-8", newline="") as handle:
        location_codes = {
            row["iso3"] for row in csv.DictReader(handle) if row.get("iso3")
        }
    missing = sorted(location_codes - country_codes)
    if missing:
        raise RuntimeError(
            "study_locations contains ISO3 codes absent from countries.csv: "
            + ", ".join(missing)
        )


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--host",default=os.getenv("MYSQL_HOST","127.0.0.1")); parser.add_argument("--port",type=int,default=int(os.getenv("MYSQL_PORT","3306"))); parser.add_argument("--user",default=os.getenv("MYSQL_USER","root")); parser.add_argument("--password",default=os.getenv("MYSQL_PASSWORD","")); args=parser.parse_args()
    validate_foreign_key_inputs()
    connection=pymysql.connect(host=args.host,port=args.port,user=args.user,password=args.password,charset="utf8mb4",autocommit=False)
    try:
        with connection.cursor() as cursor:
            for statement in statements((ROOT/"sql/01_create_schema.sql").read_text(encoding="utf-8")):
                cursor.execute(statement)
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            for table, _ in reversed(TABLE_FILES): cursor.execute(f"TRUNCATE TABLE `{table}`")
            cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            loaded_counts = {}
            for table, filename in TABLE_FILES:
                path=ROOT/filename
                with path.open(encoding="utf-8",newline="") as handle:
                    reader=csv.DictReader(handle); columns=reader.fieldnames or []
                    if not columns:
                        raise RuntimeError(f"No CSV header found in {path}")
                    placeholders=",".join(["%s"]*len(columns)); names=",".join(f"`{c}`" for c in columns)
                    query=f"INSERT INTO `{table}` ({names}) VALUES ({placeholders})"
                    batch=[]; loaded=0
                    for row in reader:
                        batch.append(tuple(normalise(row[c]) for c in columns))
                        if len(batch)>=1000:
                            cursor.executemany(query,batch); loaded += len(batch); batch=[]
                    if batch:
                        cursor.executemany(query,batch); loaded += len(batch)
                    loaded_counts[table] = loaded
                    if loaded < EXPECTED_MINIMUM_ROWS[table]:
                        raise RuntimeError(f"{table} loaded {loaded} rows from {path}")
        connection.commit()
        print("MySQL load complete:")
        for table, _ in TABLE_FILES:
            print(f"- {table}: {loaded_counts[table]} rows")
    except Exception:
        connection.rollback(); raise
    finally:
        connection.close()


if __name__ == "__main__": main()
