from datetime import datetime
from ..extensions import db
from ._types import BigInt


class BookCategory(db.Model):
    __tablename__ = "book_categories"

    book_id = db.Column(BigInt, db.ForeignKey("books.id"), primary_key=True)
    category_id = db.Column(BigInt, db.ForeignKey("categories.id"), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
