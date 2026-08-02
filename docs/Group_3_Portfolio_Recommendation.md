# Group 3 — Portfolio recommendation and robustness

## Decision result

Under the balanced assumptions, the optimal five-country screening portfolio is:

1. United States
2. China
3. India
4. Brazil
5. Mexico

This is a preliminary country-screening recommendation for a hypothetical global Phase III adult obesity-drug programme. It is not a final country activation plan.

## Model formulation

For every candidate country `i`, `x_i = 1` when selected and `0` otherwise. The model maximises the sum of scenario-weighted country scores and selects exactly five countries.

The base constraints require:

- At least four regions.
- No more than two countries from one region.
- Total opportunity score of at least 300.
- Total infrastructure score of at least 250.
- No more than one country with data-confidence score below 60.

These thresholds are planning assumptions. They are exposed in `config/optimisation.yaml` and varied during robustness testing.

## Why these five

The selected countries jointly provide very high patient-opportunity proxies, strong historical trial infrastructure, four-region diversification and no low-confidence market under the model's threshold. The portfolio has substantial slack above both opportunity and infrastructure minimums.

The unconstrained top five are identical to the constrained balanced solution because the five highest-scoring countries already satisfy every base constraint. This is reported explicitly; no artificial constraint was added to manufacture a different answer.

## Scenario analysis

The balanced, patient-reach and execution-readiness scenarios select the same five countries. In the competition-averse scenario, Russian Federation replaces Mexico because registered active trial pressure is lower in the source data.

That substitution is a warning, not an automatic operational recommendation. The public-data model does not include country activation feasibility, regulatory timelines, geopolitical constraints, costs, investigator availability or sponsor-specific policy. Any Russia recommendation therefore requires separate feasibility diligence before use.

## Monte Carlo analysis

Two thousand seeded simulations varied all four MCDA weights using a Dirichlet distribution and independently jittered the opportunity and infrastructure thresholds by ±10%.

- All 2,000 runs were feasible.
- United States, China, India and Brazil were selected in 100% of runs.
- Mexico was selected in 86.05%.
- Russian Federation was selected in 13.95%.
- Only two distinct portfolios occurred.

The analysis supports a four-country stable core and identifies the fifth position as the primary assumption-sensitive decision.

## What Monte Carlo does not prove

The simulation measures sensitivity to decision assumptions; it does not establish future trial success. It does not currently propagate source-estimate uncertainty, missing unregistered trials, country costs, recruitment rates or regulatory uncertainty.

## Defensible interpretation

Use the output as an evidence-based market-screening shortlist. Before operational activation, a sponsor should add regulatory, cost, investigator-capacity, patient-access and geopolitical diligence and then rerun the model with sponsor-approved assumptions.
