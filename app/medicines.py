"""Medicine management: CRUD, search, filtering. Owner: Database & Medicine."""
from flask import Blueprint

bp = Blueprint("medicines", __name__, url_prefix="/medicines")


@bp.route("/")
def index():
    return "medicines module - TODO"
