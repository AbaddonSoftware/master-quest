import logging

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import DevConfig, ProdConfig
from .extensions import db

logging.basicConfig(
    level=logging.ERROR,  # Set log level to capture ERROR and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app_error.log"),  # Logs errors to a file
        logging.StreamHandler(),  # Also logs errors to the console
    ],
)
logger = logging.getLogger(__name__)


def register_blueprints(app: Flask) -> None:
    from .account import account_bp
    from .auth import auth_bp
    from .healthz import bp as health_bp
    from .routes import api_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(api_bp)


def register_request_hook(app: Flask) -> None:
    from .auth import load_current_user

    @app.before_request
    def _attach_user():
        load_current_user()


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = jsonify(
            {
                "error": e.name,
                "status": e.code,
                "message": e.description,
            }
        )
        return response, e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        response = jsonify(
            {
                "error": "Internal Server Error",
                "status": 500,
                "message": "An unexpected error occurred.",
            }
        )
        return response, 500


def create_app():
    app = Flask(__name__)
    cfg = DevConfig
    app.config.from_object(cfg)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    db.init_app(app)
    import src.persistence.models

    register_blueprints(app)
    register_request_hook(app)
    register_error_handlers(app)

    return app
