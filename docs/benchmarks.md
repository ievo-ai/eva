# Agent Benchmarks

Eva includes a benchmark framework to measure agent quality before and after mutations. This is the fitness function — without it, Eva mutates blindly.

## Quick Start

```bash
# Run spec-writer benchmark (3 tasks, scored by judge)
eva benchmark run spec-writer

# Compare two versions of an agent ROLE.md
eva benchmark run spec-writer --compare agents/spec-writer/ROLE.md agents/spec-writer/ROLE-v2.md

# View historical scores
eva benchmark history spec-writer
```

## Prerequisites

- **Docker** — agents run inside `ievoai/sandbox:latest` container
- **Claude Code CLI** — judge uses `claude -p --model haiku` for scoring
- **`CLAUDE_CODE_OAUTH_TOKEN`** — set in environment for Claude CLI auth

## How It Works

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Loader  │───▶│  Runner  │───▶│  Judge   │───▶│ Reporter │
│ YAML → ↵ │    │ Docker ↵ │    │ G-Eval ↵ │    │ Rich ↵   │
│ tasks    │    │ execute  │    │ score    │    │ tables   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

1. **Loader** reads benchmark tasks and rubric from `benchmarks/<agent>/`
2. **Runner** prepares a Docker workspace with `.ievo/` structure and runs the agent via Claude CLI
3. **Judge** evaluates agent output against the rubric using G-Eval (chain-of-thought → structured JSON scores)
4. **Reporter** prints Rich tables with per-dimension breakdown

## Benchmark Suite Structure

Each agent has a directory under `benchmarks/`:

```
benchmarks/spec-writer/
├── suite.yaml          # manifest — lists rubric + tasks
├── rubric.yaml         # scoring dimensions with weights
└── tasks/
    ├── task-001-user-auth.yaml
    ├── task-002-api-crud.yaml
    └── task-003-notifications.yaml
```

### suite.yaml

```yaml
agent: spec-writer
version: "1"
description: "Benchmark suite for spec-writer agent"
rubric: rubric.yaml
tasks:
  - tasks/task-001-user-auth.yaml
  - tasks/task-002-api-crud.yaml
  - tasks/task-003-notifications.yaml
```

### rubric.yaml

Defines quality dimensions with weights (must sum to 1.0):

```yaml
agent: spec-writer
version: "1"
dimensions:
  - name: testability
    weight: 0.30
    description: "Each AC maps to one testable statement"
    criteria:
      - "Every AC has format: <action> -> <expected output>"
      - "No vague words: fast, easy, intuitive"
      - "Error cases included"

  - name: atomicity
    weight: 0.25
    description: "One behavior per REQ, 3-7 ACs"
    criteria:
      - "REQ covers exactly one user-facing behavior"
      - "3-7 acceptance criteria per REQ"
```

### Task YAML

```yaml
id: task-001-user-auth
agent: spec-writer
title: "User authentication with email/password"
input_prompt: "Write a requirement specification for user authentication..."
context_files:
  ".ievo/IEVO.md": "# iEvo Pipeline\n..."
  ".ievo/spec/requirements/example.md": "# Example REQ..."
expected_artifacts:
  - "REQ-*.md"
```

## CLI Commands

### `eva benchmark run <agent>`

Run all tasks in the benchmark suite and display scores.

```bash
eva benchmark run spec-writer
eva benchmark run spec-writer -b /path/to/benchmarks
eva benchmark run spec-writer -c custom-eva.yaml
```

Options:
- `--benchmarks, -b` — benchmarks directory (default: `benchmarks`)
- `--config, -c` — Eva config file (default: `eva.yaml`)

### `eva benchmark run <agent> --compare <old.md> <new.md>`

Compare two ROLE.md versions — runs benchmark with each version and shows fitness delta.

```bash
eva benchmark run spec-writer --compare ROLE-v1.md ROLE-v2.md
```

Output includes per-dimension delta: which dimensions improved, which regressed.

### `eva benchmark history <agent>`

Show historical benchmark scores.

```bash
eva benchmark history spec-writer
eva benchmark history spec-writer --limit 5
```

Options:
- `--limit` — number of recent results to show (default: 10)

## Walkthrough: Comparing a Mutation

Real scenario — Eva proposes a ROLE.md change for spec-writer. You want to know: did this mutation make the agent better or worse?

### Step 1: Save the current and proposed ROLE.md

```bash
# Current version (from marketplace)
cp .claude/children/spec-writer/ROLE.md /tmp/spec-writer-before.md

# Proposed version (e.g., from Eva's mutation PR)
# Either download from PR, or apply the diff manually
cp /tmp/spec-writer-before.md /tmp/spec-writer-after.md
# ... edit /tmp/spec-writer-after.md with the proposed changes
```

### Step 2: Run the comparison

```bash
eva benchmark run spec-writer \
  --compare /tmp/spec-writer-before.md /tmp/spec-writer-after.md
```

This runs the full suite twice:
1. First with the **before** ROLE.md — scores A
2. Then with the **after** ROLE.md — scores B
3. Computes delta = B − A per dimension

### Step 3: Read the output

```
Benchmark: spec-writer (v1)
┌──────────────────────┬─────────┬────────────────────────────────┐
│ Task                 │ Overall │ Status                         │
├──────────────────────┼─────────┼────────────────────────────────┤
│ task-001-user-auth   │ 72      │ testability=80, atomicity=65   │
│ task-002-api-crud    │ 68      │ testability=75, atomicity=60   │
│ task-003-notif       │ 55      │ testability=50, atomicity=60   │
├──────────────────────┼─────────┼────────────────────────────────┤
│ TOTAL                │ 65.0    │ completed (45.2s)              │
└──────────────────────┴─────────┴────────────────────────────────┘

Fitness Delta: spec-writer (mut-0001)
┌─────────────────┬────────┬───────┬───────┐
│ Metric          │ Before │ After │ Delta │
├─────────────────┼────────┼───────┼───────┤
│ Overall         │ 60.0   │ 65.0  │ +5.0  │
│ testability     │ —      │ —     │ +8.0  │
│ atomicity       │ —      │ —     │ +3.0  │
│ completeness    │ —      │ —     │ -1.0  │
│ no_impl_leakage │ —      │ —     │ +1.0  │
└─────────────────┴────────┴───────┴───────┘
```

**How to interpret:**
- **Positive delta** = mutation improved this dimension
- **Negative delta** = mutation made this dimension worse
- **Overall > 0** = mutation is net positive, safe to merge
- **Overall ≤ 0** = mutation is harmful or neutral, reconsider

### Step 4: Check history (optional)

```bash
eva benchmark history spec-writer
```

Shows all past runs so you can track trends over time.

### Automatic mode (pipeline)

When Eva runs `eva scan --live` with `benchmark.enabled: true`, comparison happens automatically for every `ROLE_PATCH` and `SKILL_PATCH` mutation. The delta is embedded in the PR body — no manual steps needed.

## Configuration

In `eva.yaml`:

```yaml
benchmark:
  enabled: true
  judge_model: haiku        # Claude model for judge (haiku = fast + cheap)
  timeout_sec: 300          # Max seconds per task execution
  docker_image: ievoai/sandbox:latest
  results_dir: ~/.eva/benchmarks   # Where historical results are stored
```

## Pipeline Integration

When `benchmark.enabled: true` in `eva.yaml`, Eva automatically evaluates mutations during the pipeline:

```
Phase 1: Observe → Phase 2: Analyze → Phase 3: Mutate
    → Phase 3.5: Evaluate (benchmark before/after)
    → Phase 4: Create PRs (with fitness delta in body)
```

Only `ROLE_PATCH` and `SKILL_PATCH` mutations targeting `agents/` paths are benchmarked. Other mutation types (config, memory, registry) are skipped.

The fitness delta is included in the PR description:

```markdown
### Benchmark Fitness Delta

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| **Overall** | 60.0 | 65.2 | +5.2 |
| testability | — | — | +3.0 |
| atomicity | — | — | +2.2 |
```

## Storage

Results are saved as JSON in `~/.eva/benchmarks/<agent>/`:

```
~/.eva/benchmarks/
└── spec-writer/
    ├── 2026-03-03T12-00-00.json
    ├── 2026-03-03T14-30-00.json
    └── ...
```

Each file contains scores, per-dimension breakdown, status, and duration.

## Adding a New Agent Benchmark

1. Create `benchmarks/<agent>/suite.yaml` with rubric and task list
2. Create `benchmarks/<agent>/rubric.yaml` with dimensions (weights must sum to 1.0)
3. Create task YAML files in `benchmarks/<agent>/tasks/`
4. Test: `eva benchmark run <agent>`

The judge is generic — it works with any rubric. The rubric defines what "quality" means for each agent type.

## Architecture

```
src/eva/benchmark/
├── __init__.py
├── models.py      # BenchmarkTask, Rubric, JudgeScore, BenchmarkResult, FitnessDelta
├── loader.py      # TaskLoader — YAML → domain objects
├── judge.py       # BenchmarkJudge — G-Eval via Claude CLI
├── runner.py      # BenchmarkRunner — Docker orchestration + scoring
├── reporter.py    # Rich console output
└── storage.py     # JSON-based historical storage
```
