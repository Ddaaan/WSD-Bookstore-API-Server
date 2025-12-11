from datetime import datetime
from ..extensions import db

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(255), nullable=False, index=True)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
