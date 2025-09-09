from flask import Blueprint, jsonify, redirect, request, session, make_response
from .service import bootstrap, start_login, finish_login
from .errors import AuthError
from . import auth_bp as bp

@bp.record_once
def _init(s): bootstrap(s.app)

@bp.get("/google/login")
def login_google():
    nxt = request.args.get("next") or "/"
    return start_login(next_path=nxt)

@bp.get("/google/callback")
def callback_google():
    try:
        user, _tokens, nxt = finish_login(request.args)
        session["user"] = {
            "provider": user.provider,
            "sub": user.subject,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        }
        return redirect(nxt, code=302)
    except Exception as e:
        return jsonify({"error": type(e).__name__, "message": str(e)}), 400

# @bp.get("/me")
# def whoami():
#     u = session.get("user")
#     resp = make_response({"authenticated": bool(u), "user": u}, 200 if u else 401)
#     resp.headers["Cache-Control"] = "no-store"
#     return resp

@bp.post("/logout")
def logout():
    session.pop("user", None)
    resp = make_response({"ok": True})
    resp.headers["Cache-Control"] = "no-store"
    return resp

