from flask import Blueprint

def register_routes(app):
    api = Blueprint("api", __name__)
    app.register_blueprint(api, url_prefix="/api")
