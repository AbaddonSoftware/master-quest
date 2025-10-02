import os
from typing import Mapping, Optional

from authlib.integrations.flask_client import OAuth
from flask.wrappers import Response

from .domain_types import Tokens, UserProfile


class GoogleClient:
    name = "google"

    @staticmethod
    def _get_best_alias(info: Mapping[str, object]) -> str:
        return info.get("name") or info.get("given_name") or "Guest" 


    def __init__(self, oauth: OAuth):
        self.client = oauth.register(
            name=self.name,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            client_kwargs={
                "scope": "openid email profile",
                "code_challenge_method": "S256",
            },
        )

    def authorize_url(
        self, *, redirect_uri: str, state: Optional[str] = None
    ) -> Response:
        if state:
            return self.client.authorize_redirect(redirect_uri, state=state)
        return self.client.authorize_redirect(redirect_uri)

    def exchange_code(
        self) -> Tokens:
        token = self.client.authorize_access_token()
        return Tokens(
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            id_token=token.get("id_token"),
            token_type=token.get("token_type"),
            expires_in=token.get("expires_in"),
            raw=token,
        )

    def fetch_userinfo(self) -> UserProfile:
        info = self.client.userinfo()
        return UserProfile(
            provider=self.name,
            subject=info.get("sub"),
            email=info.get("email"),
            name=self._get_best_alias(info),
            raw=info,
        )
