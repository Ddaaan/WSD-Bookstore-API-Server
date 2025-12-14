from ..extensions import db


# Use BigInteger for MySQL, fallback to Integer for SQLite so AUTOINCREMENT works.
BigInt = db.BigInteger().with_variant(db.Integer(), "sqlite")
