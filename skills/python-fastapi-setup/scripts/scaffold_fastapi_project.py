#!/usr/bin/env python3
"""Scaffold a production-minded FastAPI service project."""

from __future__ import annotations

import argparse
import re
import stat
import textwrap
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    if not name:
        raise ValueError("project name must contain at least one letter or digit")
    if name[0].isdigit():
        name = f"service_{name}"
    return name


def package_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return name or "fastapi-service"


def title_name(value: str) -> str:
    words = [part for part in re.split(r"[^A-Za-z0-9]+", value.strip()) if part]
    return " ".join(word[:1].upper() + word[1:] for word in words) or "FastAPI Service"


def render(template: str, **values: str) -> str:
    result = textwrap.dedent(template).lstrip("\n")
    for key, value in values.items():
        result = result.replace(f"@{key}@", value)
    return result


def render_asset(relative: str, **values: str) -> str:
    return render((ASSETS_DIR / relative).read_text(encoding="utf-8"), **values)


def write_file(root: Path, relative: str, content: str, *, executable: bool = False, force: bool = False) -> None:
    path = root / relative
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; rerun with --force to overwrite scaffold-owned files")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def production_command() -> str:
    return "gunicorn -c gunicorn.conf.py app.main:app"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a standard FastAPI service scaffold.")
    parser.add_argument("--name", required=True, help="Service name, for example inventory_api")
    parser.add_argument("--out", help="Output directory. Defaults to ./<sanitized-name>.")
    parser.add_argument("--port", default="8000", help="Local service port used in docs and Compose")
    parser.add_argument("--python-version", default="3.13", help="Python minor version for Docker ARG")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-owned files if they already exist")
    args = parser.parse_args()

    service = safe_name(args.name)
    package = package_name(args.name)
    title = title_name(args.name)
    root = Path(args.out) if args.out else Path.cwd() / service
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    values = {
        "SERVICE": service,
        "PACKAGE": package,
        "TITLE": title,
        "PORT": str(args.port),
        "PRODUCTION_COMMAND": production_command(),
        "PYTHON_VERSION": args.python_version,
    }

    files: dict[str, tuple[str, bool]] = {
        "app/__init__.py": ("", False),
        "app/core/__init__.py": ("", False),
        "app/api/__init__.py": ("", False),
        "app/api/v1/__init__.py": ("", False),
        "app/api/v1/endpoints/__init__.py": ("", False),
        "app/middleware/__init__.py": ("", False),
        "app/main.py": (
            render(
                '''
                from contextlib import asynccontextmanager
                from collections.abc import AsyncIterator

                from fastapi import FastAPI
                from fastapi.middleware.cors import CORSMiddleware

                from app.api.v1.router import api_router
                from app.core.config import get_settings
                from app.middleware.request_context import RequestIdMiddleware


                @asynccontextmanager
                async def lifespan(app: FastAPI) -> AsyncIterator[None]:
                    app.state.settings = get_settings()
                    yield


                def create_app() -> FastAPI:
                    settings = get_settings()
                    application = FastAPI(title=settings.service_name, lifespan=lifespan)
                    application.add_middleware(RequestIdMiddleware)

                    if settings.cors_origins:
                        application.add_middleware(
                            CORSMiddleware,
                            allow_origins=settings.cors_origins,
                            allow_credentials=True,
                            allow_methods=["*"],
                            allow_headers=["*"],
                        )

                    application.include_router(api_router)
                    return application


                app = create_app()
                ''',
                **values,
            ),
            False,
        ),
        "app/core/config.py": (
            render(
                '''
                from functools import lru_cache

                from pydantic_settings import BaseSettings, SettingsConfigDict


                class Settings(BaseSettings):
                    service_name: str = "@TITLE@"
                    environment: str = "local"
                    cors_origins: list[str] = []

                    model_config = SettingsConfigDict(
                        env_file=".env",
                        env_file_encoding="utf-8",
                        extra="ignore",
                    )


                @lru_cache
                def get_settings() -> Settings:
                    return Settings()
                ''',
                **values,
            ),
            False,
        ),
        "app/api/v1/dependencies.py": (
            render(
                '''
                from typing import Annotated

                from fastapi import Depends, Request

                from app.core.config import Settings, get_settings


                SettingsDep = Annotated[Settings, Depends(get_settings)]


                def get_request_id(request: Request) -> str:
                    return getattr(request.state, "request_id", "")
                ''',
                **values,
            ),
            False,
        ),
        "app/api/v1/router.py": (
            render(
                '''
                from fastapi import APIRouter

                from app.api.v1.endpoints import health


                api_router = APIRouter()
                api_router.include_router(health.router)
                ''',
                **values,
            ),
            False,
        ),
        "app/api/v1/endpoints/health.py": (
            render(
                '''
                from fastapi import APIRouter

                from app.api.v1.dependencies import SettingsDep


                router = APIRouter(tags=["health"])


                @router.get("/health")
                async def health_check(settings: SettingsDep) -> dict[str, str]:
                    return {
                        "status": "ok",
                        "service": settings.service_name,
                        "environment": settings.environment,
                    }
                ''',
                **values,
            ),
            False,
        ),
        "app/middleware/request_context.py": (
            render(
                '''
                from uuid import uuid4

                from starlette.middleware.base import BaseHTTPMiddleware
                from starlette.requests import Request
                from starlette.responses import Response


                class RequestIdMiddleware(BaseHTTPMiddleware):
                    async def dispatch(self, request: Request, call_next) -> Response:
                        request_id = request.headers.get("x-request-id") or uuid4().hex
                        request.state.request_id = request_id
                        response = await call_next(request)
                        response.headers["x-request-id"] = request_id
                        return response
                ''',
                **values,
            ),
            False,
        ),
        "tests/test_health.py": (
            render(
                '''
                from fastapi.testclient import TestClient

                from app.main import app


                def test_health_check() -> None:
                    response = TestClient(app).get("/health")

                    assert response.status_code == 200
                    assert response.json()["status"] == "ok"
                    assert response.headers["x-request-id"]
                ''',
                **values,
            ),
            False,
        ),
        "pyproject.toml": (render_asset("pyproject.toml", **values), False),
        ".env.example": (
            render(
                '''
                SERVICE_NAME="@TITLE@"
                ENVIRONMENT="local"
                CORS_ORIGINS=[]
                ''',
                **values,
            ),
            False,
        ),
        ".gitignore": (
            render(
                '''
                __pycache__/
                *.py[cod]
                .pytest_cache/
                .mypy_cache/
                .ruff_cache/
                .venv/
                venv/
                .env
                dist/
                build/
                *.egg-info/
                ''',
                **values,
            ),
            False,
        ),
        "README.md": (
            render(
                '''
                # @TITLE@

                FastAPI service scaffold with typed settings, versioned routers, request ID middleware, a root health check, and a minimal test suite.

                ## Setup

                ```bash
                python3 -m venv .venv
                source .venv/bin/activate
                python -m pip install --upgrade pip
                python -m pip install -e ".[dev]"
                cp .env.example .env
                ```

                ## Run

                ```bash
                uvicorn app.main:app --host 0.0.0.0 --port @PORT@ --reload
                ```

                ## Test

                ```bash
                python -m pytest
                ```

                ## Production

                ```bash
                @PRODUCTION_COMMAND@
                ```

                The health probe is available at `GET /health`.
                ''',
                **values,
            ),
            False,
        ),
    }

    files.update(
        {
            "gunicorn.conf.py": (render_asset("gunicorn.conf.py", **values), False),
            ".dockerignore": (render_asset(".dockerignore", **values), False),
            "Dockerfile": (render_asset("Dockerfile", **values), False),
            "docker-compose.yml": (render_asset("docker-compose.yml", **values), False),
        }
    )

    for relative, (content, executable) in files.items():
        write_file(root, relative, content, executable=executable, force=args.force)

    print(f"Created FastAPI scaffold at {root}")
    print(f"Development: uvicorn app.main:app --host 0.0.0.0 --port {args.port} --reload")
    print(f"Production:  {production_command()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
