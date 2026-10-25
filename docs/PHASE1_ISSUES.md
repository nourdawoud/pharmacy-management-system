# Suggested initial GitHub issues

1. **[Setup] Initialize Flask app and local environment** — Member 5. Acceptance: clean clone launches; requirements and ignore rules are present.
2. **[Database] Document and validate SQLite schema** — Member 1. Acceptance: tables/foreign keys documented; unique barcode and nonnegative stock enforced.
3. **[Medicines] Medicine CRUD and search** — Member 1. Acceptance: create/search/filter/edit/delete; duplicate barcode handled; permissions verified.
4. **[Inventory] Low-stock and expiry rules** — Member 2. Acceptance: alerts shown; expired medicine cannot be sold; stock cannot go negative.
5. **[Sales] Sales transactions and invoices** — Member 3. Acceptance: total from stored price; stock decreases only on valid sale; invoice/history available.
6. **[Purchases] Supplier and purchase workflow** — Member 4. Acceptance: supplier records saved; purchase history stored; stock increases.
7. **[Auth] Role-based login and user management** — Member 5. Acceptance: passwords hashed; employee denied admin pages; logout clears session.
8. **[Dashboard] Pharmacy statistics** — Member 5. Acceptance: medicine, low-stock, expiry, daily-sales and revenue counts shown.
9. **[Integration] End-to-end demo and merge conflicts** — All members. Acceptance: purchase → sale flow works; main stays runnable; PRs reviewed.
10. **[Quality] Add automated tests** — All members, coordinated by Member 5. Acceptance: login/permissions, medicine validation, and stock transactions tested in CI.
