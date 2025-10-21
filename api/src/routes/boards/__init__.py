from flask import Blueprint

board_bp = Blueprint(
    "boards", __name__, url_prefix="/rooms/<string:room_public_id>/boards"
)

from . import routes  # noqa: E402,F401
