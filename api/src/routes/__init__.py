from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")


from .boards import board_bp
from .cards import card_bp
from .invites import invite_bp
from .rooms import room_bp  # noqa: E402,F401

api_bp.register_blueprint(room_bp)
api_bp.register_blueprint(board_bp)
api_bp.register_blueprint(card_bp)
api_bp.register_blueprint(invite_bp)
