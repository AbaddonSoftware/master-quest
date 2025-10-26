from typing import Optional
from urllib.parse import urlparse
from flask import g, session

from ....extensions import db
from ....persistence.models import User

def load_current_user():
    public_id = session.get("public_id")
    if not public_id:
        g.user = None
        return
    g.user = db.session.query(User).filter_by(public_id=public_id).one_or_none()

def sanitize_next_path(next_param: Optional[str], default: str = "/") -> str:
    candidate = (next_param or "").strip()
    p = urlparse(candidate)

    return (
        candidate.startswith("/")
        and not candidate.startswith("//")
        and not p.scheme
        and not p.netloc
        and not any(ch in candidate for ch in ("\r", "\n", "\x00"))
        and p.geturl()
    ) or default
