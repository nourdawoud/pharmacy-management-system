#!/usr/bin/env bash
# Run ONCE by the Auth/Integration owner from inside the cloned repo.
# Requires GitHub CLI: https://cli.github.com  then:  gh auth login
# Fill in the five GitHub usernames below first.
set -e

DB_OWNER="username1"       # Database & Medicine
INV_OWNER="username2"      # Inventory & Expiry
SALES_OWNER="username3"    # Sales & Billing
SUP_OWNER="username4"      # Supplier & Purchase
AUTH_OWNER="username5"     # Auth, Dashboard & Integration

MILESTONE="Phase 1"

echo "Creating labels..."
for l in database inventory sales purchases auth dashboard devops docs testing priority-high; do
  gh label create "$l" --force >/dev/null
done

echo "Creating milestone..."
gh api repos/{owner}/{repo}/milestones -f title="$MILESTONE" >/dev/null 2>&1 || true

issue() { # title | label | assignee | body
  gh issue create --title "$1" --label "$2" --assignee "$3" --milestone "$MILESTONE" --body "$4" >/dev/null
  echo "  + $1"
}

echo "Creating issues..."
# ---------- Database & Medicine ----------
issue "Design database schema" "database,priority-high" "$DB_OWNER" "Finalise tables in app/models.py (User, Medicine, Supplier, Purchase, Sale + items). Share ER diagram in docs/."
issue "Seed script with sample data" "database" "$DB_OWNER" "Script that inserts demo medicines, suppliers and users so the demo is never empty."
issue "Add medicine" "database" "$DB_OWNER" "Form + endpoint to create a medicine (name, category, price, barcode, quantity, expiry, supplier). Validate input."
issue "Edit medicine" "database" "$DB_OWNER" "Edit an existing medicine's details."
issue "Delete medicine" "database" "$DB_OWNER" "Delete with confirmation; block deletion if the medicine appears in past sales (or soft-delete)."
issue "Search and filter medicines" "database" "$DB_OWNER" "Search by name/barcode, filter by category."
issue "Review integration pull requests" "database" "$DB_OWNER" "Review complex PRs and help integrate modules."

# ---------- Inventory & Expiry ----------
issue "Show current stock levels" "inventory" "$INV_OWNER" "Inventory page listing quantity per medicine."
issue "Low-stock alert logic" "inventory,priority-high" "$INV_OWNER" "Flag medicines where quantity <= reorder_level and list them."
issue "Expiry tracking" "inventory" "$INV_OWNER" "List expired medicines and those expiring within 30 days."
issue "Stock update helper (increase/decrease)" "inventory,priority-high" "$INV_OWNER" "Reusable function used by Sales (decrease) and Purchases (increase). Never allow negative stock."
issue "Block sale of expired or unavailable stock" "inventory" "$INV_OWNER" "Validation function used by Sales before completing a transaction."
issue "Highlight alerts in inventory UI" "inventory" "$INV_OWNER" "Colour-code low-stock and expired rows."

# ---------- Sales & Billing ----------
issue "Create new sale (cart)" "sales,priority-high" "$SALES_OWNER" "Start a transaction, search/select medicines and quantities."
issue "Calculate subtotals and total" "sales" "$SALES_OWNER" "Per-line subtotal and invoice total."
issue "Complete sale and reduce stock" "sales,priority-high" "$SALES_OWNER" "Save Sale + SaleItems and decrease stock using the inventory helper in one transaction."
issue "Generate receipt/invoice" "sales" "$SALES_OWNER" "Printable invoice page with items, totals, date and cashier."
issue "Sales history page" "sales" "$SALES_OWNER" "List previous sales, open any to view its invoice."
issue "Handle sale errors" "sales" "$SALES_OWNER" "Empty cart, insufficient stock, expired item: show clear messages."

# ---------- Supplier & Purchase ----------
issue "Add and edit suppliers" "purchases" "$SUP_OWNER" "CRUD for suppliers with contact info (phone, email, address)."
issue "Supplier list and details" "purchases" "$SUP_OWNER" "List suppliers, view one supplier's details."
issue "Record a purchase" "purchases,priority-high" "$SUP_OWNER" "Choose supplier, add medicines with quantity and unit cost."
issue "Update inventory on purchase" "purchases,priority-high" "$SUP_OWNER" "Increase stock using the inventory helper when a purchase is received."
issue "Purchase history" "purchases" "$SUP_OWNER" "List past purchases with totals; filter by supplier."

# ---------- Auth, Dashboard & Integration ----------
issue "Repository setup and branch protection" "devops,priority-high" "$AUTH_OWNER" "Protect main, add collaborators, create develop branch, add PR template."
issue "Set up GitHub Project board" "devops" "$AUTH_OWNER" "Kanban columns: Backlog, To Do, In Progress, In Review, Done. Add all issues."
issue "Login and logout" "auth,priority-high" "$AUTH_OWNER" "Session-based login with hashed passwords."
issue "Admin and employee roles" "auth" "$AUTH_OWNER" "Role field and admin_required decorator."
issue "Permissions per role" "auth" "$AUTH_OWNER" "Employees: sell and view stock. Admins: everything incl. user, supplier and medicine deletion."
issue "Admin: manage users" "auth" "$AUTH_OWNER" "Admin can create employee accounts (registration is admin-only)."
issue "Dashboard statistics" "dashboard" "$AUTH_OWNER" "Total medicines, low-stock count, near-expiry count, daily sales, total revenue."
issue "Navigation and layout" "dashboard" "$AUTH_OWNER" "Base template and menu connecting all modules."
issue "Integrate modules and prepare demo" "devops" "$AUTH_OWNER" "Merge everything, run through the demo script, fix integration bugs."

echo "Done. Create the board in GitHub: Projects -> New project -> Board, then add the issues."
