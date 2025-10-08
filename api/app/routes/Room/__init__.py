from flask import Blueprint
room_bp = Blueprint("room", __name__, url_prefix="/room")

from . import routes  # noqa: E402,F401

