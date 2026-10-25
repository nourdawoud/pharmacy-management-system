"""Focused regression tests for authentication and dashboard behavior."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
APP_FILE = ROOT / "app.py"


@pytest.fixture()
def pharmacy(tmp_path, monkeypatch):
    """Load the application with an isolated SQLite database."""
    monkeypatch.setenv("PHARMACY_DB", str(tmp_path / "auth-dashboard-test.db"))
    spec = importlib.util.spec_from_file_location("auth_dashboard_test_app", APP_FILE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True, SECRET_KEY="test-only-secret")
    return module


@pytest.fixture()
def client(pharmacy):
    return pharmacy.app.test_client()


def sign_in(client, username="admin", password="admin123"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_invalid_credentials_do_not_log_user_in(client):
    response = sign_in(client, username="admin", password="wrong-password")

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data
    protected = client.get("/")
    assert protected.status_code == 302
    assert "/login" in protected.headers["Location"]


def test_logout_requires_post_and_clears_session(client):
    sign_in(client)

    # A simple GET request must not change authentication state.
    assert client.get("/logout").status_code == 405
    assert client.get("/").status_code == 200

    response = client.post("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out" in response.data
    protected = client.get("/")
    assert protected.status_code == 302
    assert "/login" in protected.headers["Location"]


def test_dashboard_shows_correct_initial_inventory_counts(client):
    sign_in(client)
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<span>Total medicines</span><strong>3</strong>" in html
    assert "<span>Low stock</span><strong>2</strong>" in html
    assert "<span>Nearing expiry</span><strong>1</strong>" in html
    assert "<span>Expired</span><strong>0</strong>" in html
    assert "<span>Today's sales</span><strong>0.00</strong>" in html
    assert "<span>Total revenue</span><strong>0.00</strong>" in html


def test_employee_cannot_open_admin_user_management(client):
    sign_in(client)
    create_response = client.post(
        "/users",
        data={
            "username": "dashboard-employee",
            "password": "employee-password",
            "role": "employee",
        },
        follow_redirects=True,
    )
    assert create_response.status_code == 200

    client.post("/logout")
    sign_in(client, "dashboard-employee", "employee-password")
    assert client.get("/users").status_code == 403
