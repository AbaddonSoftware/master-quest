from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.get("/api/ping")
    def ping():
        return "pong"
        

    return app
