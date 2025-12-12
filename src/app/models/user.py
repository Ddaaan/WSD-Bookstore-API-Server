from datetime import datetime
from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # "MALE", "FEMALE" 등
    address = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True, index=True)

    role = db.Column(db.String(10), nullable=False, default="USER")  # 'USER', 'ADMIN'
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계
    reviews = db.relationship("Review", back_populates="user", lazy="dynamic")
    comments = db.relationship("Comment", back_populates="user", lazy="dynamic")
    review_likes = db.relationship("ReviewLike", back_populates="user", lazy="dynamic")
    wishlists = db.relationship("Wishlist", back_populates="user", lazy="dynamic")
    cart_items = db.relationship("Cart", back_populates="user", lazy="dynamic")