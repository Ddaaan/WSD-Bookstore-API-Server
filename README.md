# WSD Commerce API

End-to-end commerce-style REST API implemented with Flask, SQLAlchemy, and MySQL, built to satisfy the Assignment 2 requirements (30+ endpoints, JWT auth, RBAC, pagination/search/sort, docs, Postman, seeds, and automated tests).

## Key Features
- 8 blueprints covering auth, users, categories, products, reviews, orders, stats, and health (39 endpoints).
- JWT access + refresh tokens with role-based guards (`ROLE_USER`, `ROLE_ADMIN`).
- Consistent error envelope + validation using Marshmallow schemas.
- Pagination, keyword search, multi-field filtering, and dynamic sorting.
- Health endpoint, structured logging, configurable rate limit, and request size caps.
- Swagger/OpenAPI docs powered by flask-smorest at `/docs`.
- Postman collection with token automation + assertions, plus >200 row Faker seeding script.
- 20+ pytest cases spanning auth, catalog, reviews, orders, stats, and RBAC failures.

## Tech Stack
- Python 3.11, Flask 3.x, flask-smorest, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-Migrate
- MySQL / PyMySQL (SQLite in-memory for automated tests)
- Marshmallow, Alembic (via Flask-Migrate), pytest, Faker

## Project Structure
```
app/
  __init__.py          # app factory, rate limit hooks
  config.py            # env-driven config
  error_handlers.py    # global error mapping
  extensions.py        # db, migrate, jwt, api instances
  models.py            # SQLAlchemy models + mixins
  resources/           # blueprints per domain
  schemas.py           # Marshmallow schemas/DTOs
  responses.py         # error + pagination helpers
  security.py          # JWT callbacks + RBAC helpers
  rate_limit.py        # lightweight limiter
scripts/seed.py        # Faker-based data generator (>200 rows)
docs/                  # api-design, db-schema, architecture notes
postman/wsd-commerce.postman_collection.json
tests/                # pytest suites (22 tests)
README.md, .env.example, requirements.txt, wsgi.py
```

## Running Locally
```bash
# 1) Install deps
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2) Configure env
cp .env.example .env && update DB/JWT secrets

# 3) Database migrations + seed data
flask --app wsgi db upgrade
python scripts/seed.py

# 4) Start API
flask --app wsgi run --host 0.0.0.0 --port 5000
```

## Environment Variables
| Variable | Description |
| --- | --- |
| `FLASK_ENV` | `development` or `production`.
| `SECRET_KEY` | Flask session secret.
| `JWT_SECRET_KEY` | JWT signing secret.
| `DATABASE_URL` | SQLAlchemy DSN (`mysql+pymysql://user:pass@host:3306/db`).
| `RATE_LIMIT_REQUESTS` | Requests per window (default 200).
| `RATE_LIMIT_WINDOW_SECONDS` | Window length (default 60s).

`.env.example` includes safe defaults; real secrets go into `.env` only (never commit `.env`).

## Deployment Endpoints
| Purpose | URL |
| --- | --- |
| Base API | `http://<jcloud-host>:<port>` |
| Swagger UI | `http://<jcloud-host>:<port>/docs` |
| Health | `http://<jcloud-host>:<port>/health` |

Update `<jcloud-host>:<port>` with your JCloud assignment instance before submission.

## Authentication Flow
1. `POST /users` ? open registration for general users.
2. `POST /auth/login` ? returns `{ access_token, refresh_token }`.
3. Attach `Authorization: Bearer <access_token>` for protected routes.
4. `POST /auth/refresh` ? exchange refresh token for new tokens.
5. `POST /auth/logout` ? revokes current access token (blocklist stored in DB).

### Roles & Permissions
| Endpoint Group | USER | ADMIN |
| --- | --- | --- |
| `/users/me`, `/orders`, `/reviews`, `/products` (GET) | ? | ? |
| `/users` CRUD, `/categories` CRUD | ? | ? |
| `/stats/*` | ? | ? |
| `/orders` (list all, update, delete) | ? | ? |
| `/reviews` edit/delete others | ? | ? |

### Example Accounts
| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@example.com` | `P@ssw0rd!` |
| User | `user1@example.com` | `P@ssw0rd!` |

## Database Connectivity (Sample)
| Item | Value |
| --- | --- |
| Host | `db.internal.jcloud.local` |
| Port | `3306` |
| DB | `wsd_assignment` |
| User | `wsd_app` (RW on schema only) |

**Note:** Provide the exact credentials + CLI connection command separately in the secure text/word file requested by the assignment. Never commit them to git.

## Endpoint Summary
| Method & Path | Description |
| --- | --- |
| `GET /health` | Liveness, version info. |
| `POST /auth/login` | Issue JWT tokens. |
| `POST /auth/refresh` | Refresh tokens. |
| `POST /auth/logout` | Revoke token. |
| `POST /users` | Register user. |
| `GET /users` | Admin paged list. |
| `GET /users/{id}` | Admin fetch. |
| `PATCH /users/{id}` | Admin update. |
| `DELETE /users/{id}` | Admin delete. |
| `GET /users/me` | Self profile. |
| `PATCH /users/me` | Self update. |
| `PATCH /users/{id}/deactivate` | Admin deactivate. |
| `GET /users/{id}/orders` | Admin view relations. |
| `POST /categories` | Admin create category. |
| `GET /categories` | List categories. |
| `GET /categories/{id}` | Category detail. |
| `PATCH /categories/{id}` | Admin update. |
| `DELETE /categories/{id}` | Admin delete. |
| `POST /products` | Admin create product. |
| `GET /products` | Catalog search/filter/pagination. |
| `GET /products/{id}` | Product detail. |
| `PATCH /products/{id}` | Admin update. |
| `DELETE /products/{id}` | Admin delete. |
| `GET /products/{id}/reviews` | Paginated reviews per product. |
| `POST /reviews` | Authenticated review creation. |
| `GET /reviews` | Filtered review list. |
| `GET /reviews/{id}` | Review detail. |
| `PATCH /reviews/{id}` | Owner/admin edit. |
| `DELETE /reviews/{id}` | Owner/admin delete. |
| `POST /orders` | Place order. |
| `GET /orders` | Admin list all. |
| `GET /orders/me` | User order history. |
| `GET /orders/{id}` | Owner/admin detail. |
| `PATCH /orders/{id}` | Admin status update. |
| `DELETE /orders/{id}` | Admin delete. |
| `GET /orders/{id}/items` | Nested items. |
| `GET /stats/summary` | Admin KPIs. |
| `GET /stats/top-products` | Admin ranking. |
| `GET /stats/daily-orders` | Admin aggregation. |

## Docs & Tooling
- Swagger UI auto-generated at `/docs` (OpenAPI 3.1).
- Postman collection: `postman/wsd-commerce.postman_collection.json` (with token automation + assertions).
- Design notes + ERD: see `docs/` folder.

## Testing
```bash
pytest -q
```
The suite spins up an in-memory SQLite DB, seeds admin/user/catalog data, and covers at least 22 cases (auth, RBAC failures, CRUD happy paths, stats, etc.).

## Security & Performance Considerations
- Passwords hashed with Werkzeug (PBKDF2) via `User.set_password`.
- JWT blocklist ensures logout/refresh revocation.
- `.env` gating ensures secrets never in git; `.env.example` offers safe defaults.
- Rate limiter + `MAX_CONTENT_LENGTH` mitigate abusive traffic.
- DB indexes on email/name/product/category/order_id accelerate queries used in pagination/search.
- Relationship loading tuned via SQLAlchemy to avoid N+1 on nested serialization.

## Limitations & Future Work
1. Rate limiter is in-memory; replace with Redis for multi-instance deployments.
2. Alembic migrations scaffolded via Flask-Migrate but not auto-run in repo; ensure `flask db migrate` executed when schema evolves.
3. Background jobs (email receipts, analytics cache) out of scope.
4. File uploads / media storage omitted; add S3 integration if needed.

## Submission Checklist
- [x] Source code + docs in repo
- [x] `.env` excluded, `.env.example` included
- [x] Swagger docs, Postman collection, Faker seed script
- [x] Tests (`pytest`) exceed 20 cases
- [x] Ready for JCloud deployment with `wsgi.py`
