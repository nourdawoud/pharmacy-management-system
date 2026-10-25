# Team workflow and Phase 1 evidence

## Roles

| Member | Ownership | Suggested first branch |
|---|---|---|
| Member 1 | Database schema, medicine CRUD, search/filter | `feature/medicine-management` |
| Member 2 | Inventory rules, low-stock and expiry handling | `feature/inventory-alerts` |
| Member 3 | Sales transaction, invoice and sales history | `feature/sales-billing` |
| Member 4 | Supplier directory and purchase intake | `feature/supplier-purchases` |
| Member 5 | Login/roles, dashboard, integration and board upkeep | `feature/auth-dashboard` |

Each person should use their own GitHub account and author their own commits. Branch from main, create an issue for each task, open a pull request, request a teammate review, and link it with `Closes #<issue-number>`. Keep commits small and meaningful. Do not commit credentials, local database files, or real customer/patient data.

## Scrum board
Create a GitHub Project board with columns Backlog, Todo, In Progress, In Review, Done. Track owner, acceptance criteria, blockers, and meeting outcomes. Record real meeting notes in `docs/MEETING_NOTES.md`.

## Phase 1 demo checklist
- [ ] Clean clone launches using README instructions
- [ ] Admin and employee permissions differ
- [ ] Create/search/edit/delete medicine records
- [ ] Purchase increases stock
- [ ] Sale decreases stock and generates invoice
- [ ] Expired/unavailable medicine cannot be sold
- [ ] Dashboard reflects saved data
- [ ] Show Issues, board, branches, reviewed PRs, and each member's genuine commits
