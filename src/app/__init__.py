from time import perf_counter

from flask import Flask, g, request
from dotenv import load_dotenv

from .config import get_config
from .extensions import db
from .error_handlers import register_error_handlers
from .swagger import register_swagger


def create_app(config_name="dev"):
    load_dotenv()
    app = Flask(__name__)

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    db.init_app(app)

    register_blueprints(app)
    register_error_handlers(app)
    register_swagger(app)
    register_request_logging(app)

    # 개발 단계: 자동 테이블 생성
    with app.app_context():
        from .models import User, Book

        db.create_all()

    return app


def register_request_logging(app):
    @app.before_request
    def _start_timer():
        g._request_started_at = perf_counter()

    @app.after_request
    def _log_response(response):
        start_time = getattr(g, "_request_started_at", None)
        duration_ms = 0.0
        if start_time is not None:
            duration_ms = (perf_counter() - start_time) * 1000

        app.logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response


def register_blueprints(app):
    from .routes.health import bp as health_bp
    from .routes.users import bp as users_bp
    from .routes.books import bp as books_bp
    from .routes.authors import bp as authors_bp
    from .routes.categories import bp as categories_bp
    from .routes.reviews import bp as reviews_bp
    from .routes.review_likes import bp as review_likes_bp
    from .routes.comments import bp as comments_bp
    from .routes.wishlists import bp as wishlists_bp
    from .routes.cart import bp as cart_bp
    from .routes.orders import bp as orders_bp
    from .routes.auth import bp as auth_bp

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(authors_bp, url_prefix="/authors")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(reviews_bp, url_prefix="/reviews")
    app.register_blueprint(review_likes_bp, url_prefix="/reviews")
    app.register_blueprint(comments_bp)
    app.register_blueprint(wishlists_bp, url_prefix="/wishlists")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(auth_bp, url_prefix="/auth")
