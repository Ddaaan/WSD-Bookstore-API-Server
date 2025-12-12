from datetime import datetime, timedelta
from typing import Optional, Literal

import jwt
from flask import current_app

TokenType = Literal["access", "refresh"]


def create_token(user_id: int, role: str, token_type: TokenType) -> str:
    now = datetime.utcnow()

    if token_type == "access":
        exp = now + timedelta(
            minutes=current_app.config["JWT_ACCESS_EXPIRES_MIN"]
        )
    else:  # "refresh"
        exp = now + timedelta(
            days=current_app.config["JWT_REFRESH_EXPIRES_DAYS"]
        )

    payload = {
        "sub": user_id,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": exp,
    }

    secret = current_app.config["JWT_SECRET"]
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str, expected_type: Optional[TokenType] = None) -> dict:
    secret = current_app.config["JWT_SECRET"]
    payload = jwt.decode(token, secret, algorithms=["HS256"])

    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("잘못된 토큰 타입입니다.")

    return payload
