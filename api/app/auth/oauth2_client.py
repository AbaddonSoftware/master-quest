from typing import Optional, Protocol

from flask.wrappers import Response

from .domain_types import Tokens, UserProfile


class OAuth2Client(Protocol):
    """Abstract OAuth2 client interface (provider-agnostic)."""

    name: str

    def authorize_url(self, *, redirect_uri: str) -> Response: ...

    def exchange_code(
        self, *, code: str, redirect_uri: str, code_verifier: Optional[str]
    ) -> Tokens: ...

    def fetch_user(self, tokens: Tokens) -> UserProfile: ...

    # Optional extensions (Not all providers support these) They won't be used while solely using for sign-in.
    def refresh(self, refresh_token: str) -> Tokens: ...
    def revoke(self, token: str, token_type_hint: str = "access_token") -> None: ...
