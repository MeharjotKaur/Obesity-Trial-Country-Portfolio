# Manual reproduction guide

## Python validation

1. Install Python 3.12.
2. Open a terminal in the repository root.
3. Create and activate a virtual environment.
4. Run `pip install -r requirements.txt`.
5. Run `python src/run_all.py --use-snapshot`.

Expected checkpoints:

- 117 final retained studies.
- 45 screened countries.
- Base portfolio: United States, China, India, Brazil, Mexico.
- 2,000/2,000 feasible robustness runs.
- 11 automated tests passing.

## MySQL 8 validation

1. Confirm MySQL Server 8 is running.
2. Do not use Workbench's Table Data Import Wizard and do not execute the SQL files manually.
3. From the repository root, run `python src/validate_mysql.py`.
4. Enter the local MySQL password when prompted; the characters are intentionally hidden.
5. Confirm all 10 row-count reconciliations show `[PASS]` and the terminal ends in `STATUS: PASS`.
6. Send only `outputs/reports/mysql_validation.txt` for review if validation support is needed.

Optional: copy `.env.example` to `.env` and store local credentials there instead of entering the password interactively. Never share or commit `.env`.

The loader recreates and repopulates project tables. Use a local development MySQL instance, not a shared production server.

## Fresh-source rerun

Run `python src/run_all.py` without `--use-snapshot`. Live counts may differ from the published result because trial registrations change. Commit numerical resume claims only from a dated, validated run.
