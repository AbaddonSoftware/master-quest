from datetime import datetime

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)
START_TIME = datetime.now()


@bp.get("/healthz")
def ping():
    uptime = str(datetime.now() - START_TIME).split(".")[0]
    return jsonify(
        {
            "status": "ok",
            "message": "The void beckons... but at least this is working.",
            "uptime": f"and it has done so for {uptime}",
        },
        200,
    )
