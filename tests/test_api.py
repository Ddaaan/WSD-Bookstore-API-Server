import os
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.app import create_app  # noqa: E402
from src.app.extensions import db  # noqa: E402
from src.app.models import User, Category, Author, Book  # noqa: E402


def seed_data():
    admin = User(email="admin@example.com", name="Admin", role="ADMIN")
    admin.set_password("Admin123!")
    user = User(email="user1@example.com", name="User1", role="USER")
    user.set_password("User1123!")

    category = Category(name="Tech", slug="tech")
    author = Author(name="Seed Author", bio="Seeder")
    db.session.add_all([admin, user, category, author])
    db.session.commit()

    book = Book(
        title="Seed Book",
        description="Base book",
        price=Decimal("15000"),
        stock_cnt=50,
        status="ACTIVE",
        author_id=author.id,
        category_id=category.id,
    )
    db.session.add(book)
    db.session.commit()

    return {
        "admin_email": admin.email,
        "admin_password": "Admin123!",
        "user_email": user.email,
        "user_password": "User1123!",
        "user_id": user.id,
        "category_id": category.id,
        "author_id": author.id,
        "book_id": book.id,
    }


@pytest.fixture
def client(tmp_path):
    os.environ["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path/'test.db'}"
    os.environ["JWT_SECRET"] = "test-secret"
    app = create_app("dev")
    app.config.update({"TESTING": True})
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.config["SEED_IDS"] = seed_data()
    with app.test_client() as client:
        yield client


def login(client, email, password):
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.get_json()


def admin_creds(client):
    cfg = client.application.config["SEED_IDS"]
    return cfg["admin_email"], cfg["admin_password"]


def user_creds(client):
    cfg = client.application.config["SEED_IDS"]
    return cfg["user_email"], cfg["user_password"]


def get_book_id(client):
    return client.application.config["SEED_IDS"]["book_id"]


def get_user_id(client):
    return client.application.config["SEED_IDS"]["user_id"]


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "OK"


def test_admin_login_success(client):
    email, pwd = admin_creds(client)
    resp = client.post("/auth/login", json={"email": email, "password": pwd})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_invalid_password(client):
    email, _ = admin_creds(client)
    resp = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert resp.status_code == 401


def test_refresh_missing_token(client):
    resp = client.post("/auth/refresh", json={})
    assert resp.status_code == 400


def test_create_user_success(client):
    payload = {"email": "new@example.com", "password": "Secret123!", "name": "New"}
    resp = client.post("/users", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["email"] == payload["email"]


def test_create_user_duplicate_email(client):
    email, _ = admin_creds(client)
    resp = client.post("/users", json={"email": email, "password": "Secret123!", "name": "Dup"})
    assert resp.status_code == 409


def test_list_users_requires_auth(client):
    resp = client.get("/users")
    assert resp.status_code == 401


def test_list_users_admin_success(client):
    email, pwd = admin_creds(client)
    token = login(client, email, pwd)["access_token"]
    resp = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_create_book_requires_auth(client):
    cfg = client.application.config["SEED_IDS"]
    resp = client.post(
        "/books",
        json={
            "title": "NoAuth",
            "price": 10000,
            "category_id": cfg["category_id"],
            "author_id": cfg["author_id"],
        },
    )
    assert resp.status_code == 401


def test_create_book_success(client):
    cfg = client.application.config["SEED_IDS"]
    email, pwd = admin_creds(client)
    token = login(client, email, pwd)["access_token"]
    resp = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Brand New",
            "price": 22000,
            "category_id": cfg["category_id"],
            "author_id": cfg["author_id"],
            "stock_cnt": 5,
            "status": "ACTIVE",
        },
    )
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Brand New"


def test_list_books_keyword_filter(client):
    resp = client.get("/books", query_string={"keyword": "Seed"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["totalElements"] >= 1


def test_get_book_not_found(client):
    resp = client.get("/books/99999")
    assert resp.status_code == 404


def test_update_book_success(client):
    email, pwd = admin_creds(client)
    token = login(client, email, pwd)["access_token"]
    book_id = get_book_id(client)
    resp = client.put(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Seed Book Updated"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Seed Book Updated"


def test_delete_book_success(client):
    cfg = client.application.config["SEED_IDS"]
    email, pwd = admin_creds(client)
    token = login(client, email, pwd)["access_token"]
    resp = client.post(
        "/books",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "ToDelete",
            "price": 11000,
            "category_id": cfg["category_id"],
            "author_id": cfg["author_id"],
        },
    )
    book_id = resp.get_json()["id"]
    delete_resp = client.delete(f"/books/{book_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete_resp.status_code == 200


def test_create_review_missing_fields(client):
    resp = client.post("/reviews", json={"book_id": get_book_id(client)})
    assert resp.status_code == 400


def test_create_review_success(client):
    cfg = client.application.config["SEED_IDS"]
    resp = client.post(
        "/reviews",
        json={"book_id": cfg["book_id"], "user_id": cfg["user_id"], "rating": 5, "content": "Great!"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["rating"] == 5


def test_get_reviews_filtered(client):
    cfg = client.application.config["SEED_IDS"]
    client.post(
        "/reviews",
        json={"book_id": cfg["book_id"], "user_id": cfg["user_id"], "rating": 4, "content": "Nice"},
    )
    resp = client.get("/reviews", query_string={"book_id": cfg["book_id"], "min_rating": 4})
    assert resp.status_code == 200
    assert resp.get_json()["totalElements"] >= 1


def test_add_wishlist_success(client):
    cfg = client.application.config["SEED_IDS"]
    resp = client.post("/wishlists", json={"user_id": cfg["user_id"], "book_id": cfg["book_id"]})
    assert resp.status_code == 201


def test_add_wishlist_duplicate(client):
    cfg = client.application.config["SEED_IDS"]
    client.post("/wishlists", json={"user_id": cfg["user_id"], "book_id": cfg["book_id"]})
    resp = client.post("/wishlists", json={"user_id": cfg["user_id"], "book_id": cfg["book_id"]})
    assert resp.status_code == 409


def test_add_cart_invalid_quantity(client):
    cfg = client.application.config["SEED_IDS"]
    resp = client.post(
        "/cart",
        json={"user_id": cfg["user_id"], "book_id": cfg["book_id"], "quantity": 0},
    )
    assert resp.status_code == 400


def test_add_cart_success(client):
    cfg = client.application.config["SEED_IDS"]
    resp = client.post(
        "/cart",
        json={"user_id": cfg["user_id"], "book_id": cfg["book_id"], "quantity": 2},
    )
    assert resp.status_code == 201


def test_create_order_requires_auth(client):
    cfg = client.application.config["SEED_IDS"]
    resp = client.post("/orders", json={"user_id": cfg["user_id"], "items": [{"book_id": cfg["book_id"]}]})
    assert resp.status_code == 401


def test_create_order_success(client):
    cfg = client.application.config["SEED_IDS"]
    email, pwd = user_creds(client)
    token = login(client, email, pwd)["access_token"]
    resp = client.post(
        "/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": cfg["user_id"], "items": [{"book_id": cfg["book_id"], "quantity": 1}]},
    )
    assert resp.status_code == 201


def test_list_orders_requires_auth(client):
    resp = client.get("/orders")
    assert resp.status_code == 401


def test_list_orders_user_scope(client):
    cfg = client.application.config["SEED_IDS"]
    email, pwd = user_creds(client)
    token = login(client, email, pwd)["access_token"]
    client.post(
        "/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": cfg["user_id"], "items": [{"book_id": cfg["book_id"], "quantity": 1}]},
    )
    resp = client.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["totalElements"] >= 1
