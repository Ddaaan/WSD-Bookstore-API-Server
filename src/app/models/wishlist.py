from datetime import datetime
from ..extensions import db


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey("books.id"), nullable=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="wishlists")
    book = db.relationship("Book", back_populates="wishlists")
