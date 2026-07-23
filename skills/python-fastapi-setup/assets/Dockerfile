ARG PYTHON_VERSION=@PYTHON_VERSION@
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY gunicorn.conf.py ./gunicorn.conf.py

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir .

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE @PORT@

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:@PORT@/health', timeout=3).read()" || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
