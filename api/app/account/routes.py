from flask import session, make_response
from . import account_bp as bp

@bp.get("/me")
def whoami():
    u = session.get("user")
    resp = make_response({"authenticated": bool(u), "user": u}, 200 if u else 401)
    resp.headers["Cache-Control"] = "no-store"
    return resp