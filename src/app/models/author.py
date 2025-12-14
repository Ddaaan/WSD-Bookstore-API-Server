from datetime import datetime
from ..extensions import db


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 관계 - 하나의 저자는 여러 책을 가질 수 있음
    books = db.relationship("Book", back_populates="author", lazy="dynamic")
