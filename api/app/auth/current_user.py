from __future__ import annotations

from app.extensions import db
from app.persistence.models import User
from flask import g, session


def load_current_user():
    public_id = session.get("public_id")
    if not public_id:
        g.user = None
    g.user = db.session.query(User).filter_by(public_id=public_id).one_or_none()
