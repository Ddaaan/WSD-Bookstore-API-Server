# API Design Overview

This document summarizes the REST design decisions that map the Assignment 1 deliverables to the implemented Flask service.

## Resources & Endpoints

| Resource | Core Endpoints | Notes |
| --- | --- | --- |
| Auth | `POST /auth/login`, `POST /auth/refresh` | Stateless JWT (access + refresh), shared error codes |
| Users | `POST /users`, `GET /users`, `GET/PATCH/DELETE /users/{id}`, `GET /users/me` | Admin-only list/detail, all responses hide password hashes |
| Books | CRUD on `/books`, search filters (`keyword`, `category_id`, `author_id`, `min_price`, `max_price`) | Admin write, everyone read |
| Authors | CRUD `/authors` | Linked to `books.author_id` |
| Categories | CRUD `/categories` | Linked to `books.category_id` |
| Reviews | CRUD `/reviews`, nested `GET /books/{id}/reviews` | RBAC: owner or admin can edit/delete |
| Review Likes | `POST/DELETE /review_likes/{review_id}` | Prevent duplicates per user |
| Comments | CRUD `/comments`, nested under reviews | Soft deletion with timestamps |
| Wishlists | CRUD `/wishlists` | Unique `(user_id, book_id)` |
| Cart | CRUD `/cart/items` | Aggregates `quantity`, used by orders |
| Orders | `POST /orders`, `GET /orders`, `GET /orders/{id}`, `PATCH /orders/{id}/status` | Status transitions validated; admin can inspect any order |
| Health | `GET /health` | Liveness info |

The total exceeds 30 HTTP methods once CRUD + nested resources + auth endpoints are counted.

## Request Validation
- Primitive checks performed manually (e.g., `_parse_decimal`, `_parse_date`) for books
- `ApiError` drives consistent error payloads. Validation failures always include `code=VALIDATION_FAILED` and optionally `details`.
- Authentication guard `jwt_required` enforces Bearer tokens and optional role arguments.

## Pagination & Sorting
- Shared helper `apply_pagination_and_sort` accepts `page`, `size`, `sort=field,DESC|ASC`
- Implemented across `/books` and `/orders`

## Searching & Filtering
- `/books`: keyword (title/description), author/category filters, price min/max, status
- `/orders`: filter by status and `user_id` (admin override)

## Error Codes
- Enumerated in `src/app/error_codes.py` (10+ codes)
- Swagger + Postman embed representative examples for 400/401/403/404/409/422/500

## Security
- JWT access tokens for API access; refresh tokens for renewal
- Role-based gating via decorator
- Password hashing handled by `werkzeug.security.generate_password_hash`

## Logging
- `register_request_logging` writes method/path/status/time for every response
- Exceptions flow through `register_error_handlers`, logging stacktraces automatically

## Documentation Assets
- Swagger spec under `docs/swagger.json` (served at `/swagger.json` + `/docs`)
- Postman collection with token automation under `postman/bookstore.postman_collection.json`
