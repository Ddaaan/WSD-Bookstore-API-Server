from datetime import datetime
from ..extensions import db


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)

    # ISBN13 코드
    isbn13 = db.Column(db.String(13), nullable=True, unique=True, index=True)

    # 출판사 이름 (nullable 허용)
    publisher = db.Column(db.String(255), nullable=True)

    # 출판일 
    published_date = db.Column(db.Date, nullable=True)

    stock_cnt = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")

    # FK: authors.id
    author_id = db.Column(db.BigInteger,
                          db.ForeignKey("authors.id"),
                          nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author = db.relationship("Author", back_populates="books")
    categories = db.relationship(
        "Category",
        secondary="book_categories",
        back_populates="books",
        lazy="dynamic",
    )
    reviews = db.relationship("Review", back_populates="book", lazy="dynamic")
    wishlists = db.relationship("Wishlist", back_populates="book", lazy="dynamic")
    cart_items = db.relationship("Cart", back_populates="book", lazy="dynamic")
    order_items = db.relationship("OrderItem", back_populates="book", lazy="dynamic")
