from datetime import datetime
from ..extensions import db
from ._types import BigInt


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(BigInt, primary_key=True, autoincrement=True)
    user_id = db.Column(BigInt, db.ForeignKey("users.id"), nullable=False, index=True)
    book_id = db.Column(BigInt, db.ForeignKey("books.id"), nullable=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="wishlists")
    book = db.relationship("Book", back_populates="wishlists")
