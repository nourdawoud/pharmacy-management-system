# Pharmacy Management System

Software Engineering course project. A web app for pharmacies to manage medicines, stock and expiry dates, sales and invoices, suppliers and purchases, with admin/employee roles and a dashboard.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # http://127.0.0.1:5000
pytest                           # run tests
```

## Modules
medicines, inventory, sales, purchases, auth, dashboard (one Flask blueprint each in `app/`).

## Workflow
See [CONTRIBUTING.md](CONTRIBUTING.md) for branching, commit and PR rules.
