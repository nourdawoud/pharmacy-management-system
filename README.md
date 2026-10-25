# Pharmacy Management System

A Flask + SQLite web application for a five-person Software Engineering project.

## Phase 1 features

- Role-based login (admin and employee)
- Medicine create/search/filter; admin-only edit/delete
- Stock monitoring, low-stock and expiry alerts
- Sales transactions, stock reduction, sales history and printable invoices
- Supplier management and purchase records with stock increases
- Dashboard statistics (medicine count, low stock, expiry, daily sales, revenue)
- Password hashing and basic input validation

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

**Demo login:** `admin` / `admin123`

Change the demo password and set a strong `SECRET_KEY` before any public deployment. This is a student demo, not production-ready pharmacy software.

## GitHub workflow

- Keep `main` stable.
- Create one branch per task: `feature/medicine-search`, `fix/expired-sale-validation`.
- Create an Issue for each task and link PRs with `Closes #<issue-number>`.
- Open a Pull Request and request a teammate review before merging.
- Use meaningful commits, e.g. `feat: add medicine search and category filter`.
- Do not commit `.env`, database files, credentials, or real patient/customer data.

## Suggested team split

1. Database + medicine CRUD/search
2. Inventory, low-stock and expiry rules
3. Sales, billing, invoices and sales history
4. Suppliers and purchases
5. Authentication, dashboard, integration and project coordination

Each person should implement and commit their own work. Do not make commits under another person's account; commit history is part of the contribution evidence.

## Known scope limits

This starter supports one medicine line per sale. Multi-item shopping carts, supplier editing/deletion, user deactivation/password reset, robust audit logging, automated tests, and deployment hardening should be treated as follow-up tasks. Add tests before Phase 2.
