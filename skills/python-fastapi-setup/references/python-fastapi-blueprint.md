# Python FastAPI Project Blueprint

## Purpose

Use this blueprint when creating or modernizing a Python FastAPI service. It gives the agent concrete defaults while leaving room for an existing repository's conventions.

## Discovery First

Before writing files, classify the target directory:

- Greenfield: empty directory or explicit request for a new API/service.
- Existing project: Python source, package metadata, tests, ASGI entrypoints, Docker files, CI, `.env` examples, or git history already exist.

For existing projects, inspect and summarize:

- ASGI app location and import path.
- Router structure and endpoint behavior that must be preserved.
- Current endpoint contracts: method, path, status code, response fields, response field types, sample payloads, headers, query/path parameters, and error responses visible in code or tests.
- Dependency manager: `pyproject.toml`, `requirements.txt`, Poetry, uv, PDM, pip-tools, or a custom flow.
- Settings/environment pattern and secret handling.
- Middleware and observability.
- Tests and local validation commands.
- Startup commands in docs, scripts, Docker, Compose, systemd, Procfile, or CI.

Modernize by filling gaps in that pipeline instead of replacing working pieces.

## Existing Endpoint Preservation

When a user asks to preserve existing behavior, treat the current app as the source of truth:

- Read the old route handlers before creating the new router modules.
- Copy literal sample payloads, IDs, names, and field types unless the user asked to change them.
- If the old route returns `{"id": 1, "name": "Widget"}`, the migrated test should assert that exact value. A cleaner scaffold that returns `{"id": "item-1", "name": "Sample Item One"}` has broken the contract.
- Write regression tests that call the new ASGI app through `TestClient` and assert the old status codes and response JSON.
- Keep old endpoints at the same paths unless the user explicitly asks for a versioned prefix migration. If a prefix changes, document the compatibility decision.
- Remove wrapper launchers only after the README, Docker, Compose, or process-manager files point at the replacement import path.

## Greenfield Layout

```text
project/
  app/
    __init__.py
    main.py
    core/
      __init__.py
      config.py
    api/
      __init__.py
      v1/
        __init__.py
        router.py
        dependencies.py
        endpoints/
          __init__.py
          health.py
    middleware/
      __init__.py
      request_context.py
  tests/
    test_health.py
  pyproject.toml
  gunicorn.conf.py
  Dockerfile
  .dockerignore
  docker-compose.yml
  .env.example
  .gitignore
  README.md
```

Generate `Dockerfile`, `.dockerignore`, `docker-compose.yml`, and `gunicorn.conf.py` for greenfield services by default.

## Reusable Deployment Templates

Keep stable generated deployment configuration in `assets/` and render it through the scaffold script:

- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml`
- `gunicorn.conf.py`
- `pyproject.toml`

Use `@PLACEHOLDER@` values for service package names, ports, Python version, and container commands. Do not copy database wallets, bind mounts, project-specific image names, external secrets, or deprecated Gunicorn worker classes into the generic templates.

## App Composition

`app/main.py` should be the composition root:

- Define `create_app()`.
- Configure middleware.
- Register routers.
- Define lifespan when process-level resources need startup and shutdown ownership.
- Export `app = create_app()`.

FastAPI's lifespan pattern is useful for resources shared across requests, such as database pools, long-lived HTTP clients, ML models, background processors, or business service instances. Store these on `app.state` and clean them up during shutdown.

## Settings

Prefer `pydantic-settings`:

- Put `Settings` in `app/core/config.py`.
- Use `SettingsConfigDict(env_file=".env", extra="ignore")`.
- Provide a cached `get_settings()` function.
- Keep `.env.example` limited to safe defaults and placeholders.

The FastAPI documentation shows this pattern so tests can override settings cleanly and so environment values are validated before use.

## Routers And Dependencies

Use `app/api/v1/endpoints/` for new services unless a repo already has a different router convention.

- Keep `/health` cheap, deterministic, and free of external service calls.
- Use `app/api/v1/router.py` to aggregate versioned routers.
- Put typed dependency accessors in `app/api/v1/dependencies.py`.
- Endpoints may import service classes for typing and exceptions, but should receive configured instances from dependencies.

## Middleware

Default middleware should be minimal:

- Request ID middleware is a good default for traceability.
- CORS is appropriate for browser-facing APIs or explicit frontend integration.
- Avoid sessions, compression, rate limiting, caching, auth middleware, or custom exception middleware unless the user asks or the existing app needs it.

## Deployment Choices

Current deployment docs support several valid paths:

- Local development: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`.
- Simple local smoke test: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Production and container default: use Gunicorn with the external `uvicorn-worker` package, for example `gunicorn -c gunicorn.conf.py app.main:app`.
- Do not use new scaffolds that import or configure `uvicorn.workers.UvicornWorker`, because Uvicorn documents that module as deprecated.

## Dependency Policy

Default runtime dependencies:

```text
fastapi
uvicorn[standard]
pydantic-settings
gunicorn
uvicorn-worker
```

Default development dependencies:

```text
pytest
httpx
```

Do not pin Python dependency versions in generated `pyproject.toml`; let pip resolve the latest compatible releases for the selected Python runtime.

## Validation

Run as many checks as the local environment supports:

```bash
python3 -m compileall -q app tests
python3 -m pytest
uvicorn app.main:app --host 0.0.0.0 --port 8000
curl -fsS http://127.0.0.1:8000/health
```

For Gunicorn projects:

```bash
gunicorn -c gunicorn.conf.py app.main:app
curl -fsS http://127.0.0.1:8000/health
```

For Docker projects:

```bash
docker build -t fastapi-smoke .
docker run --rm -p 8000:8000 fastapi-smoke
curl -fsS http://127.0.0.1:8000/health
```

If a dependency is missing, report the exact command that could not run and why.

## Source Notes

- FastAPI's advanced guide recommends lifespan for startup and shutdown resource management.
- FastAPI's settings guide uses `pydantic-settings` and cached settings dependencies.
- FastAPI's Docker guide recommends building from official Python images and commonly using a single process per container when replication happens at the platform layer.
- Uvicorn's deployment guide documents `uvicorn.workers` as deprecated and points Gunicorn users to the `uvicorn-worker` package.
