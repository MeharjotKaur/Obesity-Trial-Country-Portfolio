"""Run base, scenario, leave-one-out and near-optimal portfolio analyses."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from common import ROOT, atomic_json_write, utc_now
from portfolio_model import PortfolioConstraints, solve_portfolio, weighted_scores


def load_config(root: Path):
    cfg = yaml.safe_load((root / "config/optimisation.yaml").read_text())
    constraints = PortfolioConstraints(portfolio_size=cfg["portfolio_size"], **cfg["constraints"])
    return cfg, constraints


def build(root: Path = ROOT) -> dict:
    cfg, constraints = load_config(root)
    countries = pd.read_csv(root / "data/processed/country_features_scored.csv")
    out_tables, out_reports = root / "outputs/tables", root / "outputs/reports"
    out_tables.mkdir(parents=True, exist_ok=True); out_reports.mkdir(parents=True, exist_ok=True)

    scenario_rows, selected_rows = [], []
    scenario_results = {}
    for name, weights in cfg["scenarios"].items():
        result = solve_portfolio(countries, weights, constraints)
        if result["status"] != "Optimal":
            raise RuntimeError(f"Scenario {name} is {result['status']}")
        selected = result["selected"]
        scenario_results[name] = result
        scenario_rows.append({"scenario": name, "objective_value": result["objective_value"], **result["diagnostics"]})
        for _, row in selected.iterrows():
            selected_rows.append({"scenario": name, "iso3": row.iso3, "country_name": row.country_name,
                                  "region": row.region, "model_score": row.model_score})

    base = scenario_results["balanced"]
    base_iso = set(base["selected"].iso3)
    naive = countries.assign(model_score=weighted_scores(countries, cfg["scenarios"]["balanced"])).nlargest(constraints.portfolio_size, "model_score")
    naive_regions = int(naive.region.nunique())
    naive_feasible = (
        naive_regions >= constraints.minimum_regions
        and naive.region.value_counts().max() <= constraints.maximum_countries_per_region
        and naive.opportunity_score.sum() >= constraints.minimum_total_opportunity_score
        and naive.infrastructure_score.sum() >= constraints.minimum_total_infrastructure_score
        and (naive.data_confidence_score < constraints.low_confidence_threshold).sum() <= constraints.maximum_low_confidence_countries
    )

    leave_rows = []
    for iso3 in sorted(base_iso):
        alt = solve_portfolio(countries, cfg["scenarios"]["balanced"], constraints, {iso3})
        alt_names = " | ".join(alt["selected"].country_name.tolist()) if alt["status"] == "Optimal" else ""
        leave_rows.append({"removed_iso3": iso3, "removed_country": countries.set_index("iso3").loc[iso3, "country_name"],
                           "status": alt["status"], "alternative_portfolio": alt_names,
                           "objective_loss": base["objective_value"] - alt["objective_value"] if alt["objective_value"] else None})

    # Enumerate distinct feasible alternatives by iteratively excluding one base member.
    alternatives = pd.DataFrame(leave_rows).sort_values("objective_loss")
    pd.DataFrame(scenario_rows).to_csv(out_tables / "scenario_summary.csv", index=False)
    pd.DataFrame(selected_rows).to_csv(out_tables / "scenario_portfolios.csv", index=False)
    alternatives.to_csv(out_tables / "leave_one_out_alternatives.csv", index=False)

    summary = {
        "generated_at_utc": utc_now(),
        "solver": "PuLP CBC binary integer programming",
        "base_status": base["status"],
        "base_portfolio": base["selected"].country_name.tolist(),
        "base_iso3": base["selected"].iso3.tolist(),
        "base_objective": base["objective_value"],
        "base_diagnostics": base["diagnostics"],
        "naive_top_five": naive.country_name.tolist(),
        "naive_feasible": bool(naive_feasible),
        "base_equals_naive": bool(base_iso == set(naive.iso3)),
        "scenario_portfolios": {name: result["selected"].country_name.tolist() for name, result in scenario_results.items()},
        "assumption_notice": "Weights and portfolio constraints are sponsor-planning assumptions and are tested for sensitivity.",
    }
    atomic_json_write(summary, out_reports / "group3_optimisation_summary.json")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
