"""Create a deterministic, stratified taxonomy review sheet for human validation."""
from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

from common import ROOT

SEED = 20260731


def main() -> None:
    rows=list(csv.DictReader((ROOT/"data/interim/studies.csv").open(encoding="utf-8")))
    strata=defaultdict(list)
    for row in rows:
        if row["included"] == "True": key="included_review" if row["review_flags"] else "included_clean"
        else: key="excluded"
        strata[key].append(row)
    rng=random.Random(SEED); sample=[]
    targets={"included_clean":20,"included_review":25,"excluded":25}
    for key,n in targets.items():
        chosen=rng.sample(strata[key],min(n,len(strata[key])))
        for row in chosen:
            sample.append({"stratum":key,"nct_id":row["nct_id"],"brief_title":row["brief_title"],"intervention_types":row["intervention_types"],"minimum_age":row["minimum_age"],"maximum_age":row["maximum_age"],"rule_included":row["included"],"rule_exclusion_reasons":row["exclusion_reasons"],"rule_review_flags":row["review_flags"],"manual_label":"","reviewer_rationale":""})
    out=ROOT/"data/audit/taxonomy_manual_review_sample.csv"; out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(sample[0]);
    with out.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(sample)
    print({"sample_rows":len(sample),"seed":SEED,"strata":targets,"output":str(out)})


if __name__ == "__main__": main()

