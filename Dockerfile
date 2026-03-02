FROM python:3.13-slim AS base

LABEL maintainer="iEvo <hello@ievo.ai>"
LABEL description="Eva — meta-evolution Mother agent for iEvo"

# No bytecode, unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Node.js + Claude Code CLI + GitHub CLI
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends curl ca-certificates git && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y -qq --no-install-recommends nodejs && \
    npm install -g @anthropic-ai/claude-code && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] \
      https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

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
