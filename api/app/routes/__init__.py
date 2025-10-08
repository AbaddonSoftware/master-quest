from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")


from .Room import room_bp  # noqa: E402,F401

api_bp.register_blueprint(room_bp)
