from flask import Blueprint, jsonify, make_response, redirect, request, session

from . import auth_bp as bp
from .errors import AuthError
from .service import bootstrap, finish_login, start_login


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
        user, _tokens, nxt = finish_login(request.args)
        session["user"] = {
            "provider": user.provider,
            "sub": user.subject,
            "email": user.email,
            "name": user.name,
        }
        return redirect(nxt, code=302)
    except Exception as e:
        return jsonify({"error": type(e).__name__, "message": str(e)}), 400


@bp.post("/logout")
def logout():
    session.pop("user", None)
    resp = make_response({"ok": True})
    resp.headers["Cache-Control"] = "no-store"
    return resp
