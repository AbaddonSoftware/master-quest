from typing import Optional
from urllib.parse import urlparse


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
