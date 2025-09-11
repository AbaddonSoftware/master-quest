from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import DevConfig, ProdConfig
from .extensions import db, sessions


def create_app():
    flask_app = Flask(__name__)
    cfg = DevConfig
    flask_app.config.from_object(cfg)

    flask_app.wsgi_app = ProxyFix(
        flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
    )

    db.init_app(flask_app)
    sessions.init_app(flask_app)

    import app.persistence.models

    from .healthz import bp as health_bp

    flask_app.register_blueprint(health_bp)

    from .auth import auth_bp

    flask_app.register_blueprint(auth_bp)
    from .account import account_bp

    flask_app.register_blueprint(account_bp)

    return flask_app
