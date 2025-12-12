from datetime import datetime
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

from .error_codes import ErrorCodes


class ApiError(Exception):
    """
    서비스 내부에서 명시적으로 발생시키는 예외.
    표준 에러 응답 포맷으로 변환된다.
    """

    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def _make_error_response(status_code: int, code: str, message: str, details: dict | None = None):
    return jsonify({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "path": request.path,
        "status": status_code,
        "code": code,
        "message": message,
        "details": details or {},
    }), status_code


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return _make_error_response(
            status_code=err.status_code,
            code=err.code,
            message=err.message,
            details=err.details,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        status_code = err.code or 500
        code = ErrorCodes.BAD_REQUEST if status_code < 500 else ErrorCodes.INTERNAL_SERVER_ERROR
        return _make_error_response(
            status_code=status_code,
            code=code,
            message=str(err.description),
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(err: Exception):
        # 디버깅용 로그는 서버 콘솔에 출력
        app.logger.exception("Unhandled exception occurred: %s", err)

        return _make_error_response(
            status_code=500,
            code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message="서버 내부 오류가 발생했습니다.",
        )
