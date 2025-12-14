# Architecture Notes

## Layering
```
run.py / wsgi -> create_app()
 └── app/
     ├── __init__.py          # app factory, logging, swagger bootstrap
     ├── config.py            # per-env configuration
     ├── extensions.py        # SQLAlchemy instance
     ├── error_handlers.py    # ApiError + HTTP/global handlers
     ├── auth_utils.py        # JWT guard decorator
     ├── swagger.py           # Swagger UI + spec serving
     ├── models/              # SQLAlchemy models per domain
     ├── routes/              # Blueprints (auth, users, books, ...)
     ├── pagination.py        # shared pagination helper
     └── ...
```

- **Blueprint per domain**: keeps route definitions isolated and testable.
- **Service/DAO layer** is lightweight; most logic handled at route level due to assignment scope.
- **Error handling** centralizes JSON envelope and logging logic.

## Request Flow
1. `create_app` loads config, initializes DB, registers blueprints, swagger, logging hooks.
2. `jwt_required` decorator validates Bearer tokens, sets `g.current_user`, and enforces RBAC.
3. Routes perform validation, query DB via SQLAlchemy session, and return JSON.
4. Pagination helper standardizes `page/size/sort` logic.
5. `ApiError` raised on validation/auth failures → converted to consistent payload.
6. `register_request_logging` writes summary log per request; `app.logger.exception` logs stacktraces for unexpected errors.

## Documentation Tooling
- Static `docs/swagger.json` served through `/swagger.json`, embedded in Swagger UI via `flask-swagger-ui`.
- README + docs folder capture API design/DB schema/architecture for submission.
- Postman collection located in `postman/`.

## Testing & Tooling
- `pytest` used for unit/integration tests (fixtures target in-memory SQLite or MySQL test DB).
- `scripts/seed_data.py` populates sample data for manual testing/Postman.

## Deployment Considerations
- Designed to run behind WSGI server (Gunicorn, uWSGI). `create_app` keeps everything configurable via env.
- Use `.env` on both local/JCloud; `config.get_config` chooses dev/prod.
- For production, set `FLASK_ENV=prod`, disable debug, configure DB URI, and run with process manager (systemd, pm2, supervisor, etc.).
