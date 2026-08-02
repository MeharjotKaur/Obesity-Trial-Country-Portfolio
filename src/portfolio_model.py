"""Reusable binary portfolio optimisation model for Group 3."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd
import pulp

PILLARS = ("opportunity", "infrastructure", "competitive_headroom", "data_confidence")


@dataclass(frozen=True)
class PortfolioConstraints:
    portfolio_size: int
    minimum_regions: int
    maximum_countries_per_region: int
    minimum_total_opportunity_score: float
    minimum_total_infrastructure_score: float
    low_confidence_threshold: float
    maximum_low_confidence_countries: int


def weighted_scores(countries: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    if set(weights) != set(PILLARS):
        raise ValueError(f"Weights must contain exactly {PILLARS}")
    if abs(sum(weights.values()) - 1.0) > 1e-8 or min(weights.values()) < 0:
        raise ValueError("Weights must be non-negative and sum to one")
    return sum(countries[f"{pillar}_score"] * weights[pillar] for pillar in PILLARS)


def solve_portfolio(
    countries: pd.DataFrame,
    weights: Mapping[str, float],
    constraints: PortfolioConstraints,
    excluded_iso3: set[str] | None = None,
) -> dict:
    frame = countries.reset_index(drop=True).copy()
    frame["model_score"] = weighted_scores(frame, weights)
    excluded_iso3 = excluded_iso3 or set()

    model = pulp.LpProblem("country_portfolio", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"select_{frame.loc[i, 'iso3']}", cat="Binary") for i in frame.index}
    regions = sorted(frame.region.unique())
    y = {r: pulp.LpVariable(f"use_region_{j}", cat="Binary") for j, r in enumerate(regions)}

    model += pulp.lpSum(frame.loc[i, "model_score"] * x[i] for i in frame.index)
    model += pulp.lpSum(x.values()) == constraints.portfolio_size, "portfolio_size"
    model += pulp.lpSum(y.values()) >= constraints.minimum_regions, "minimum_regions"
    for r in regions:
        members = [i for i in frame.index if frame.loc[i, "region"] == r]
        model += pulp.lpSum(x[i] for i in members) <= constraints.maximum_countries_per_region, f"region_cap_{regions.index(r)}"
        model += pulp.lpSum(x[i] for i in members) >= y[r], f"region_used_lower_{regions.index(r)}"
        model += pulp.lpSum(x[i] for i in members) <= constraints.portfolio_size * y[r], f"region_used_upper_{regions.index(r)}"
    model += pulp.lpSum(frame.loc[i, "opportunity_score"] * x[i] for i in frame.index) >= constraints.minimum_total_opportunity_score, "minimum_opportunity"
    model += pulp.lpSum(frame.loc[i, "infrastructure_score"] * x[i] for i in frame.index) >= constraints.minimum_total_infrastructure_score, "minimum_infrastructure"
    low_conf = [i for i in frame.index if frame.loc[i, "data_confidence_score"] < constraints.low_confidence_threshold]
    model += pulp.lpSum(x[i] for i in low_conf) <= constraints.maximum_low_confidence_countries, "low_confidence_cap"
    for i in frame.index:
        if frame.loc[i, "iso3"] in excluded_iso3:
            model += x[i] == 0, f"excluded_{frame.loc[i, 'iso3']}"

    status_code = model.solve(pulp.PULP_CBC_CMD(msg=False))
    status = pulp.LpStatus[status_code]
    if status != "Optimal":
        return {"status": status, "selected": pd.DataFrame(), "objective_value": None, "diagnostics": {}}

    chosen = frame.loc[[i for i in frame.index if x[i].value() > 0.5]].copy()
    chosen = chosen.sort_values("model_score", ascending=False)
    diagnostics = {
        "countries_selected": int(len(chosen)),
        "regions_selected": int(chosen.region.nunique()),
        "maximum_region_count": int(chosen.region.value_counts().max()),
        "total_opportunity_score": float(chosen.opportunity_score.sum()),
        "total_infrastructure_score": float(chosen.infrastructure_score.sum()),
        "low_confidence_countries": int((chosen.data_confidence_score < constraints.low_confidence_threshold).sum()),
    }
    diagnostics["opportunity_slack"] = diagnostics["total_opportunity_score"] - constraints.minimum_total_opportunity_score
    diagnostics["infrastructure_slack"] = diagnostics["total_infrastructure_score"] - constraints.minimum_total_infrastructure_score
    return {
        "status": status,
        "selected": chosen,
        "objective_value": float(pulp.value(model.objective)),
        "diagnostics": diagnostics,
    }
