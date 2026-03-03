#!/usr/bin/env bash
# ievo.sh — Launch Claude Code with iEvo pipeline agents
#
# First run: starts new session
# Next runs: resumes last session (--continue picks most recent)
# Claude auto-discovers sub-agents from .claude/agents/
# Debug logs: .ievo/debug.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

DEBUG_LOG=".ievo/debug.log"

# ── Preflight checks ──────────────────────────────────────────

if [ ! -d ".ievo" ]; then
  echo "Error: .ievo/ not found. Run ievo init first." >&2
  exit 1
fi

if [ ! -d ".claude/agents" ]; then
  echo "Error: .claude/agents/ not found. Deploy agents first." >&2
  exit 1
fi

if ! command -v claude &>/dev/null; then
  echo "Error: claude CLI not found. Install Claude Code first." >&2
  exit 1
fi

AGENT_COUNT=$(find .claude/agents -name '*.md' | wc -l | tr -d ' ')
echo "iEvo pipeline ready — $AGENT_COUNT agents loaded"
echo "Debug log: $DEBUG_LOG"
echo ""

# ── Launch Claude ─────────────────────────────────────────────

# Try to continue the most recent session, fall back to new
claude --continue --debug-file "$DEBUG_LOG" 2>/dev/null || exec claude --debug-file "$DEBUG_LOG"
