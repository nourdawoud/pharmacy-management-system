"""Suppliers and purchases. Owner: Supplier & Purchase."""
from flask import Blueprint

bp = Blueprint("purchases", __name__, url_prefix="/purchases")


@bp.route("/")
def index():
    return "purchases module - TODO"
