import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class DecisionModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tax = pd.read_csv(ROOT / "data/processed/trial_taxonomy_final.csv")
        cls.score = pd.read_csv(ROOT / "data/processed/country_features_scored.csv")

    def test_final_cohort_is_subset(self):
        self.assertTrue((self.tax.loc[self.tax.final_included, "included"] == True).all())

    def test_scores_are_bounded_and_complete(self):
        cols = ["opportunity_score", "infrastructure_score", "competitive_headroom_score", "data_confidence_score", "attractiveness_score"]
        self.assertFalse(self.score[cols].isna().any().any())
        self.assertTrue(((self.score[cols] >= 0) & (self.score[cols] <= 100)).all().all())

    def test_candidate_gates(self):
        self.assertTrue((self.score.relevant_studies >= 2).all())
        self.assertTrue((self.score.unique_facilities >= 5).all())

    def test_weights_reproduce_score(self):
        expected = (.30*self.score.opportunity_score + .30*self.score.infrastructure_score + .25*self.score.competitive_headroom_score + .15*self.score.data_confidence_score)
        self.assertLess((expected-self.score.attractiveness_score).abs().max(), 1e-9)


if __name__ == "__main__": unittest.main()
