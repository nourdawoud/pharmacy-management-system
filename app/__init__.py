from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pharmacy.db"
    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)

    # One blueprint per module -> each member works in their own file,
    # which keeps merge conflicts to a minimum.
    from .auth import bp as auth_bp
    from .medicines import bp as medicines_bp
    from .inventory import bp as inventory_bp
    from .sales import bp as sales_bp
    from .purchases import bp as purchases_bp
    from .dashboard import bp as dashboard_bp

    for bp in (auth_bp, medicines_bp, inventory_bp, sales_bp, purchases_bp, dashboard_bp):
        app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
    return app
