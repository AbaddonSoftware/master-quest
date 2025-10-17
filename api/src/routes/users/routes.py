from flask import abort, g, jsonify

from . import account_bp as bp


@bp.get("/me")
def me():
    if not g.user:
        abort(401)
    return jsonify(
        {
            "id": g.user.public_id,
            "email": g.user.email,
            "display_name": g.user.preferred_name,
        }
    )
    # u = getattr(g, "user", None)
    # resp = make_response(
    #     {"authenticated": bool(u), "user": u.name if u else None}, 200 if u else 401
    # )
    # resp.headers["Cache-Control"] = "no-store"
    # return resp
