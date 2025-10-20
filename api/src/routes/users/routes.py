from flask import abort, g, jsonify

from . import account_bp as bp


@bp.get("/me")
def me():
    if not g.user:
        abort(401, "What are you doing here? Who knows. Perhaps you forgot to log in?")
    return jsonify(
        {
            "id": g.user.public_id,
            "email": g.user.email,
            "display_name": g.user.display_name,
        }
    )
