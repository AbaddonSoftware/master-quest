from flask import Blueprint

board_bp = Blueprint("board", __name__, url_prefix="/boards")

from . import routes  # noqa: E402,F401
