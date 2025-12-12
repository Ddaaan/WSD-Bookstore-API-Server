from datetime import datetime
from ..extensions import db


class BookCategory(db.Model):
    __tablename__ = "book_categories"

    book_id = db.Column(db.BigInteger, db.ForeignKey("books.id"), primary_key=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey("categories.id"), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
