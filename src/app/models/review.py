from datetime import datetime
from ..extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    book_id = db.Column(db.BigInteger, db.ForeignKey("books.id"), nullable=False, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)

    rating = db.Column(db.Integer, nullable=False)  # 1~5
    title = db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 관계 설정
    user = db.relationship("User", back_populates="reviews")
    book = db.relationship("Book", back_populates="reviews")
    comments = db.relationship("Comment", back_populates="review", lazy="dynamic")
    likes = db.relationship("ReviewLike", back_populates="review", lazy="dynamic")
