# Pharmacy Management System

Software Engineering course project: a pharmacy web application for medicine management, inventory and expiry alerts, sales and invoices, suppliers and purchases, admin/employee roles, and dashboard metrics.

## Run locally

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000.

## Demo login

- Username: `admin`
- Password: `admin123`

The app creates sample medicines and a default supplier in a new database. Change the demo password and set a strong `SECRET_KEY` environment variable before deploying publicly. This is a course demo, not production-ready pharmacy software.

## Tests

Run `pytest -q`. Tests use temporary SQLite databases and cover login protection, dashboard rendering, medicine creation/search, purchase and sale stock changes, invoice generation, expired-medicine rejection, and employee permissions.

## Active application code

The runnable Phase 1 demo is implemented in the repository-root `app.py`; `run.py` explicitly loads that file. The `app/` directory is an incomplete modular refactor scaffold and is not currently used by the running demo. Changes to those scaffold files do not affect the current runtime; coordinate before migrating features into them.

## Team workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch, commit, review, and pull-request conventions.
