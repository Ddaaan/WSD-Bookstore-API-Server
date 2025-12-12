from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from ..jwt_utils import create_token, decode_token
import jwt

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    """
    이메일/비밀번호로 로그인 → Access / Refresh 토큰 발급
    요청 예시:
    {
      "email": "user1@example.com",
      "password": "test1234"
    }
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email, password 는 필수입니다."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

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
    """
    Refresh 토큰으로 새로운 Access 토큰 재발급
    요청 예시:
    {
      "refresh_token": "..."
    }
    """
    data = request.get_json() or {}
    token = data.get("refresh_token")

    if not token:
        return jsonify({"message": "refresh_token 필드는 필수입니다."}), 400

    try:
        payload = decode_token(token, expected_type="refresh")
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh 토큰이 만료되었습니다. 다시 로그인해주세요."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 Refresh 토큰입니다."}), 401

    user_id = payload.get("sub")
    role = payload.get("role")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 401

    new_access = create_token(user.id, role, "access")
    new_refresh = create_token(user.id, role, "refresh")

    return jsonify({
        "access_token": new_access,
        "refresh_token": new_refresh
    }), 200
