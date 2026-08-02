import csv
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from build_foundation import age_years


class FoundationTests(unittest.TestCase):
    def test_age_parser(self):
        self.assertEqual(age_years("18 Years"),18)
        self.assertAlmostEqual(age_years("6 Months"),0.5)
        self.assertIsNone(age_years("N/A"))

    def test_snapshot_is_valid_and_unique(self):
        with (ROOT/"data/raw/clinical_trials_2026-07-31.json").open(encoding="utf-8") as handle:
            studies=json.load(handle)
        ids=[s["protocolSection"]["identificationModule"]["nctId"] for s in studies]
        self.assertEqual(len(ids),717)
        self.assertEqual(len(ids),len(set(ids)))

    def test_relational_integrity(self):
        with (ROOT/"data/interim/studies.csv").open(encoding="utf-8") as handle:
            studies=list(csv.DictReader(handle))
        ids={r["nct_id"] for r in studies}
        self.assertEqual(len(ids),len(studies))
        for filename in ["conditions.csv","interventions.csv","sponsors.csv","study_locations_harmonised.csv"]:
            with (ROOT/"data/interim"/filename).open(encoding="utf-8") as handle:
                rows=list(csv.DictReader(handle))
            self.assertFalse({r["nct_id"] for r in rows}-ids, filename)

    def test_country_mapping(self):
        with (ROOT/"data/interim/study_locations_harmonised.csv").open(encoding="utf-8") as handle:
            rows=list(csv.DictReader(handle))
        unresolved=[r for r in rows if r["country_raw"] and not r["iso3"]]
        self.assertEqual({r["country_raw"] for r in unresolved},{"Serbia and Montenegro"})
        self.assertEqual(len(unresolved),1)


if __name__ == "__main__": unittest.main()
