# syntax=docker/dockerfile:1.7
#
# Chainly AI — CPU-only Ultralytics YOLO + FastAPI.
# Layer order: dependency files → PyTorch CPU → requirements → application code
# so code-only rebuilds do not reinstall Python packages.

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 1) Dependency manifest only (maximizes cache hits when code changes)
COPY requirements.txt /app/requirements.txt

# 2) CPU-only PyTorch, then 3) the rest of the stack
RUN python -m pip install --upgrade pip --no-cache-dir \
    && python -m pip install --no-cache-dir \
        torch==2.2.0+cpu torchvision==0.17.0+cpu \
        --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# 4) Application source (change often — stays above cached dependency layers)
COPY . /app

RUN useradd --create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "main.py"]
