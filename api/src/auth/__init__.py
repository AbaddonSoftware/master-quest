from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
from . import routes
from .current_user import load_current_user
