from datetime import datetime
from ..extensions import db


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey("books.id"), nullable=False, index=True)

    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="cart_items")
    book = db.relationship("Book", back_populates="cart_items")
