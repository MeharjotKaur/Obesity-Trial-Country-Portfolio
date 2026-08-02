"""Create decision-focused Group 3 figures."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from common import ROOT


def build(root: Path = ROOT):
    sns.set_theme(style="whitegrid", context="talk")
    figures = root / "outputs/figures"; figures.mkdir(parents=True, exist_ok=True)
    portfolios = pd.read_csv(root / "outputs/tables/scenario_portfolios.csv")
    freq = pd.read_csv(root / "outputs/tables/country_selection_frequency.csv")
    features = pd.read_csv(root / "data/processed/country_features_scored.csv")

    selected = portfolios[portfolios.scenario.eq("balanced")].merge(
        features[["iso3", "opportunity_score", "infrastructure_score", "competitive_headroom_score", "data_confidence_score"]], on="iso3"
    ).set_index("country_name")
    pillars = selected[["opportunity_score", "infrastructure_score", "competitive_headroom_score", "data_confidence_score"]]
    pillars.columns = ["Patient opportunity", "Infrastructure", "Competitive headroom", "Data confidence"]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    sns.heatmap(pillars, annot=True, fmt=".1f", cmap="YlGnBu", vmin=0, vmax=100, ax=ax, cbar_kws={"label": "Score (0–100)"})
    ax.set(xlabel="", ylabel="", title="Balanced portfolio: strengths differ by country")
    fig.tight_layout(); fig.savefig(figures / "03_portfolio_pillar_scores.png", dpi=220); plt.close(fig)

    top = freq[freq.selection_frequency_pct.gt(0)].sort_values("selection_frequency_pct")
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    colors = ["#176B87" if v >= 80 else "#E09F3E" for v in top.selection_frequency_pct]
    ax.barh(top.country_name, top.selection_frequency_pct, color=colors)
    ax.axvline(80, color="#444", linestyle="--", linewidth=1.2, label="Stable-core threshold")
    ax.set(xlim=(0, 105), xlabel="Selection frequency across 2,000 runs (%)", ylabel="")
    ax.set_title("Four-country stable core; fifth position is assumption-sensitive", fontsize=18, pad=12)
    for y, v in enumerate(top.selection_frequency_pct): ax.text(v + 1, y, f"{v:.1f}%", va="center", fontsize=10)
    ax.legend(loc="lower right"); fig.tight_layout()
    fig.savefig(figures / "04_selection_frequency.png", dpi=220); plt.close(fig)

    matrix = portfolios.assign(selected=1).pivot_table(index="country_name", columns="scenario", values="selected", fill_value=0)
    order = ["balanced", "patient_reach", "execution_readiness", "competition_averse"]
    matrix = matrix.reindex(columns=order).sort_values(order, ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    sns.heatmap(matrix, annot=False, cmap=["#F2F2F2", "#176B87"], cbar=False, linewidths=1, linecolor="white", ax=ax)
    ax.set(xlabel="", ylabel="", title="Portfolio membership across strategic scenarios")
    ax.set_xticklabels(["Balanced", "Patient reach", "Execution readiness", "Competition averse"], rotation=20, ha="right")
    fig.tight_layout(); fig.savefig(figures / "05_scenario_portfolios.png", dpi=220); plt.close(fig)


if __name__ == "__main__": build()
