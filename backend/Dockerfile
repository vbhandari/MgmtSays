# =============================================================================
# MgmtSays Backend Dockerfile
# =============================================================================

# -----------------------------------------------------------------------------
# Base stage
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    # Dependencies for unstructured/document processing
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Development stage
# -----------------------------------------------------------------------------
FROM base as development

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install -e ".[dev]"

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY alembic.ini ./

# Create upload directory
RUN mkdir -p /app/uploads

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# -----------------------------------------------------------------------------
# Production stage
# -----------------------------------------------------------------------------
FROM base as production

# Install only production dependencies
COPY pyproject.toml ./
RUN pip install .

# Copy source code
COPY src/ ./src/
COPY alembic.ini ./

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/uploads && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
