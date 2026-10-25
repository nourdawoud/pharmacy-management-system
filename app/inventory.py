"""Inventory & expiry: stock levels, low-stock and expiry alerts. Owner: Inventory & Expiry."""
from flask import Blueprint

bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@bp.route("/")
def index():
    return "inventory module - TODO"
