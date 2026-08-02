"""Create the small, decision-relevant Group 2 figure set."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from common import ROOT

sns.set_theme(style="whitegrid", context="talk")
OUT = ROOT / "outputs/figures"; OUT.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(ROOT / "data/processed/country_features_scored.csv")

top = d.nlargest(12, "attractiveness_score").sort_values("attractiveness_score")
fig, ax = plt.subplots(figsize=(11, 7))
ax.barh(top.country_name, top.attractiveness_score, color="#2F6B8A")
ax.set(xlabel="Attractiveness score (0–100 within candidate set)", ylabel="", title="Base-case country attractiveness")
ax.set_xlim(0, 100)
fig.tight_layout(); fig.savefig(OUT / "01_country_attractiveness.png", dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 7))
sns.scatterplot(data=d, x="opportunity_score", y="infrastructure_score", size="active_trials", hue="competitive_headroom_score", palette="viridis", sizes=(60, 500), ax=ax)
for _, r in d.nlargest(8, "attractiveness_score").iterrows(): ax.annotate(r.country_name, (r.opportunity_score, r.infrastructure_score), xytext=(5, 4), textcoords="offset points", fontsize=9)
ax.set(title="Opportunity, infrastructure and competitive headroom", xlabel="Opportunity score", ylabel="Infrastructure score")
fig.tight_layout(); fig.savefig(OUT / "02_country_tradeoffs.png", dpi=180); plt.close(fig)
