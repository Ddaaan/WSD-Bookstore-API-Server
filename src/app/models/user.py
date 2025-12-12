from datetime import datetime
from ..extensions import db
import bcrypt  # 🔹 추가


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
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
    orders = db.relationship("Order", back_populates="user", lazy="dynamic")

    # 비밀번호 해싱 메서드 추가
    def set_password(self, raw_password: str):
        """평문 비밀번호를 받아 bcrypt로 해싱하여 password_hash에 저장"""
        hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """입력한 평문 비밀번호가 저장된 해시와 일치하는지 확인"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )
