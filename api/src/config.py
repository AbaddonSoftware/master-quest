import os
from typing import List


def _parse_origins() -> List[str]:
    return [
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "/tmp/flask_session"
    SESSION_PERMANENT = False
    CORS_ALLOWED_ORIGINS = _parse_origins()


class DevConfig(BaseConfig):
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    DEBUG = True

    if not BaseConfig.CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]


class ProdConfig(BaseConfig):
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
    DEBUG = False
