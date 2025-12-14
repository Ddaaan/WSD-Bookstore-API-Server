import os
import sys
import random
from decimal import Decimal
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

# 현재 파일 기준으로 프로젝트 루트 경로를 sys.path에 추가
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.app import create_app
from src.app.extensions import db
from src.app.models import (
    User,
    Author,
    Category,
    Book,
    Order,
    OrderItem,
    Review,
)



def clear_and_create_tables():
    """모든 테이블 드롭 후 다시 생성 (개발/테스트용)"""
    print("[*] Dropping all tables...")
    db.drop_all()
    print("[*] Creating all tables...")
    db.create_all()
    print("[*] DB schema recreated.")


def seed_users():
    print("[*] Seeding users...")

    users = []

    # 관리자 계정 1개
    admin = User(
        email="admin@example.com",
        name="Admin",
        role="ADMIN",
        password_hash=generate_password_hash("Admin123!"),
    )
    users.append(admin)

    # 일반 사용자 9명
    for i in range(1, 10):
        u = User(
            email=f"user{i}@example.com",
            name=f"User{i}",
            role="USER",
            password_hash=generate_password_hash(f"User{i}123!"),
        )
        users.append(u)

    db.session.add_all(users)
    db.session.commit()

    print(f"[*] Inserted {len(users)} users.")
    return users


def seed_categories():
    print("[*] Seeding categories...")
    names = [
        "소설",
        "에세이",
        "자기계발",
        "IT/프로그래밍",
        "경제/경영",
        "과학",
        "역사",
        "여행",
    ]

    categories = []
    for name in names:
        c = Category(
            name=name,
        )
        categories.append(c)

    db.session.add_all(categories)
    db.session.commit()

    print(f"[*] Inserted {len(categories)} categories.")
    return categories



def seed_authors():
    print("[*] Seeding authors...")
    family_names = ["김", "이", "박", "최", "정", "조", "한", "장", "유", "임"]
    given_names = ["지민", "서연", "도윤", "하준", "수진", "민서", "지후", "예린", "서현"]

    authors = []
    for i in range(20):
        name = random.choice(family_names) + random.choice(given_names)
        a = Author(
            name=name,
            bio=f"{name} 작가의 약력입니다.",
        )
        authors.append(a)

    db.session.add_all(authors)
    db.session.commit()

    print(f"[*] Inserted {len(authors)} authors.")
    return authors


def seed_books(authors, categories):
    print("[*] Seeding books...")

    titles = [
        "파이썬 웹 개발 완전 정복",
        "플라스크로 시작하는 백엔드",
        "알고리즘 문제풀이 비법",
        "데이터베이스 설계와 최적화",
        "깨지기 쉬운 개발자의 마음",
        "혼자 공부하는 컴퓨터 구조",
        "AI와 함께하는 미래",
        "나는 오늘도 코드를 읽는다",
        "테스트 주도 개발 입문",
        "실전 REST API 설계",
    ]

    books = []
    for i in range(80):  # 80권 정도 생성
        title = random.choice(titles) + f" #{i+1}"
        author = random.choice(authors)
        category = random.choice(categories)

        price = Decimal(random.randint(8, 35) * 1000)  # 8,000 ~ 35,000원
        stock_cnt = random.randint(0, 50)

        b = Book(
            title=title,
            description=f"{title} 에 대한 소개입니다.",
            price=price,
            stock_cnt=stock_cnt,
            isbn=f"978-{random.randint(1000000000, 9999999999)}",
            publisher="WSD 출판사",
            published_date=datetime.utcnow().date()
            - timedelta(days=random.randint(0, 365 * 3)),
            author_id=author.id,
            category_id=category.id,
        )
        books.append(b)

    db.session.add_all(books)
    db.session.commit()

    print(f"[*] Inserted {len(books)} books.")
    return books


def seed_orders_and_reviews(users, books):
    print("[*] Seeding orders & reviews...")

    orders = []
    order_items = []
    reviews = []

    # 로그인 가능한 일반 사용자만 대상으로 주문/리뷰 생성
    target_users = [u for u in users if u.role == "USER"]

    for u in target_users:
        # 각 사용자마다 2~4개의 주문 생성
        for _ in range(random.randint(2, 4)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 60))

            o = Order(
                user_id=u.id,
                status=random.choice(["PENDING", "PAID", "SHIPPED", "COMPLETED"]),
                total_amount=Decimal("0"),
                created_at=created_at,
            )
            db.session.add(o)
            db.session.flush()  # o.id 사용 위해

            num_items = random.randint(1, 4)
            picked_books = random.sample(books, num_items)

            total = Decimal("0")
            for b in picked_books:
                quantity = random.randint(1, 3)
                oi = OrderItem(
                    order_id=o.id,
                    book_id=b.id,
                    quantity=quantity,
                    unit_price=b.price,
                )
                total += b.price * quantity
                order_items.append(oi)
                db.session.add(oi)

                # 리뷰도 약간 생성
                if random.random() < 0.5:
                    r = Review(
                        user_id=u.id,
                        book_id=b.id,
                        rating=random.randint(3, 5),
                        content=f"{b.title} 에 대한 짧은 리뷰입니다.",
                        created_at=created_at + timedelta(hours=random.randint(1, 72)),
                    )
                    reviews.append(r)
                    db.session.add(r)

            o.total_amount = total
            orders.append(o)

    db.session.commit()

    print(f"[*] Inserted {len(orders)} orders.")
    print(f"[*] Inserted {len(order_items)} order_items.")
    print(f"[*] Inserted {len(reviews)} reviews.")

    return orders, order_items, reviews


def main():
    # prod 설정을 사용 (DATABASE_URL에 맞게 접속)
    app = create_app("prod")

    with app.app_context():
        clear_and_create_tables()

        users = seed_users()
        categories = seed_categories()
        authors = seed_authors()
        books = seed_books(authors, categories)
        seed_orders_and_reviews(users, books)

        # 대략 개수 출력
        total_rows = (
            User.query.count()
            + Author.query.count()
            + Category.query.count()
            + Book.query.count()
            + Order.query.count()
            + OrderItem.query.count()
            + Review.query.count()
        )
        print(f"[*] Total logical rows (중복 포함) ~ {total_rows} 개")


if __name__ == "__main__":
    main()