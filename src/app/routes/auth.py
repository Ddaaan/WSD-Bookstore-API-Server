from flask import Blueprint, request, jsonify
from ..models import User
from ..jwt_utils import create_token, decode_token
from ..error_handlers import ApiError
from ..error_codes import ErrorCodes
import jwt

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="email, password 는 필수입니다.",
            details={"email": bool(email), "password": bool(password)},
        )

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ApiError(
            status_code=401,
            code=ErrorCodes.UNAUTHORIZED,
            message="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    access_token = create_token(user.id, user.role, "access")
    refresh_token = create_token(user.id, user.role, "refresh")

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }), 200


@bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json() or {}
    token = data.get("refresh_token")

    if not token:
        raise ApiError(
            status_code=400,
            code=ErrorCodes.VALIDATION_FAILED,
            message="refresh_token 필드는 필수입니다.",
        )

    try:
        payload = decode_token(token, expected_type="refresh")
    except jwt.ExpiredSignatureError:
        raise ApiError(
            status_code=401,
            code=ErrorCodes.TOKEN_EXPIRED,
            message="Refresh 토큰이 만료되었습니다. 다시 로그인해주세요.",
        )
    except jwt.InvalidTokenError:
        raise ApiError(
            status_code=401,
            code=ErrorCodes.UNAUTHORIZED,
            message="유효하지 않은 Refresh 토큰입니다.",
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    user = User.query.get(user_id)
    if not user:
        raise ApiError(
            status_code=401,
            code=ErrorCodes.USER_NOT_FOUND,
            message="사용자를 찾을 수 없습니다.",
        )

    new_access = create_token(user.id, role, "access")
    new_refresh = create_token(user.id, role, "refresh")

    return jsonify({
        "access_token": new_access,
        "refresh_token": new_refresh
    }), 200
