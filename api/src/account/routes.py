from flask import g, make_response

from . import account_bp as bp


@bp.get("/")
@bp.get("/me")
def whoami():
    u = getattr(g, "user", None)
    resp = make_response(
        {"authenticated": bool(u), "user": u.name if u else None}, 200 if u else 401
    )
    resp.headers["Cache-Control"] = "no-store"
    return resp
