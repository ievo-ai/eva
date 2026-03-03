# Session 016 — Agent Benchmark & Evaluation Framework

**Date**: 2026-03-03
**Status**: in_progress
**REQ**: REQ-001

## Goal

Add fitness function to Eva's mutation pipeline. Run standardized tasks before/after mutation → score with G-Eval judge → include fitness delta in PR as evidence.

## Phases

### Phase 1: Models + Config + Loader
- `src/eva/benchmark/models.py` — BenchmarkTask, Rubric, Dimension, JudgeScore, BenchmarkResult, FitnessDelta
- `src/eva/benchmark/loader.py` — TaskLoader reads YAML from benchmarks/
- `src/eva/core/config.py` — add BenchmarkConfig
- `benchmarks/spec-writer/` — suite.yaml, rubric.yaml, 3 task files
- Tests for all above

### Phase 2: Judge
- `src/eva/benchmark/judge.py` — G-Eval via Claude CLI (Haiku)
- Tests with mocked subprocess

### Phase 3: Runner
- `src/eva/benchmark/runner.py` — Docker orchestration
- Tests with mocked Docker subprocess

### Phase 4: CLI + Storage + Reporter
- `src/eva/benchmark/storage.py` — JSON historical storage
- `src/eva/benchmark/reporter.py` — Rich tables
- `src/eva/cli.py` — benchmark command group (run, pipeline, history)
- Tests for all above

### Phase 5: Pipeline Integration
- `src/eva/pipeline.py` — Phase 3.5 EVALUATE
- `src/eva/github/pr_creator.py` — fitness delta in PR body
- Tests

## Key Decisions
- Custom G-Eval judge via Claude CLI (Haiku) — no DeepEval/Inspect AI dependency
- Spec-writer only in v1, 3 tasks, 4 rubric dimensions
- `benchmarks/` in repo root (data, not code)
- JSON storage in `~/.eva/benchmarks/`
