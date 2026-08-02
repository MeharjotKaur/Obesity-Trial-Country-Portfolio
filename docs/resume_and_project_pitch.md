# Resume and project pitch

## Recommended project title

**Global Phase III Obesity Trial Country-Portfolio Optimisation**

## Resume bullets

- Engineered a reproducible ClinicalTrials.gov API pipeline to audit 717 Phase III obesity records, apply therapeutic-intent rules and construct a conservative 117-study evidence cohort across 53 countries.
- Built a four-pillar country-attractiveness model across 45 eligible markets and formulated a PuLP/CBC binary programme to select a five-country portfolio under opportunity, infrastructure, competition, confidence and regional-diversity constraints.
- Stress-tested the recommendation across four sponsor-priority scenarios and 2,000 Monte Carlo runs, identifying a four-country stable core and an assumption-sensitive fifth market.

Use only after reproducing the project locally. If space is tight, use the second and third bullets.

## 30-second version

I built a healthcare strategy analytics project to screen countries for a hypothetical global Phase III obesity-drug programme. I transformed ClinicalTrials.gov, WHO and World Bank data into opportunity, historical infrastructure, competitive-headroom and confidence scores, then used binary optimisation to select five countries under portfolio constraints. I tested the result across four scenarios and 2,000 sensitivity runs. The key output was a stable four-country core, while the fifth position changed under competition-heavy assumptions.

## Two-minute version

The business question was not "which countries rank highest?" but "which combination of five countries forms the strongest diversified portfolio under explicit constraints?" I first extracted 717 broad Phase III obesity records and built relational study, sponsor, intervention and location tables. Because keyword matching created false positives, I used therapeutic intent to freeze a conservative 117-study general-adult pharmacotherapy cohort.

At country level I engineered four pillars: an obesity-burden opportunity proxy; historical trial infrastructure based on facilities, repeat experience, studies and sponsor diversity; competitive headroom based on active registered pressure; and data confidence. Forty-five countries met minimum evidence and coverage gates. The scores are transparent assumptions, not objective truth.

I then formulated a binary integer programme in PuLP/CBC to select exactly five countries while enforcing regional diversity, minimum opportunity and infrastructure, and a cap on low-confidence markets. The balanced solution was the United States, China, India, Brazil and Mexico. The simple top five happened to be feasible too, which I reported honestly.

Finally, I changed sponsor priorities and ran 2,000 seeded sensitivity simulations. The United States, China, India and Brazil appeared in every run; Mexico appeared in 86.05%, with Russia appearing only under competition-heavy assumptions. Because the public data omit costs, regulatory feasibility and current investigator capacity, I position this as a preliminary screening tool, not a final activation plan.
