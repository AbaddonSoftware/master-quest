from __future__ import annotations

from app.extensions import db
from app.persistence.models import Identity
from flask import g, session


def load_current_user():
    """Attach g.user if session['user'] exists; keep it O(1) with Identity -> User join."""
    g.user = None
    s = session.get("user")
    if not s:
        return
    provider = s.get("provider")
    sub = s.get("sub")
    if not provider or not sub:
        return
    # Look up by Identity (stable per-provider subject)
    ident = (
        db.session.query(Identity)
        .filter(Identity.provider == provider, Identity.subject == sub)
        .first()
    )
    if ident:
        g.user = ident.user
