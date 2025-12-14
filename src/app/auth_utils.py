from functools import wraps
from flask import request, g
import jwt

from .jwt_utils import decode_token
from .models import User
from .error_handlers import ApiError
from .error_codes import ErrorCodes


def jwt_required(role: str | None = None):
    """
    Decorator enforcing JWT authentication and optional role-based access control.
    All failures raise ApiError to keep error responses consistent.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            parts = auth_header.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise ApiError(
                    status_code=401,
                    code=ErrorCodes.UNAUTHORIZED,
                    message="Authorization header must follow 'Bearer <token>'.",
                )

            token = parts[1]

            try:
                payload = decode_token(token, expected_type="access")
            except jwt.ExpiredSignatureError:
                raise ApiError(
                    status_code=401,
                    code=ErrorCodes.TOKEN_EXPIRED,
                    message="Access token has expired. Please login again.",
                )
            except jwt.InvalidTokenError:
                raise ApiError(
                    status_code=401,
                    code=ErrorCodes.UNAUTHORIZED,
                    message="Invalid access token.",
                )

            user_id_claim = payload.get("sub")
            user_role = payload.get("role")

            try:
                user_id = int(user_id_claim)
            except (TypeError, ValueError):
                raise ApiError(
                    status_code=401,
                    code=ErrorCodes.UNAUTHORIZED,
                    message="Invalid access token.",
                )

            user = User.query.get(user_id)
            if not user:
                raise ApiError(
                    status_code=401,
                    code=ErrorCodes.USER_NOT_FOUND,
                    message="User associated with this token could not be found.",
                )

            g.current_user = user

            if role and user_role != role:
                raise ApiError(
                    status_code=403,
                    code=ErrorCodes.FORBIDDEN,
                    message="You do not have permission to perform this action.",
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
