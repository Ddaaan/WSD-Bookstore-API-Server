# Database Schema & Constraints

The service uses SQLAlchemy models backed by MySQL (PyMySQL driver). Below is the logical ER outline (PK **bold**, FK _italic_).

```
users
-----
**id** BIGINT PK
email VARCHAR(255) UNIQUE
name VARCHAR(100)
role VARCHAR(10) DEFAULT 'USER'
password_hash VARCHAR(255)
timestamps...

authors
-------
**id**
name
bio
timestamps...

categories
----------
**id**
name UNIQUE
slug UNIQUE
timestamps...

books
-----
**id**
title, description, price NUMERIC(12,2)
isbn13 UNIQUE
published_at DATE
stock_cnt INT
status VARCHAR(20)
_author_id_ -> authors.id
_category_id_ -> categories.id

book_categories (junction for many-to-many)
-------------------------------------------
**book_id**, **category_id**

orders
------
**id**
_user_id_ -> users.id
status ENUM (PENDING/PAID/...)
total_amount NUMERIC(12,2)
paid_at DATETIME NULL
deleted_at supports soft delete

order_items
-----------
**id**
_order_id_ -> orders.id
_book_id_ -> books.id
quantity INT
unit_price NUMERIC(12,2)

reviews
-------
**id**
_book_id_, _user_id_
rating INT (1~5)
title/content TEXT
timestamps + deleted_at

review_likes
------------
**id**
_review_id_, _user_id_
unique constraint prevents duplicate like per user

comments
--------
**id**
_review_id_, _user_id_
content TEXT

wishlists
---------
**id**
_user_id_, _book_id_
unique pair

cart
----
**id**
_user_id_, _book_id_
quantity INT
```

## Indexing Strategy
- `users.email`, `books.title`, `books.category_id`, `books.author_id`, `orders.user_id`, `order_items.order_id`, etc. defined via SQLAlchemy `index=True`.
- Text search uses `LIKE` for title/description; can be upgraded to full-text indexes if MySQL edition allows.

## Integrity Rules
- Every FK uses `BigInteger` to align with PK types (e.g., `books.category_id`).
- `orders` uses status transitions validated in route to prevent illegal updates (`STATE_CONFLICT`).
- Seed script builds >200 entities to validate constraints & indexes.

## Migration Strategy
- Alembic/Flask-Migrate already configured via `requirements.txt`.
- To generate migrations when the schema changes:
  ```
  flask --app run db migrate -m "describe change"
  flask --app run db upgrade
  ```
