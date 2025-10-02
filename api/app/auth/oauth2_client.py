from typing import Mapping, Optional, Protocol

from flask.wrappers import Response

from .domain_types import Tokens, UserProfile


class OAuth2Client(Protocol):
    name: str

    def authorize_url(
        self, *, redirect_uri: str, state: Optional[str] = None
    ) -> Response: ...
    def exchange_code(
        self, *, code: str, redirect_uri: str, code_verifier: Optional[str]
    ) -> Tokens: ...
    def fetch_userinfo(self, token: Mapping[str, object]) -> UserProfile: ...
