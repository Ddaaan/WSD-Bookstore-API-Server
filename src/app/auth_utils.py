from functools import wraps
from flask import request, jsonify, g
import jwt

from .jwt_utils import decode_token
from .models import User


def jwt_required(role: str | None = None):
    """
    @jwt_required()           → 로그인된 사용자만 접근 가능
    @jwt_required("ADMIN")    → 관리자만 접근 가능
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            parts = auth_header.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"message": "Authorization 헤더에 Bearer 토큰이 필요합니다."}), 401

            token = parts[1]

            try:
                payload = decode_token(token, expected_type="access")
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Access 토큰이 만료되었습니다."}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "유효하지 않은 Access 토큰입니다."}), 401

            user_id = payload.get("sub")
            user_role = payload.get("role")

            user = User.query.get(user_id)
            if not user:
                return jsonify({"message": "사용자를 찾을 수 없습니다."}), 401

            # Flask 전역 컨텍스트에 현재 사용자 저장
            g.current_user = user

            # 역할 체크
            if role and user_role != role:
                return jsonify({"message": "해당 리소스에 접근할 권한이 없습니다."}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
