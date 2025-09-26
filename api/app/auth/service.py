import os
from typing import Mapping, Optional, Tuple

from app.extensions import db
from app.persistence.models import Identity, User
from authlib.integrations.flask_client import OAuth
from flask import session

from .domain_types import Tokens, UserProfile
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

    u = User(
        email=user.email,
        name=user.name,
    )
    db.session.add(u)
    db.session.flush()

    i = Identity(
        user_id=u.id,
        provider=user.provider,
        subject=user.subject,
        email_at_auth=user.email,
        #    profile_json=user.raw,
    )
    db.session.add(i)
    db.session.commit()
    return u


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


def finish_login(params: Mapping[str, str]) -> Tuple[UserProfile, Tokens, str]:
    assert _oauth is not None, "call bootstrap(app) first"
    oauth = _oauth

    token = oauth.google.authorize_access_token()

    tokens = Tokens(
        access_token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        id_token=token.get("id_token"),
        token_type=token.get("token_type"),
        expires_in=token.get("expires_in"),
        raw=token,
    )

    info = oauth.google.userinfo()
    user = UserProfile(
        provider="google",
        subject=info.get("sub", ""),
        email=info.get("email"),
        name=info.get("name") or info.get("given_name"),
        raw=info,
    )
    _upsert_user_identity(user)
    next_path = session.pop("post_login_next", "/")
    return user, tokens, next_path
