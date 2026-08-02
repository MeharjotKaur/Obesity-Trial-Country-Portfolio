# Interview defence guide

## Core logic you must own

### Why this is not machine learning

There is no defensible labelled outcome for country-level recruitment speed, cost or trial success. The project therefore uses prescriptive analytics: transparent multi-criteria scoring, constrained optimisation and sensitivity analysis.

### Why optimisation if the answer equals the top five?

Ranking evaluates countries independently; optimisation verifies the combination against portfolio rules. In the base case, the top five were feasible, so the optimiser confirmed rather than changed the answer. It still provides constraint diagnostics, scenario re-solving and leave-one-out substitutes. No artificial rule was introduced to manufacture a difference.

### What PuLP does

PuLP expresses the binary variables, objective and constraints. CBC searches feasible combinations and returns the maximum-scoring portfolio. You should explain the formulation, not claim to have implemented the CBC algorithm.

### Why Monte Carlo?

Weights and selected thresholds are assumptions. Repeatedly perturbing them reveals whether the recommendation is stable. It is sensitivity analysis, not proof of future success.

## Likely cross-questions

**Why only Phase III?**  
The decision scenario is a confirmatory global programme. Phase III history is a closer infrastructure and competition proxy than early-phase activity, while the limitation is narrower sample size.

**How did you prevent irrelevant obesity records?**  
I separated broad retrieval from therapeutic relevance. The rules inspect intervention modality, target population and weight-management intent, and a stratified 70-record sheet exposed false inclusions such as perioperative studies in bariatric patients.

**Why 117 rather than 717?**  
717 is the high-recall audit universe. The 117-study cohort is the conservative analytical evidence base after therapeutic-intent filtering.

**Is obese population the eligible patient pool?**  
No. It is population multiplied by adult obesity prevalence, explicitly labelled a burden proxy. Eligibility depends on age, BMI, comorbidities, exclusions and access, which these sources cannot resolve.

**Can a listed facility be treated as available?**  
No. It is historical registered-location evidence. Actual capacity requires feasibility outreach and current investigator/site diligence.

**Why these weights?**  
They encode a balanced sponsor view: 30% opportunity, 30% infrastructure, 25% headroom and 15% confidence. They are exposed, scenario-tested and sampled rather than declared objectively correct.

**What does a 100% selection frequency mean?**  
The country appeared in all 2,000 defined assumption draws. It does not mean a 100% probability that the country is optimal in reality.

**Why does Russia appear?**  
Its public registered data show low active pressure, which helps under competition-heavy weights. The model omits material geopolitical, regulatory and operational feasibility, so Russia is a diligence flag, not an automatic recommendation.

**What would you add with sponsor data?**  
Country and site startup timelines, budget, contracting performance, investigator availability, screen-failure and recruitment data, regulatory risk, patient-access pathways and sponsor policy constraints.

**How did SQL add value?**  
The MySQL layer stores normalised study, location, sponsor, intervention and country tables; foreign keys protect integrity, indexes support joins, CTEs calculate repeat facilities, and window functions rank country facilities. Python performs reproducible extraction, scoring and optimisation.

## Honest ownership wording

Say: "I developed the decision framework and interpretation with AI-assisted implementation, validated the pipeline, changed scenarios and can explain each transformation and constraint."

Do not say that you independently wrote every line if that is not true. The defensible differentiator is your command of the problem formulation, assumptions, validation and conclusion.
