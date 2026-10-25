import os
import sqlite3
from datetime import date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("PHARMACY_DB", os.path.join(BASE_DIR, "pharmacy.db"))
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-key")
# Keep session cookies unavailable to JavaScript and limit cross-site sending.
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','employee'))
        );
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '',
            barcode TEXT UNIQUE,
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
            reorder_level INTEGER NOT NULL DEFAULT 10 CHECK(reorder_level >= 0),
            expiry_date TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            address TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_cost REAL NOT NULL CHECK(unit_cost >= 0),
            purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY(medicine_id) REFERENCES medicines(id)
        );
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL CHECK(total >= 0),
            sold_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            subtotal REAL NOT NULL CHECK(subtotal >= 0),
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(medicine_id) REFERENCES medicines(id)
        );
        """)
        if not db.execute("SELECT id FROM users WHERE username='admin'").fetchone():
            db.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                       ("admin", generate_password_hash("admin123"), "admin"))
        if not db.execute("SELECT id FROM suppliers LIMIT 1").fetchone():
            db.execute("INSERT INTO suppliers(name,phone,email,address) VALUES(?,?,?,?)",
                       ("Default Supplier", "", "", ""))
        if not db.execute("SELECT id FROM medicines LIMIT 1").fetchone():
            sample = [
                ("Paracetamol 500mg", "Pain relief", "MED-0001", 25.0, 80, 15, (date.today()+timedelta(days=240)).isoformat()),
                ("Vitamin C", "Vitamins", "MED-0002", 60.0, 8, 10, (date.today()+timedelta(days=25)).isoformat()),
                ("Amoxicillin 250mg", "Antibiotic", "MED-0003", 95.0, 0, 10, (date.today()+timedelta(days=400)).isoformat()),
            ]
            db.executemany("""INSERT INTO medicines(name,category,barcode,unit_price,quantity,reorder_level,expiry_date)
                              VALUES(?,?,?,?,?,?,?)""", sample)


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return fn(*args, **kwargs)
    return wrapped


@app.template_filter("money")
def money(value):
    return f"{float(value or 0):,.2f}"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update(user_id=user["id"], username=user["username"], role=user["role"])
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    today = date.today().isoformat()
    soon = (date.today() + timedelta(days=30)).isoformat()
    with get_db() as db:
        total_medicines = db.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
        low_stock = db.execute("SELECT COUNT(*) FROM medicines WHERE quantity <= reorder_level").fetchone()[0]
        expiring = db.execute("SELECT COUNT(*) FROM medicines WHERE expiry_date IS NOT NULL AND expiry_date BETWEEN ? AND ?", (today, soon)).fetchone()[0]
        expired = db.execute("SELECT COUNT(*) FROM medicines WHERE expiry_date IS NOT NULL AND expiry_date < ?", (today,)).fetchone()[0]
        daily_sales = db.execute("SELECT COALESCE(SUM(total),0) FROM sales WHERE date(sold_at)=?", (today,)).fetchone()[0]
        revenue = db.execute("SELECT COALESCE(SUM(total),0) FROM sales").fetchone()[0]
        alerts = db.execute("""SELECT * FROM medicines WHERE quantity <= reorder_level
                            OR (expiry_date IS NOT NULL AND expiry_date <= ?)
                            ORDER BY expiry_date LIMIT 8""", (soon,)).fetchall()
        recent_sales = db.execute("""SELECT s.id,s.total,s.sold_at,u.username FROM sales s
                                  JOIN users u ON u.id=s.user_id ORDER BY s.id DESC LIMIT 5""").fetchall()
    return render_template("dashboard.html", total_medicines=total_medicines, low_stock=low_stock,
                           expiring=expiring, expired=expired, daily_sales=daily_sales,
                           revenue=revenue, alerts=alerts, recent_sales=recent_sales, today=today)


@app.route("/medicines", methods=["GET", "POST"])
@login_required
def medicines():
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            category = request.form.get("category", "").strip()
            barcode = request.form.get("barcode", "").strip() or None
            unit_price = float(request.form["unit_price"])
            quantity = int(request.form.get("quantity", 0))
            reorder_level = int(request.form.get("reorder_level", 10))
            expiry_date = request.form.get("expiry_date") or None
            if not name or unit_price < 0 or quantity < 0 or reorder_level < 0:
                raise ValueError("Check the medicine details and numeric values.")
            with get_db() as db:
                db.execute("""INSERT INTO medicines(name,category,barcode,unit_price,quantity,reorder_level,expiry_date)
                              VALUES(?,?,?,?,?,?,?)""",
                           (name, category, barcode, unit_price, quantity, reorder_level, expiry_date))
            flash("Medicine added.", "success")
            return redirect(url_for("medicines"))
        except sqlite3.IntegrityError:
            flash("That barcode is already in use.", "error")
        except (ValueError, KeyError):
            flash("Enter valid medicine details. Prices and quantities cannot be negative.", "error")
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sql = "SELECT * FROM medicines WHERE (name LIKE ? OR category LIKE ? OR COALESCE(barcode,'') LIKE ?)"
    params = [f"%{q}%", f"%{q}%", f"%{q}%"]
    if category:
        sql += " AND category=?"
        params.append(category)
    sql += " ORDER BY name"
    with get_db() as db:
        rows = db.execute(sql, params).fetchall()
        categories = db.execute("SELECT DISTINCT category FROM medicines WHERE category<>'' ORDER BY category").fetchall()
    return render_template("medicines.html", medicines=rows, q=q, category=category, categories=categories)


@app.route("/medicines/<int:medicine_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_medicine(medicine_id):
    with get_db() as db:
        medicine = db.execute("SELECT * FROM medicines WHERE id=?", (medicine_id,)).fetchone()
        if not medicine:
            abort(404)
        if request.method == "POST":
            try:
                values = (request.form["name"].strip(), request.form.get("category", "").strip(),
                          request.form.get("barcode", "").strip() or None, float(request.form["unit_price"]),
                          int(request.form["quantity"]), int(request.form["reorder_level"]),
                          request.form.get("expiry_date") or None, medicine_id)
                if not values[0] or values[3] < 0 or values[4] < 0 or values[5] < 0:
                    raise ValueError()
                db.execute("""UPDATE medicines SET name=?,category=?,barcode=?,unit_price=?,quantity=?,
                              reorder_level=?,expiry_date=? WHERE id=?""", values)
                flash("Medicine updated.", "success")
                return redirect(url_for("medicines"))
            except sqlite3.IntegrityError:
                flash("That barcode is already in use.", "error")
            except (ValueError, KeyError):
                flash("Please enter valid medicine details.", "error")
            medicine = db.execute("SELECT * FROM medicines WHERE id=?", (medicine_id,)).fetchone()
    return render_template("edit_medicine.html", medicine=medicine)


@app.route("/medicines/<int:medicine_id>/delete", methods=["POST"])
@admin_required
def delete_medicine(medicine_id):
    with get_db() as db:
        used = db.execute("SELECT 1 FROM sale_items WHERE medicine_id=? UNION SELECT 1 FROM purchases WHERE medicine_id=? LIMIT 1",
                          (medicine_id, medicine_id)).fetchone()
        if used:
            flash("This medicine is in transaction history and cannot be deleted.", "error")
        else:
            db.execute("DELETE FROM medicines WHERE id=?", (medicine_id,))
            flash("Medicine deleted if it existed.", "success")
    return redirect(url_for("medicines"))


@app.route("/suppliers", methods=["GET", "POST"])
@login_required
def suppliers():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Supplier name is required.", "error")
        else:
            with get_db() as db:
                db.execute("INSERT INTO suppliers(name,phone,email,address) VALUES(?,?,?,?)",
                           (name, request.form.get("phone", "").strip(), request.form.get("email", "").strip(),
                            request.form.get("address", "").strip()))
            flash("Supplier added.", "success")
        return redirect(url_for("suppliers"))
    with get_db() as db:
        rows = db.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    return render_template("suppliers.html", suppliers=rows)


@app.route("/purchases", methods=["GET", "POST"])
@login_required
def purchases():
    with get_db() as db:
        if request.method == "POST":
            try:
                supplier_id = int(request.form["supplier_id"])
                medicine_id = int(request.form["medicine_id"])
                quantity = int(request.form["quantity"])
                unit_cost = float(request.form["unit_cost"])
                if quantity <= 0 or unit_cost < 0:
                    raise ValueError()
                db.execute("INSERT INTO purchases(supplier_id,medicine_id,quantity,unit_cost) VALUES(?,?,?,?)",
                           (supplier_id, medicine_id, quantity, unit_cost))
                db.execute("UPDATE medicines SET quantity=quantity+? WHERE id=?", (quantity, medicine_id))
                flash("Purchase recorded and stock updated.", "success")
                return redirect(url_for("purchases"))
            except (ValueError, KeyError, sqlite3.IntegrityError):
                flash("Please provide valid purchase details.", "error")
        supplier_rows = db.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
        medicine_rows = db.execute("SELECT * FROM medicines ORDER BY name").fetchall()
        history = db.execute("""SELECT p.*,s.name AS supplier_name,m.name AS medicine_name
                              FROM purchases p JOIN suppliers s ON s.id=p.supplier_id
                              JOIN medicines m ON m.id=p.medicine_id ORDER BY p.id DESC LIMIT 50""").fetchall()
    return render_template("purchases.html", suppliers=supplier_rows, medicines=medicine_rows, history=history)


@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    with get_db() as db:
        if request.method == "POST":
            try:
                medicine_id = int(request.form["medicine_id"])
                quantity = int(request.form["quantity"])
                medicine = db.execute("SELECT * FROM medicines WHERE id=?", (medicine_id,)).fetchone()
                if not medicine or quantity <= 0:
                    raise ValueError()
                if medicine["expiry_date"] and medicine["expiry_date"] < date.today().isoformat():
                    flash("Expired medicine cannot be sold.", "error")
                elif medicine["quantity"] < quantity:
                    flash("Not enough stock available.", "error")
                else:
                    total = medicine["unit_price"] * quantity
                    db.execute("INSERT INTO sales(user_id,total) VALUES(?,?)", (session["user_id"], total))
                    sale_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                    db.execute("INSERT INTO sale_items(sale_id,medicine_id,quantity,unit_price,subtotal) VALUES(?,?,?,?,?)",
                               (sale_id, medicine_id, quantity, medicine["unit_price"], total))
                    db.execute("UPDATE medicines SET quantity=quantity-? WHERE id=?", (quantity, medicine_id))
                    flash(f"Sale #{sale_id} completed. Total: {total:.2f}", "success")
                    return redirect(url_for("invoice", sale_id=sale_id))
            except (ValueError, KeyError):
                flash("Select a medicine and enter a valid quantity.", "error")
        medicine_rows = db.execute("""SELECT * FROM medicines WHERE quantity>0 AND
                                   (expiry_date IS NULL OR expiry_date>=?) ORDER BY name""",
                                   (date.today().isoformat(),)).fetchall()
        history = db.execute("""SELECT s.id,s.total,s.sold_at,u.username FROM sales s JOIN users u ON u.id=s.user_id
                             ORDER BY s.id DESC LIMIT 50""").fetchall()
    return render_template("sales.html", medicines=medicine_rows, sales=history)


@app.route("/sales/<int:sale_id>")
@login_required
def invoice(sale_id):
    with get_db() as db:
        sale = db.execute("SELECT s.*,u.username FROM sales s JOIN users u ON u.id=s.user_id WHERE s.id=?",
                          (sale_id,)).fetchone()
        if not sale:
            abort(404)
        items = db.execute("""SELECT si.*,m.name AS medicine_name FROM sale_items si
                           JOIN medicines m ON m.id=si.medicine_id WHERE si.sale_id=?""", (sale_id,)).fetchall()
    return render_template("invoice.html", sale=sale, items=items)


@app.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "employee")
        if not username or len(password) < 8 or role not in ("admin", "employee"):
            flash("Enter a username, a password of at least 8 characters, and a valid role.", "error")
        else:
            try:
                with get_db() as db:
                    db.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                               (username, generate_password_hash(password), role))
                flash("User created.", "success")
            except sqlite3.IntegrityError:
                flash("That username already exists.", "error")
        return redirect(url_for("users"))
    with get_db() as db:
        rows = db.execute("SELECT id,username,role FROM users ORDER BY username").fetchall()
    return render_template("users.html", users=rows)


@app.errorhandler(403)
def forbidden(_):
    return render_template("error.html", code=403, message="You do not have permission to access this page."), 403


@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, message="The requested page was not found."), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
