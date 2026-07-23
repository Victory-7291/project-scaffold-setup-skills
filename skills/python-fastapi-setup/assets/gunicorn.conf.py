from __future__ import annotations

import multiprocessing
import os


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


bind = os.getenv("GUNICORN_BIND", "0.0.0.0:@PORT@")
workers = _get_int("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1)
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "uvicorn_worker.UvicornWorker")
backlog = _get_int("GUNICORN_BACKLOG", 2048)
timeout = _get_int("GUNICORN_TIMEOUT", 120)
graceful_timeout = _get_int("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _get_int("GUNICORN_KEEPALIVE", 10)
max_requests = _get_int("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = _get_int("GUNICORN_MAX_REQUESTS_JITTER", 100)

accesslog = "-" if _get_bool("GUNICORN_ACCESSLOG", True) else None
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
capture_output = _get_bool("GUNICORN_CAPTURE_OUTPUT", True)
daemon = False
reload = False
