# Session 013 — Docker Sandbox Implementation

**Date**: 2026-03-02
**Topic**: Implement Docker sandbox for iEvo agent execution
**Result**: SUCCESS — all 6 steps complete, both repos pushed

## What was built

Docker sandbox architecture for running iEvo agents in isolated containers.

### CLI repo (ievo-ai/cli)

**New files:**
- `src/ievo/core/docker.py` — Docker utilities (check_docker, image_exists, build_sandbox_image, build_docker_command)
- `tests/test_docker.py` — 27 tests covering all Docker functions
- `sandbox/Dockerfile` — Python 3.13-slim + Node.js + Claude Code CLI

**Modified files:**
- `src/ievo/core/agent.py` — Added `SandboxConfig` dataclass (allowed_tools, network, memory_mb, cpu_limit, timeout_seconds) to `AgentPackage`
- `src/ievo/commands/run.py` — Refactored: Docker default, `--local` fallback, auto-build image, TTY detection
- `tests/test_agent.py` — 4 new tests for SandboxConfig
- `tests/test_run.py` — 11 new Docker mode tests (success, fallbacks, auto-build, errors)

**Stats:** 408 tests, 99.5% coverage

### Marketplace repo (ievo-ai/marketplace)

Added `sandbox:` section to all 4 agent manifests:
- **spec-writer**: Read, Write, Glob, Grep (no network)
- **architect**: Read, Write, Glob, Grep (no network)
- **coder**: Read, Write, Edit, Bash, Glob, Grep (no network)
- **researcher**: Read, Write, Glob, Grep, WebFetch, WebSearch (network: true)

### Eva repo (ievo-ai/eva)

- Updated `.claude/settings.local.json` — broad permissions, rm requires approval

## Architecture decisions

- D-013-1: Docker is default execution mode, local is fallback (`--local` flag)
- D-013-2: No `--network none` — Claude CLI needs Anthropic API access
- D-013-3: Network isolation via `--allowedTools` (tool-level, not Docker network)
- D-013-4: Auto-build sandbox image if Docker available but image missing
- D-013-5: Graceful fallback chain: Docker → auto-build → local

## Commits

| Repo | Hash | Description |
|------|------|-------------|
| cli | `320e7d7` | feat: Docker sandbox for agent execution |
| marketplace | `f7e6eb1` | feat: add sandbox config to all agent manifests |

## What's next

- [ ] Build and test sandbox image: `docker build -t ievoai/sandbox:latest sandbox/`
- [ ] Real E2E test: `ievo run spec-writer -m "Create REQ for word counter"`
- [ ] Create Docker Hub account and CI (issues #11, #14)
- [ ] Fix remaining CLI issues (#3, #4, #5, #6, #8)
