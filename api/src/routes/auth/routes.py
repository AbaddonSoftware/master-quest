from flask import jsonify, make_response, redirect, request, session
from src.domain.validators import validate_str, validate_user_logged_in

from . import auth_bp as bp
from .service import bootstrap, finish_login, set_profile_service, start_login


@bp.record_once
def _init(s):
    bootstrap(s.app)


@bp.get("/google/login")
def login_google():
    nxt = request.args.get("next") or "/"
    return start_login(next_path=nxt)


@bp.get("/google/callback")
def callback_google():
    try:
        user, nxt = finish_login(request.args)
        session.clear()
        session["public_id"] = str(user.public_id)
        # session.permanent = True
        return redirect(nxt, code=302)
    except Exception as e:
        return jsonify({"error": type(e).__name__, "message": str(e)}), 400


@bp.post("/set-profile")
def set_profile():
    id = validate_user_logged_in()
    data = request.get_json(silent=True) or {}
    field = "display_name"
    display_name = validate_str(data.get(field), field, min_len=3, max_len=30)
    set_profile_service(id, display_name)
    return jsonify({"msg": "ok"}), 200


@bp.post("/logout")
def logout():
    session.pop("public_id", None)
    resp = make_response({"ok": True})
    resp.headers["Cache-Control"] = "no-store"
    return resp
