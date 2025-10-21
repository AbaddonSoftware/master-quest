import os
from datetime import datetime, timezone
from typing import Mapping, Optional, Tuple

from authlib.integrations.flask_client import OAuth
from flask import session
from ...extensions import db
from ...persistence.models import Identity, User

from .domain_types import UserProfile
from .google_client import GoogleClient
from .oauth2_client import OAuth2Client
from .utils import sanitize_next_path

_oauth: Optional[OAuth] = None
_client: Optional[OAuth2Client] = None
_boot = False


def _upsert_user_identity(user: UserProfile) -> User:
    """
    Ensure (provider, subject) exists; create User if first-time.
    """
    ident = (
        db.session.query(Identity)
        .filter(Identity.provider == user.provider, Identity.subject == user.subject)
        .first()
    )
    if ident:
        if user.email and ident.user.email is None:
            ident.user.email = user.email
        if user.name and ident.user.name is None:
            ident.user.name = user.name
        db.session.commit()
        return ident.user

    user_data = User(
        email=user.email, name=user.name, last_login_at=datetime.now(timezone.utc)
    )
    db.session.add(user_data)
    db.session.flush()

    identity_info = Identity(
        user_id=user_data.id,
        provider=user.provider,
        subject=user.subject,
    )
    db.session.add(identity_info)
    db.session.commit()
    return user_data


def _base() -> str:
    return (os.environ.get("OAUTH_REDIRECT_BASE") or "http://localhost:8080").rstrip(
        "/"
    )


def bootstrap(app) -> None:
    global _oauth, _client, _boot
    if _boot:
        return
    _oauth = OAuth(app)
    _client = GoogleClient(_oauth)  # Google only for now
    _boot = True


def start_login(*, next_path: str = "/"):
    assert _client is not None, "call bootstrap(app) first"
    session["post_login_next"] = sanitize_next_path(next_path, "/")
    redirect_uri = f"{_base()}/auth/google/callback"
    return _client.authorize_url(redirect_uri=redirect_uri)


def finish_login(params: Mapping[str, str]) -> Tuple[UserProfile, str]:
    assert _oauth is not None, "call bootstrap(app) first"
    _client.exchange_code()
    profile: UserProfile = _client.fetch_userinfo()
    user = _upsert_user_identity(profile)
    next_path = session.pop("post_login_next", "/")
    return user, next_path


def set_profile_service(user_id: int, display_name: str):
    user = db.session.get(User, user_id)
    user.display_name = display_name
    db.session.commit()
