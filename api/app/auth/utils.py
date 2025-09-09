import base64, hashlib, secrets
from typing import Optional
from urllib.parse import urlparse

def sanitize_next_path(next_param: Optional[str], default: str = "/") -> str:
    candidate = (next_param or "").strip()
    parsed_url = urlparse(candidate)

    starts_with_single_slash = parsed_url.path.startswith("/")
    does_not_start_with_doubleslash = not parsed_url.path.startswith("//")
    has_no_scheme = not parsed_url.scheme
    has_no_netloc = not parsed_url.netloc
    contains_no_control_chars = all(
        character not in candidate for character in ("\r", "\n", "\x00")
    )

    if (
        starts_with_single_slash
        and does_not_start_with_doubleslash
        and has_no_scheme
        and has_no_netloc
        and contains_no_control_chars
    ):
        return parsed_url.geturl() or default
    return default

def code_verifier() -> str:
    v = secrets.token_urlsafe(48)
    return v

def code_challenge(verifier: str) -> str:
    d = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode("ascii")

def generate_state() -> str:
    return secrets.token_urlsafe(32)
