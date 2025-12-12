from flask import Flask
from .config import get_config
from .extensions import db

def create_app(config_name="dev"):
    app = Flask(__name__)

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    db.init_app(app)

    register_blueprints(app)

    # 개발 단계: 자동 테이블 생성
    with app.app_context():
        from .models import User, Book
        db.create_all()

    return app

def register_blueprints(app):
    from .routes.health import bp as health_bp
    from .routes.users import bp as users_bp
    from .routes.books import bp as books_bp
    from .routes.authors import bp as authors_bp
    from .routes.categories import bp as categories_bp
    from .routes.reviews import bp as reviews_bp

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(authors_bp, url_prefix="/authors")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(reviews_bp, url_prefix="/reviews")