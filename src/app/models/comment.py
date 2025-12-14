from datetime import datetime
from ..extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    review_id = db.Column(db.BigInteger, db.ForeignKey("reviews.id"), nullable=False, index=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey("comments.id"), nullable=True, index=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    # 관계
    review = db.relationship("Review", back_populates="comments")
    user = db.relationship("User", back_populates="comments")

    parent = db.relationship("Comment", remote_side=[id], backref="children")
