from datetime import datetime
from ..extensions import db
from ._types import BigInt


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(BigInt, primary_key=True, autoincrement=True)
    user_id = db.Column(BigInt, db.ForeignKey("users.id"), nullable=False, index=True)

    # PENDING, PAID, CANCELLED, SHIPPED, COMPLETED
    status = db.Column(db.String(20), nullable=False, default="PENDING")

    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    paid_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", lazy="dynamic")
