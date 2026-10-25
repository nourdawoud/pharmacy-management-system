"""Integration tests for the working Phase 1 application."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
APP_FILE = ROOT / "app.py"


@pytest.fixture()
def pharmacy(tmp_path, monkeypatch):
    """Load a fresh app instance backed by a temporary SQLite database."""
    monkeypatch.setenv("PHARMACY_DB", str(tmp_path / "pharmacy-test.db"))
    spec = importlib.util.spec_from_file_location("pharmacy_test_app", APP_FILE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True, SECRET_KEY="test-only-secret")
    return module


@pytest.fixture()
def client(pharmacy):
    return pharmacy.app.test_client()


def login(client, username="admin", password="admin123"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_dashboard_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_login_and_dashboard(client):
    response = login(client)
    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Total medicines" in response.data


def test_medicine_create_and_search(client):
    login(client)
    response = client.post(
        "/medicines",
        data={
            "name": "Test Ibuprofen",
            "category": "Pain relief",
            "barcode": "TEST-IBU-1",
            "unit_price": "12.50",
            "quantity": "6",
            "reorder_level": "8",
            "expiry_date": "2099-12-31",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Medicine added" in response.data
    response = client.get("/medicines?q=TEST-IBU-1")
    assert b"Test Ibuprofen" in response.data


def test_purchase_increases_stock_and_sale_creates_invoice(client, pharmacy):
    login(client)
    with pharmacy.get_db() as db:
        medicine = db.execute(
            "SELECT id, quantity FROM medicines WHERE barcode='MED-0001'"
        ).fetchone()
        supplier = db.execute("SELECT id FROM suppliers LIMIT 1").fetchone()
    assert medicine is not None and supplier is not None
    medicine_id, initial_stock = medicine["id"], medicine["quantity"]

    response = client.post(
        "/purchases",
        data={
            "supplier_id": supplier["id"],
            "medicine_id": medicine_id,
            "quantity": "4",
            "unit_cost": "10.00",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with pharmacy.get_db() as db:
        after_purchase = db.execute(
            "SELECT quantity FROM medicines WHERE id=?", (medicine_id,)
        ).fetchone()["quantity"]
    assert after_purchase == initial_stock + 4

    response = client.post(
        "/sales",
        data={"medicine_id": str(medicine_id), "quantity": "2"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invoice #" in response.data
    with pharmacy.get_db() as db:
        after_sale = db.execute(
            "SELECT quantity FROM medicines WHERE id=?", (medicine_id,)
        ).fetchone()["quantity"]
    assert after_sale == initial_stock + 2


def test_expired_medicine_cannot_be_sold(client, pharmacy):
    login(client)
    with pharmacy.get_db() as db:
        db.execute(
            """INSERT INTO medicines
               (name, category, barcode, unit_price, quantity, reorder_level, expiry_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("Expired test medicine", "Test", "EXPIRED-1", 5.0, 9, 1, "2000-01-01"),
        )
        medicine_id = db.execute(
            "SELECT id FROM medicines WHERE barcode='EXPIRED-1'"
        ).fetchone()["id"]

    response = client.post(
        "/sales",
        data={"medicine_id": str(medicine_id), "quantity": "1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Expired medicine cannot be sold" in response.data
    with pharmacy.get_db() as db:
        quantity = db.execute(
            "SELECT quantity FROM medicines WHERE id=?", (medicine_id,)
        ).fetchone()["quantity"]
    assert quantity == 9


def test_employee_cannot_access_user_management(client):
    login(client)
    response = client.post(
        "/users",
        data={"username": "testemployee", "password": "employee-pass-123", "role": "employee"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    client.get("/logout")
    login(client, "testemployee", "employee-pass-123")
    response = client.get("/users")
    assert response.status_code == 403
