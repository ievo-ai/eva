#!/usr/bin/env bash
# Deploy Eva to Digital Ocean host via Docker Compose.
#
# Prerequisites:
#   - Ubuntu/Debian host with SSH access (root)
#   - EVA_GITHUB_TOKEN with org-wide access to ievo-ai
#
# Usage:
#   scp scripts/deploy-do.sh root@eva-host:/tmp/ && ssh root@eva-host bash /tmp/deploy-do.sh

set -euo pipefail

IEVO_DIR="/opt/ievo-ai"
EVA_DIR="${IEVO_DIR}/eva"
REPOS=(eva marketplace cli sdk curator ievo.ai)

echo "=== Eva DO Deployment (Docker) ==="

# ── 1. System deps ────────────────────────────────────────
echo "[1/5] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq git curl ca-certificates > /dev/null

# ── 2. Install Docker ─────────────────────────────────────
if ! command -v docker &> /dev/null; then
    echo "[2/5] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
else
    echo "[2/5] Docker already installed."
fi

# Ensure Docker Compose plugin is available
if ! docker compose version &> /dev/null; then
    echo "  Installing Docker Compose plugin..."
    apt-get install -y -qq docker-compose-plugin > /dev/null
fi

# ── 3. Clone repos ───────────────────────────────────────
echo "[3/5] Cloning ievo-ai repos..."
mkdir -p "$IEVO_DIR"

if [ -z "${EVA_GITHUB_TOKEN:-}" ]; then
    echo "ERROR: EVA_GITHUB_TOKEN not set."
    echo "  export EVA_GITHUB_TOKEN=github_pat_..."
    exit 1
fi

for repo in "${REPOS[@]}"; do
    target="${IEVO_DIR}/${repo}"
    if [ -d "$target" ]; then
        echo "  Updating ${repo}..."
        cd "$target" && git pull --ff-only && cd -
    else
        echo "  Cloning ${repo}..."
        git clone "https://x-access-token:${EVA_GITHUB_TOKEN}@github.com/ievo-ai/${repo}.git" "$target"
    fi
done

# ── 4. Create .env (if not exists) ───────────────────────
if [ ! -f "${EVA_DIR}/.env" ]; then
    echo "[4/5] Creating .env template..."
    cat > "${EVA_DIR}/.env" << 'ENVEOF'
# Eva DO deployment — fill in all values

# GitHub PAT (org-wide ievo-ai access)
EVA_GITHUB_TOKEN=

# Anthropic API key (Haiku, ~$1/month)
ANTHROPIC_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_COMMUNITY_CHAT=-1003516954980
TELEGRAM_EVOLUTIONS_TOPIC=10

# Sentry (optional)
# EVA_SENTRY_TOKEN=
# EVA_SENTRY_DSN=
ENVEOF
    echo "  Created ${EVA_DIR}/.env — FILL IN THE TOKENS!"
else
    echo "[4/5] .env already exists."
fi

# ── 5. Start Eva TG daemon ────────────────────────────────
echo "[5/5] Starting Eva TG daemon..."
cd "$EVA_DIR"
docker compose build eva-tg-daemon
docker compose up -d eva-tg-daemon
echo "  Eva TG daemon started."

# ── Done ─────────────────────────────────────────────────
echo ""
echo "=== Deployment complete ==="
echo ""
echo "Next steps:"
echo "  1. Fill in ${EVA_DIR}/.env with tokens"
echo "  2. Restart: cd ${EVA_DIR} && docker compose up -d eva-tg-daemon"
echo "  3. Check logs: docker compose -f ${EVA_DIR}/docker-compose.yml logs -f eva-tg-daemon"
echo ""
echo "Structure:"
echo "  ${IEVO_DIR}/"
for repo in "${REPOS[@]}"; do
    echo "  ├── ${repo}/"
done
echo ""
echo "Commands:"
echo "  docker compose logs -f eva-tg-daemon   # watch logs"
echo "  docker compose restart eva-tg-daemon   # restart"
echo "  docker compose stop eva-tg-daemon      # stop"
echo ""
echo "Update all repos:"
echo "  for d in ${IEVO_DIR}/*/; do cd \$d && git pull && cd -; done"
echo "  cd ${EVA_DIR} && docker compose build && docker compose up -d eva-tg-daemon"
