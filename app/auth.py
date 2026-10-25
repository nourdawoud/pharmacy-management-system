"""Login, roles and permissions. Owner: Auth, Dashboard & Integration."""
from functools import wraps
from flask import Blueprint, abort
from flask_login import current_user, login_required

bp = Blueprint("auth", __name__, url_prefix="/auth")


def admin_required(view):
    """Decorator: only admins may access the view."""
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@bp.route("/login")
def login():
    return "login - TODO"
