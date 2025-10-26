from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
from . import routes
from .utils.utils import load_current_user, sanitize_next_path
from .types.domain_types import Tokens, UserProfile