from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.route("", methods=["GET"])
def health_check():
    return jsonify({
        "status": "OK",
        "service": "bookstore-api"
    }), 200
