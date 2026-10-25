# Contribution Rules

## Branching
- `main`: always runnable, used for the demo. No direct pushes.
- `develop`: integration branch. Feature PRs target `develop`; `develop` is merged into `main` for milestones.
- One issue = one branch = one pull request.
- Names: `feature/<short-name>` and `fix/<short-name>` (e.g. `feature/medicine-search`, `fix/expired-sale`).
- Delete the branch after merging.

## Commits
Format: `type: short description (#issue)` with types `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
Examples: `feat: add medicine search by barcode (#12)`, `fix: block sale of expired stock (#27)`.
Commit small and often. Everyone commits their own work under their own account.

## Pull requests
- Fill in the PR template and link the issue (`Closes #n`).
- At least one teammate reviews. Changes to `app/models.py` need the Database owner's review.
- Squash or rebase to keep history clean; resolve conflicts on your branch, not on `develop`.

## Issues and board
Every task is an issue with a label, an assignee and the "Phase 1" milestone.
Move cards across the board: Backlog -> To Do -> In Progress -> In Review -> Done.

## Team and ownership
| Module | File(s) | Owner |
|---|---|---|
| Database & Medicine | `app/models.py`, `app/medicines.py` | |
| Inventory & Expiry | `app/inventory.py` | |
| Sales & Billing | `app/sales.py` | |
| Supplier & Purchase | `app/purchases.py` | |
| Auth, Dashboard & Integration | `app/auth.py`, `app/dashboard.py` | |
