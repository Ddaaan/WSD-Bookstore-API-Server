import json
from pathlib import Path

from flask import Blueprint, current_app, jsonify
from flask_swagger_ui import get_swaggerui_blueprint


swagger_spec_bp = Blueprint("swagger_spec", __name__)


def _default_spec_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "docs" / "swagger.json"


@swagger_spec_bp.route("/swagger.json")
def swagger_json():
    spec_path = Path(current_app.config.get("SWAGGER_SPEC_PATH", _default_spec_path()))

    if not spec_path.exists():
        return jsonify({"error": "Swagger spec not found.", "path": str(spec_path)}), 404

    with spec_path.open(encoding="utf-8") as fp:
        data = json.load(fp)
    return jsonify(data)


def register_swagger(app):
    """
    Mounts swagger.json and Swagger UI (/docs by default) onto the Flask app.
    """

    swagger_url = app.config.get("SWAGGER_UI_URL", "/docs")
    api_url = app.config.get("SWAGGER_SPEC_URL", "/swagger.json")

    swaggerui_bp = get_swaggerui_blueprint(
        base_url=swagger_url,
        api_url=api_url,
        config={"app_name": "WSD Bookstore API"},
    )

    app.register_blueprint(swagger_spec_bp)
    app.register_blueprint(swaggerui_bp, url_prefix=swagger_url)
