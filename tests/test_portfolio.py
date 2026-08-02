import sys
import unittest
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from portfolio_model import PortfolioConstraints, solve_portfolio


class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.countries = pd.read_csv(ROOT / "data/processed/country_features_scored.csv")
        cls.cfg = yaml.safe_load((ROOT / "config/optimisation.yaml").read_text())
        cls.constraints = PortfolioConstraints(portfolio_size=cls.cfg["portfolio_size"], **cls.cfg["constraints"])
        cls.result = solve_portfolio(cls.countries, cls.cfg["scenarios"]["balanced"], cls.constraints)

    def test_base_is_optimal_and_selects_five(self):
        self.assertEqual(self.result["status"], "Optimal")
        self.assertEqual(len(self.result["selected"]), 5)

    def test_constraints_hold(self):
        chosen = self.result["selected"]
        c = self.constraints
        self.assertGreaterEqual(chosen.region.nunique(), c.minimum_regions)
        self.assertLessEqual(chosen.region.value_counts().max(), c.maximum_countries_per_region)
        self.assertGreaterEqual(chosen.opportunity_score.sum(), c.minimum_total_opportunity_score)
        self.assertGreaterEqual(chosen.infrastructure_score.sum(), c.minimum_total_infrastructure_score)
        self.assertLessEqual((chosen.data_confidence_score < c.low_confidence_threshold).sum(), c.maximum_low_confidence_countries)

    def test_excluding_each_base_country_changes_portfolio(self):
        for iso3 in self.result["selected"].iso3:
            alt = solve_portfolio(self.countries, self.cfg["scenarios"]["balanced"], self.constraints, {iso3})
            self.assertEqual(alt["status"], "Optimal")
            self.assertNotIn(iso3, set(alt["selected"].iso3))


if __name__ == "__main__": unittest.main()
