from flask import Blueprint

invite_bp = Blueprint("invites", __name__, url_prefix="/invites")

from . import routes  # noqa: E402,F401
