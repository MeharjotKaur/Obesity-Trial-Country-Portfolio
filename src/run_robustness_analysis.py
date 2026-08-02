"""Monte Carlo weight and threshold sensitivity for the five-country portfolio."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from common import ROOT, atomic_json_write, utc_now
from portfolio_model import PILLARS, PortfolioConstraints, solve_portfolio


def build(root: Path = ROOT) -> dict:
    cfg = yaml.safe_load((root / "config/optimisation.yaml").read_text())
    mc = cfg["monte_carlo"]
    countries = pd.read_csv(root / "data/processed/country_features_scored.csv")
    base_w = np.array([cfg["scenarios"]["balanced"][p] for p in PILLARS])
    rng = np.random.default_rng(mc["random_seed"])
    weight_draws = rng.dirichlet(base_w * mc["dirichlet_concentration"], size=mc["simulations"])
    base_c = cfg["constraints"]
    jitter = mc["threshold_jitter_fraction"]

    selection = Counter(); portfolios = Counter(); rows = []; infeasible = 0
    for sim_id, weights_arr in enumerate(weight_draws, start=1):
        opp_min = base_c["minimum_total_opportunity_score"] * rng.uniform(1-jitter, 1+jitter)
        infra_min = base_c["minimum_total_infrastructure_score"] * rng.uniform(1-jitter, 1+jitter)
        constraints = PortfolioConstraints(
            portfolio_size=cfg["portfolio_size"], minimum_regions=base_c["minimum_regions"],
            maximum_countries_per_region=base_c["maximum_countries_per_region"],
            minimum_total_opportunity_score=float(opp_min), minimum_total_infrastructure_score=float(infra_min),
            low_confidence_threshold=base_c["low_confidence_threshold"],
            maximum_low_confidence_countries=base_c["maximum_low_confidence_countries"],
        )
        weights = dict(zip(PILLARS, weights_arr))
        result = solve_portfolio(countries, weights, constraints)
        if result["status"] != "Optimal":
            infeasible += 1; continue
        iso = tuple(sorted(result["selected"].iso3.tolist()))
        portfolios[iso] += 1
        selection.update(iso)
        rows.append({"simulation_id": sim_id, **{f"weight_{p}": weights[p] for p in PILLARS},
                     "minimum_opportunity": opp_min, "minimum_infrastructure": infra_min,
                     "objective_value": result["objective_value"], "portfolio_iso3": "|".join(iso)})

    feasible = mc["simulations"] - infeasible
    freq = countries[["iso3", "country_name", "region"]].copy()
    freq["selection_count"] = freq.iso3.map(selection).fillna(0).astype(int)
    freq["selection_frequency_pct"] = 100 * freq.selection_count / feasible
    freq = freq.sort_values(["selection_frequency_pct", "country_name"], ascending=[False, True])
    portfolio_rows = [{"portfolio_iso3": "|".join(k), "count": v, "frequency_pct": 100*v/feasible}
                      for k, v in portfolios.most_common()]
    out_tables, out_reports = root / "outputs/tables", root / "outputs/reports"
    pd.DataFrame(rows).to_csv(out_tables / "monte_carlo_runs.csv", index=False)
    freq.to_csv(out_tables / "country_selection_frequency.csv", index=False)
    pd.DataFrame(portfolio_rows).to_csv(out_tables / "portfolio_frequency.csv", index=False)
    stable = freq.loc[freq.selection_frequency_pct >= 80, "country_name"].tolist()
    summary = {
        "generated_at_utc": utc_now(), "simulations": mc["simulations"], "random_seed": mc["random_seed"],
        "feasible_runs": feasible, "infeasible_runs": infeasible,
        "stable_core_80pct": stable,
        "top_selection_frequencies": dict(zip(freq.head(10).country_name, freq.head(10).selection_frequency_pct.round(2))),
        "distinct_portfolios": len(portfolios),
        "uncertainty_scope": "MCDA weights plus opportunity and infrastructure thresholds; source-data uncertainty is not modelled.",
    }
    atomic_json_write(summary, out_reports / "group3_robustness_summary.json")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
