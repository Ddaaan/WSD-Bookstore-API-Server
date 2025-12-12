from datetime import datetime
from ..extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.BigInteger, primary_key=True)
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
