import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 공통 설정
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
    JWT_ACCESS_EXPIRES_MIN = int(os.getenv("JWT_ACCESS_EXPIRES_MIN", "30"))
    JWT_REFRESH_EXPIRES_DAYS = int(os.getenv("JWT_REFRESH_EXPIRES_DAYS", "7"))


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///bookstore.db")
    DEBUG = True


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    DEBUG = False


def get_config(name: str):
    return ProdConfig if name == "prod" else DevConfig
