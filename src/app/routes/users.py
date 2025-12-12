from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from ..auth_utils import jwt_required
from ..error_handlers import ApiError
from ..error_codes import ErrorCodes

bp = Blueprint("users", __name__)


@bp.route("", methods=["POST"])
def create_user():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="email, password, name 은 필수입니다.",
            details={"email": bool(email), "password": bool(password), "name": bool(name)},
        )

    if User.query.filter_by(email=email).first():
        raise ApiError(
            status_code=409,
            code=ErrorCodes.DUPLICATE_RESOURCE,
            message="이미 사용 중인 이메일입니다.",
            details={"email": email},
        )

    user = User(
        email=email,
        name=name,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }), 201


@bp.route("", methods=["GET"])
@jwt_required(role="ADMIN")
def list_users():
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role
        })
    return jsonify(result), 200
