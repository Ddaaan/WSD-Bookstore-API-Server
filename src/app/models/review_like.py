from datetime import datetime
from ..extensions import db


class ReviewLike(db.Model):
    __tablename__ = "review_likes"

    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), primary_key=True)
    review_id = db.Column(db.BigInteger, db.ForeignKey("reviews.id"), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="review_likes")
    review = db.relationship("Review", back_populates="likes")
