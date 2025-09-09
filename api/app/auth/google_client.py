import os
from flask.wrappers import Response
from typing import Optional
from authlib.integrations.flask_client import OAuth
from .oauth2_client import OAuth2Client
from .domain_types import Tokens, UserProfile

class GoogleClient(OAuth2Client):
    name = "google"

    def __init__(self, oauth: OAuth):
        self.client = oauth.register(
            name=self.name,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_id=os.environ["GOOGLE_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            client_kwargs={"scope": "openid email profile"},
        )

    def authorize_url(self, *, redirect_uri: str) -> Response:
        return self.client.authorize_redirect(redirect_uri)

    def exchange_code(self, *, code: str, redirect_uri: str, code_verifier: Optional[str]) -> Tokens:
        token = self.client.fetch_access_token(
            code=code, redirect_uri=redirect_uri, code_verifier=code_verifier
        )
        return Tokens(
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            id_token=token.get("id_token"),
            token_type=token.get("token_type"),
            expires_in=token.get("expires_in"),
            raw=token,
        )

    def fetch_user(self, tokens: Tokens) -> UserProfile:
        info = self.client.userinfo(token=tokens.raw)
        return UserProfile(
            provider=self.name,
            subject=info.get("sub", ""),
            email=info.get("email"),
            name=info.get("name") or info.get("given_name"),
            picture=info.get("picture"),
            raw=info,
        )

    # Optional extras (Google supports both) They exist here for completeness but are not used 
    # in the current app implementation as we only use this for sign-in.
    def refresh(self, refresh_token: str) -> Tokens:
        token = self.client.refresh_token(self.client.access_token_url, refresh_token=refresh_token)
        return Tokens(
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token") or refresh_token,
            id_token=token.get("id_token"),
            token_type=token.get("token_type"),
            expires_in=token.get("expires_in"),
            raw=token,
        )

    def revoke(self, token: str, token_type_hint: str = "access_token") -> None:
        self.client.revoke_token("https://oauth2.googleapis.com/revoke", token, token_type_hint=token_type_hint)
