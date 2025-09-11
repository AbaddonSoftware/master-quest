# api/app/auth/service.py
import os
from typing import Mapping, Optional, Tuple

from authlib.integrations.flask_client import OAuth
from flask import session

from .domain_types import Tokens, UserProfile
from .google_client import GoogleClient
from .oauth2_client import OAuth2Client
from .utils import sanitize_next_path

_oauth: Optional[OAuth] = None
_client: Optional[OAuth2Client] = None
_boot = False


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
        picture=info.get("picture"),
        raw=info,
    )

    next_path = session.pop("post_login_next", "/")
    return user, tokens, next_path
