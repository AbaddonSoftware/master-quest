from flask import Blueprint

bp = Blueprint("api", __name__)


@bp.get("/healthz")
def ping():
    return {
        "ok": True,
        "message": "The void beckons… but at least this is working.",
    }
