# iEvo Roadmap

Extracted from original TODO.md. Tracks deferred tasks across phases.

---

## Phase 2: Tester Agent
- [ ] Create `agents/tester/ROLE.md` with instructions
- [ ] Define Tester responsibilities beyond Coder's unit tests:
  - Integration tests (multiple modules together)
  - Acceptance tests (does it really match the spec?)
  - Edge cases the Coder missed
  - Performance smoke tests
  - Security review (input validation, auth bypass)
- [ ] Tester memory files (test patterns, known flaky tests, coverage gaps)
- [ ] Tester runs AFTER Coder finishes a requirement
- [ ] Tester can file bug reports as new REQ-xxx-bugfix.md

## Phase 3: PM Agent
- [ ] Create `agents/pm/ROLE.md` with instructions
- [ ] PM generates dashboard/status report
- [ ] PM can re-prioritize based on product owner input
- [ ] PM manages sprints/iterations (optional)
- [ ] PM memory: sprint history, velocity tracking
- [ ] Consider OpenClaw for PM notifications via Telegram/Slack

## Phase 4: Reviewer Agent
- [ ] Create `agents/reviewer/ROLE.md` with instructions
- [ ] Reviewer checks: code quality, plan match, no scope creep, test quality
- [ ] Reviewer can request changes → Coder fixes
- [ ] Reviewer memory: style guide, past review patterns

---

## Infrastructure

### GitHub Actions Automation
- [ ] Debug and test spec-writer.yml workflow
- [ ] Debug and test coder-agent.yml workflow
- [ ] Add workflow for Change Requests (label: `change`)
- [ ] Add workflow that triggers Architect before Coder
- [ ] Add workflow for Tester after Coder PR

### Orchestrator Improvements
- [ ] Pipeline config in YAML (which agents, in what order, conditions)
- [ ] Agent SDK sub-agents for parallel execution where possible
- [ ] Session logging per agent (separate log files)

### Memory System Improvements
- [ ] Auto-summarize memory when files get too large
- [ ] Memory consolidation: merge old HISTORY entries into CONTEXT
- [ ] Cross-agent memory sharing (Architect reads Coder's patterns)
- [ ] MemoryManager class handles load/save/consolidate
- [ ] Semantic search over memory/ directory

### Multi-Project Support
- [ ] Copier template as GitHub repo with tagged releases
- [ ] `copier update` to pull template improvements
- [ ] Project-specific config in CLAUDE.md
- [ ] Shared agent packages across projects

---

## Future: Pluggable Agent Examples
- Medical Researcher: MCP → @cyanheads/pubmed-mcp-server (36M citations)
- Unity Developer: MCP → mcp-unity (bridge to Unity Editor)
- DevOps: MCP → kubernetes-mcp (kubectl + helm via natural language)
- Security Officer: MCP → agent-scan-mcp (prompt injection, tool poisoning)
- Refactoring Guru: MCP → tree-sitter + LSP for code analysis
- DB Admin: MCP → postgres-mcp, mysql-mcp

## Spec Quality
- [ ] Spec linter script: validate REQ format, check for missing fields
- [ ] Auto-detect duplicate requirements
- [ ] Dependency graph visualization (mermaid or graphviz)
- [ ] Spec coverage report: which REQs have plans? Tests? Implementation?

## Performance & Scale
- [ ] What happens at 100+ requirements? (pagination, selective loading)
- [ ] What happens at 10k+ lines of code? (tree-sitter, AST analysis)
