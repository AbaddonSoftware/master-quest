from flask import Blueprint

card_bp = Blueprint(
    "cards",
    __name__,
    url_prefix="/rooms/<string:room_public_id>/boards/<string:board_public_id>/columns/<int:column_id>/cards",
)

from . import routes  # noqa: E402,F401
