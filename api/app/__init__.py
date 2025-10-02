from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from app.auth import load_current_user

from .config import DevConfig, ProdConfig
from .extensions import db


def register_blueprints(app: Flask) -> None:
    from .healthz import bp as health_bp
    from .auth import auth_bp
    from .account import account_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)


def register_request_hook(app: Flask) -> None:
    @app.before_request
    def _attach_user():
        load_current_user()


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def _http_error(e):
        return (
            jsonify({"error": e.name, "status": e.code, "message": e.description}),
            e.code,
        )


def create_app():
    flask_app = Flask(__name__)
    cfg = DevConfig
    flask_app.config.from_object(cfg)

    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    db.init_app(flask_app)
    import app.persistence.models
    register_blueprints(flask_app)
    register_request_hook(flask_app)
    register_error_handlers(flask_app)

    return flask_app
