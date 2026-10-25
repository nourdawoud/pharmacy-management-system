from app import create_app, db
from app.models import Medicine


def make_app():
    return create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})


def test_app_starts():
    client = make_app().test_client()
    assert client.get("/").status_code == 200


def test_medicine_can_be_stored():
    app = make_app()
    with app.app_context():
        db.session.add(Medicine(name="Panadol", price=25.0, quantity=5, reorder_level=10))
        db.session.commit()
        med = Medicine.query.first()
        assert med.is_low_stock and not med.is_expired
