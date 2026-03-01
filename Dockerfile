FROM python:3.13-slim AS base

LABEL maintainer="iEvo <hello@ievo.ai>"
LABEL description="Eva — meta-evolution Mother agent for iEvo"

# No bytecode, unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first (cache layer)
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copy source
COPY src/ src/
COPY agent/ agent/
COPY schemas/ schemas/

# Re-install with source (editable not needed in container)
RUN pip install --no-cache-dir .

# Default config location
ENV EVA_CONFIG=/app/eva.yaml

# Health check
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD eva status || exit 1

ENTRYPOINT ["eva"]
CMD ["scan"]
