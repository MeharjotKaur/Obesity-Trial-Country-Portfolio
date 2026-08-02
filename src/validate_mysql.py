"""Load MySQL 8, run SQL checks/views/queries, and save a shareable validation log."""
from __future__ import annotations

import os
import getpass
import csv
import subprocess
import sys
from pathlib import Path

import pymysql

from common import ROOT
from load_mysql import TABLE_FILES, statements


def load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    load_dotenv()
    password = os.getenv("MYSQL_PASSWORD", "")
    if not password or password == "replace_locally":
        password = getpass.getpass("MySQL password: ")
        os.environ["MYSQL_PASSWORD"] = password
    subprocess.run([sys.executable, "src/load_mysql.py"], cwd=ROOT, check=True)
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=password,
        database="obesity_trial_portfolio",
        charset="utf8mb4",
    )
    lines = ["MYSQL VALIDATION", "================", ""]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            lines.append(f"MySQL version: {cursor.fetchone()[0]}")
            lines.extend(["", "Row-count reconciliation:"])
            for table, relative_path in TABLE_FILES:
                with (ROOT / relative_path).open(encoding="utf-8", newline="") as handle:
                    expected = sum(1 for _ in csv.DictReader(handle))
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                actual = int(cursor.fetchone()[0])
                status = "PASS" if actual == expected and actual > 0 else "FAIL"
                lines.append(f"- {table}: database={actual}, csv={expected} [{status}]")
                if status == "FAIL":
                    raise RuntimeError(f"Row-count mismatch for {table}: database={actual}, csv={expected}")
            for statement in statements((ROOT / "sql/03_analytical_views.sql").read_text(encoding="utf-8")):
                cursor.execute(statement)
            checks = list(statements((ROOT / "sql/02_quality_checks.sql").read_text(encoding="utf-8")))
            for statement in checks:
                cursor.execute(statement)
                if cursor.description:
                    rows = cursor.fetchall()
                    lines.extend(["", "Quality checks:"])
                    failures = 0
                    for name, count in rows:
                        failures += int(count)
                        lines.append(f"- {name}: {count}")
                    if failures:
                        raise RuntimeError(f"MySQL validation found {failures} quality-check failure(s)")
            cursor.execute("SELECT COUNT(*) FROM studies")
            lines.append(f"Studies loaded: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM country_features WHERE screen_pass = 1")
            lines.append(f"Screened candidate countries: {cursor.fetchone()[0]}")
            cursor.execute("SELECT scenario, COUNT(*) FROM scenario_portfolios GROUP BY scenario ORDER BY scenario")
            lines.append("Scenario rows: " + ", ".join(f"{name}={count}" for name, count in cursor.fetchall()))
            cursor.execute("SELECT country_name, selection_frequency_pct FROM country_selection_frequency ORDER BY selection_frequency_pct DESC, country_name LIMIT 6")
            lines.append("Top selection frequencies:")
            lines.extend(f"- {name}: {float(value):.2f}%" for name, value in cursor.fetchall())
    finally:
        connection.close()
    lines.extend(["", "STATUS: PASS"])
    output = ROOT / "outputs/reports/mysql_validation.txt"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
