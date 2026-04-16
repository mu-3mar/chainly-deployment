# syntax=docker/dockerfile:1.7
#
# Production-ready image for the QC-SCM Detection Service.
# - Minimal base (python:3.10-slim)
# - Small/faster builds (layered dependency install, no pip cache)
# - Sensible Python env defaults
# - Non-root runtime user
#
# Run command (required by project): python main.py

FROM python:3.10-slim AS runtime

# ---- Python runtime defaults (best practice) ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ---- Minimal OS deps ----
# OpenCV wheels (even headless) may require libglib + libGL at runtime.
# Keep this list minimal; add more only when a wheel actually needs it.
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
      libglib2.0-0 \
      libgl1 \
  && rm -rf /var/lib/apt/lists/*

# ---- Install Python deps first for better caching ----
# Copy only dependency files first (fast rebuild when only code changes).
COPY requirements.txt /app/requirements.txt

# Install pip + CPU-only PyTorch wheels first, then the rest of the dependencies.
# This ensures we never pull CUDA/GPU builds and avoids pip trying to resolve torch again.
RUN python -m pip install --upgrade pip --no-cache-dir \
  && python -m pip install --no-cache-dir \
       torch torchvision \
       --index-url https://download.pytorch.org/whl/cpu \
  && python -m pip install --no-cache-dir -r /app/requirements.txt

# ---- Copy the application code (models included locally) ----
COPY . /app

# ---- Security: run as a non-root user ----
RUN useradd --create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser \
  && chown -R appuser:appuser /app
USER appuser

# ---- API server port (main.py reads config/api.yaml, defaults to 8000) ----
EXPOSE 8000

# ---- Entrypoint ----
CMD ["python", "main.py"]

