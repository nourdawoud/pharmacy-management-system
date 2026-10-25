"""Sales & billing: transactions, totals, invoices. Owner: Sales & Billing."""
from flask import Blueprint

bp = Blueprint("sales", __name__, url_prefix="/sales")


@bp.route("/")
def index():
    return "sales module - TODO"
