"""Reproducibly extract Phase III obesity trials from ClinicalTrials.gov API v2."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from common import ROOT, atomic_json_write, sha256, utc_now


def fetch_json(url: str, timeout: int, max_attempts: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "obesity-trial-portfolio/1.0"})
    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == max_attempts:
                raise
            time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError("unreachable")


def extract(config_path: Path) -> tuple[Path, Path]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    source = config["clinical_trials"]
    params = {
        "query.cond": source["query_condition"],
        "filter.advanced": source["advanced_filter"],
        "pageSize": source["page_size"],
        "countTotal": "true",
        "format": "json",
    }
    studies: list[dict[str, Any]] = []
    pages = 0
    expected_total = None
    while True:
        url = source["endpoint"] + "?" + urllib.parse.urlencode(params)
        payload = fetch_json(url, source["timeout_seconds"], source["max_attempts"])
        pages += 1
        expected_total = payload.get("totalCount", expected_total)
        studies.extend(payload.get("studies", []))
        token = payload.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token

    ids = [s.get("protocolSection", {}).get("identificationModule", {}).get("nctId") for s in studies]
    if expected_total is not None and len(studies) != expected_total:
        raise ValueError(f"Pagination incomplete: expected {expected_total}, received {len(studies)}")
    if None in ids or len(ids) != len(set(ids)):
        raise ValueError("NCT IDs are missing or duplicated")

    raw_dir = ROOT / config["paths"]["raw"]
    snapshot = raw_dir / f"clinical_trials_{config['snapshot_date']}.json"
    manifest = raw_dir / f"clinical_trials_{config['snapshot_date']}_manifest.json"
    atomic_json_write(studies, snapshot)
    atomic_json_write({
        "source": source["endpoint"],
        "query": {k: v for k, v in params.items() if k != "pageToken"},
        "retrieved_at_utc": utc_now(),
        "pages": pages,
        "record_count": len(studies),
        "unique_nct_ids": len(set(ids)),
        "sha256": sha256(snapshot),
        "project_version": config["project_version"],
    }, manifest)
    return snapshot, manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/pipeline.yaml")
    args = parser.parse_args()
    output, manifest = extract(args.config)
    print(output)
    print(manifest)

