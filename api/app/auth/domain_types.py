from dataclasses import dataclass, field
from typing import Mapping, Any, Optional
from types import MappingProxyType

@dataclass(frozen=True)
class Tokens:
    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    raw: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class UserProfile:
    provider: str
    subject: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

