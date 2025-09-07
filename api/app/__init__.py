from flask import Flask

from .config import DevConfig, ProdConfig
from .extensions import db, sessions
from .routes import register_routes

def create_app():
    flask_app = Flask(__name__)
    
    cfg = DevConfig
    flask_app.config.from_object(cfg)

    db.init_app(flask_app)
    sessions.init_app(flask_app)

    import app.persistence.models  

    @flask_app.get("/api/ping")
    def ping():
        return "pong"
        

    return flask_app
