from datetime import datetime
from ..extensions import db
from ._types import BigInt


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(BigInt, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    books = db.relationship(
        "Book",
        secondary="book_categories",
        back_populates="categories",
        lazy="dynamic",
    )
