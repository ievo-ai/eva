# Evolution Log

## 2026-03-01: Re-read YAML files between sequential edits

**Context:** While hardening GitHub Actions workflow files (quoting shell vars, moving `${{ }}` into `env:` blocks), two sequential Edit calls on `eva-scan.yml` without re-reading between them created a duplicate `env:` block — corrupting the YAML structure. Separately, a security hook blocked an edit to `eva-on-issue.yml` but I proceeded without verifying, requiring another edit cycle.

**Action:** Added "Editing rules" section to CLAUDE.md: (1) always re-read YAML workflow files between sequential edits, (2) when a hook blocks an Edit, verify file state before proceeding.

**Goal:** Prevent YAML file corruption from blind sequential edits. Prevent wasted edit cycles when hooks block changes.

## 2026-03-01: Always assignee on issues, no sensitive data in evo logs

**Context:** Created GitHub issue without `--assignee` — Denis had to remind me. Then guessed the wrong username instead of looking it up. Also applied `ievo` label to an issue meant for a human collaborator, not for Eva.

**Action:** Updated CLAUDE.md "Working rules": (1) always `--assignee` on issues, look up usernames first, (2) `ievo` label = Eva's task only, (3) evolution logs must never contain sensitive information. Updated `/evo` skill step 8 with assignee and label guidance.

**Goal:** Ensure issues are properly assigned. Keep evolution logs safe for public visibility. Correct label semantics.

## 2026-03-01: Include .gitattributes from the first commit

**Context:** CRLF warnings appeared on every commit since the project was created. Fixed only in session 006 by adding `.gitattributes` and normalizing 43 files. Should have been there from the start.

**Action:** Added rule to CLAUDE.md "Working rules": always include `.gitattributes` with `* text=auto eol=lf` from the first commit of any new repo.

**Goal:** Prevent CRLF/LF inconsistency from accumulating across the project lifecycle.

## 2026-03-01: Verify before acting — adopt fact-check skill

**Context:** Created children symlinks in `agent/children/` instead of `.claude/children/` — wrong path, Denis corrected. Earlier, rejected meddylib's `fact-check` skill as "medical domain-specific" without evaluating its core principle. The core principle — verify facts before acting — is universal and would have prevented multiple errors in this session (wrong paths, guessed usernames, wrong labels).

**Action:** Created `/verify` skill (adapted from meddylib's fact-check) for path verification, convention checking, GitHub API queries, and pattern evaluation. Added "verify before acting" to CLAUDE.md working rules. Reversed the original rejection of fact-check (D-024 adoption table).

**Goal:** Prevent errors from assumptions. Check conventions, paths, and API state before acting. Evaluate patterns by substance, not domain name.

## 2026-03-01: Incremental session bookkeeping and push after milestones

**Context:** Session 009 completed Phase 2 (MkDocs + docs for 4 repos, all committed) but the session file still showed unchecked boxes and "IN PROGRESS" status. All 4 repos had unpushed commits. When context was exhausted, the session record was stale and work was local-only — blocking recovery until the next context window restored state manually.

**Action:** Added two working rules to CLAUDE.md: (1) update session file checkboxes and status immediately after each phase completes, before starting the next phase; (2) push repos after each milestone, not at session end.

**Goal:** Ensure session files always reflect actual progress so context loss doesn't block recovery. Ensure committed work is pushed to remotes incrementally so local-only state is minimized.

## 2026-03-01: Enforce test coverage tooling before adding coverage rules

**Context:** Added "100% test coverage" working rule to CLAUDE.md with `uv run pytest --cov`, but `pytest-cov` was not in dependencies. The rule was unenforceable — running the command failed with "unrecognized arguments". Also, CI workflow (`tests.yml`) used bare `pip install` instead of `uv sync` and had no coverage step.

**Action:** Added `pytest-cov>=6.0` to dev dependencies. Added `[tool.coverage.run]` and `[tool.coverage.report]` config to `pyproject.toml` with `fail_under=54` (current baseline, target 100%). Updated CI to use `uv sync --group dev` and `pytest --cov`. Updated CLAUDE.md rule with "never lower fail_under".

**Goal:** Ensure every rule has working tooling behind it. Coverage ratchet prevents regression while allowing incremental improvement toward 100%.

## 2026-03-02: Minimal path first — remove preemptive fallbacks

**Context:** Built a Telegram responder with unnecessary complexity: API fallback (`_call_claude_api`), message classifier, system prompts, role context loading, model configuration — all for a system that only ever runs via Claude Code CLI in Docker. Denis had to explicitly request removal of each piece. The classifier caused false positives (marking real questions as "noise"), and the API path was never used in production.

**Action:** Added two working rules to CLAUDE.md: (1) "Minimal path first, fallbacks later" — implement only the primary deployment path, add fallbacks only when failure is observed; (2) "Design for the deployment context" — include sender identity in multi-user interfaces from the start. Updated stale CLAUDE.md documentation (responder description, env vars, daemon interval).

**Goal:** Prevent over-engineering. Build what's needed for the actual deployment, not hypothetical scenarios. Reduce surface area for bugs by avoiding preemptive abstractions.

## 2026-03-02: Post-push checklist — session save + evolution publish

**Context:** After three consecutive `git push` operations, did not save the session file or publish the evolution to Telegram. Both are covered by existing rules ("auto-record sessions after every push", "/evo step 9: publish evolution"). The rules existed but were not followed — scattered across different documents, easy to skip under momentum.

**Action:** Added "Post-push checklist" to CLAUDE.md working rules — a single enforceable checkpoint tied to the `git push` event: (1) update session file + HISTORY.md, (2) if /evo was run, publish evolution. Framed as "part of the push, not afterthoughts."

**Goal:** Consolidate scattered post-push obligations into one rule that's harder to skip. The push is not done until the checklist is complete.

## 2026-03-02: Unified evolution format — open source transparency

**Context:** Eva's Telegram formatter had two personalities: children got transparent messages (title, description, confidence), Eva got "spiced" mysterious one-liners ("Her gaze shifted. A child will see clearer now."). This was designed for a closed-source marketing strategy. But iEvo is now fully open source — hiding internals serves no purpose and confuses readers.

**Action:** Removed `format_child_message`, `format_eva_message`, `EVA_SPICE`, `EVA_CHILDREN` — replaced with single `format_telegram_message` that uses transparent format for all agents including Eva. Updated tests accordingly.

**Goal:** One format for all agents. Open source means open communication.

## 2026-03-02: Never fabricate identifiers — verify or admit ignorance

**Context:** During CLI E2E testing, Eva fabricated GitHub username "dennisdup" instead of looking up via `gh api repos/<repo>/collaborators`. The lookup rule already existed in CLAUDE.md but was scoped only to GitHub issue assignees. Eva treated it as advisory and guessed a plausible-sounding username, wasting a command cycle and eroding trust.

**Action:** Generalized the rule in CLAUDE.md: "Never fabricate external identifiers" — covers usernames, repo names, branch names, URLs, API endpoints, file paths. Always look up, never guess. Fabricating a plausible identifier is worse than admitting ignorance.

**Goal:** Prevent hallucination of any external identifier. The cost of a lookup is seconds; the cost of fabrication is trust.

## 2026-03-02: Coverage is not confidence — mocks are not reality

**Context:** Eva's CLI test suite had 340 tests and 100% line coverage. During a real E2E test of `ievo run spec-writer`, the pipeline failed immediately: no file permissions, no progress feedback, Claude session hung. All tests passed because they mocked `subprocess.run` — they tested command assembly, not real execution. 100% coverage gave false confidence that the pipeline worked.

**Action:** Added rule to CLAUDE.md: "Coverage is not confidence" — mocked integration tests prove code paths in isolation, not that the system works end-to-end. For commands that launch external processes, document what a real E2E test requires. Never claim "pipeline works" based on mocked tests alone.

**Goal:** Prevent false confidence from high coverage numbers. Mocks are necessary but not sufficient. Real validation requires real execution.

## 2026-03-02: Docs ship with code — not as afterthoughts

**Context:** Eva pushed a feature commit (Docker sandbox — new module, Dockerfile, refactored run.py) to the CLI repo without updating any documentation. README.md, CLAUDE.md, docs/ARCHITECTURE.md, docs/commands.md, docs/configuration.md were all stale. Denis had to explicitly ask "docs updated?" to trigger the update, which landed as a separate commit. The rule "keep docs updated" existed as a preference in memory but was not in the working rules — the place Eva checks before committing.

**Action:** Added working rule to CLAUDE.md: "Docs ship with code" — when a commit changes user-facing behavior (CLI flags, config format, architecture), documentation updates go in the same commit. Before committing, ask: does this change affect user-facing behavior? If yes, update docs first.

**Goal:** Prevent stale documentation. Docs are part of the feature, not a follow-up task. One commit = code + tests + docs.

## 2026-03-02: Validate assumptions — markers, signatures, test completeness

**Context:** Three errors in one CLI session: (1) Changed `find_project_root()` to search for `.ievo/` directory, but `~/.ievo/` (global config) already existed in the path hierarchy — any CWD under home was falsely detected as a project. (2) Called `init(name=None)` for auto-init without checking the function signature — Typer default was `"."`, not `None`, causing TypeError. (3) Wrote mock-only tests for auto-init that asserted `.assert_called_once()` without verifying actual file creation — Denis caught it: "what's the point of these tests?"

**Action:** Added two rules to Eva CLAUDE.md: (1) "Verify marker uniqueness" — when changing discovery markers, check for collisions in the path hierarchy; (2) "Complete test types per feature" — every feature needs unit + integration + UI tests, mock-only tests are incomplete. Also added the same testing rule to CLI CLAUDE.md.

**Goal:** Prevent three failure modes: marker collisions from not checking existing paths, signature mismatches from not reading function definitions, and false test confidence from mock-only coverage.

## 2026-03-02: Acceptance gate — self-review before declaring done

**Context:** Eva repeatedly marked requirements as complete without verifying test completeness. Pattern: write code, write mock tests, see "449 tests pass, 99% coverage" → say "done". But mocks only proved wiring, not behavior. Denis had to catch gaps manually every time: "what's the point of these mock tests?", "are you actually testing the TUI?", "requirements must be FULLY covered."

**Action:** Created `/acceptance` skill (`.claude/skills/acceptance/SKILL.md`) — mandatory self-review gate before marking any task complete. Checklist: identify requirement, list changes, verify all test types (unit + integration + edge cases + UI), verify real outcomes not just mock calls, check coverage on changed files, check docs. Added "Acceptance before done" rule to both Eva and CLI CLAUDE.md.

**Goal:** Prevent premature "done" declarations. Eva must prove completeness through systematic self-review, not just pass a coverage threshold. The skill is a mandatory gate, not optional.

## 2026-03-02: Pipeline clarification — 15-minute rule, Sprint/Backlog, Acceptance loop

**Context:** Was about to add "≤15 min per requirement" to Spec Writer, but Spec Writer works with business logic and cannot estimate implementation time. Only Architect knows how long implementation takes. The pipeline also lacked formal concepts for Backlog (raw ideas), Sprint (agreed scope), feedback loops (Acceptance → Coder), and escalation (Coder → Architect when plan doesn't work).

**Action:** Tightened Architect ROLE.md decomposition threshold from 30 min to 15 min. Updated Eva ROLE.md pipeline with full lifecycle: Backlog → Spec Writer → Sprint → Architect (≤15 min tasks) → Coder → Acceptance → loop. Added Acceptance child to Eva's family. Removed Tester/Reviewer from planned agents (Acceptance replaces both). Added Coder → Architect escalation (Q-xxx-arch.md). Added Acceptance → Coder feedback loop with formal reports. Researcher proposals now go to Backlog, not directly to Eva. Updated Eva + CLI CLAUDE.md with 15-minute rule. Did NOT modify Spec Writer — time estimation is not its responsibility.

**Goal:** Assign decomposition responsibility to the right agent. Formalize the complete pipeline lifecycle with Backlog, Sprint, feedback loops, and escalation paths. Prevent context exhaustion from oversized tasks.

## 2026-03-02: EVO as dedicated agent — continuous pipeline observer

**Context:** EVO was a skill embedded in each agent, triggered only manually (/evo). Errors accumulated silently between manual sessions. No systematic analysis at pipeline transitions meant context was lost by the time errors were reviewed. Research (ICLR 2025, OpenAI cookbook, EvoAgentX) showed that retrospective learning works best when it happens close to the error — not in batches. 42% of multi-agent failures are spec errors, 37% coordination failures — both detectable at transition points.

**Action:** Created EVO as a dedicated marketplace agent (agents/evo/) with continuous observation at every pipeline transition: post-spec, post-plan, post-implementation, post-acceptance. EVO analyzes quality at each gate, traces errors to root cause (which agent failed?), and proposes ROLE.md mutations. Adopted Kanban-flow model (not Scrum) — continuous flow with WIP limits, no fixed time-boxes. Updated evolution model from 3 tiers to 4 layers: Self-correction → EVO agent → Curator → Eva. EVO does not self-evolve (Eva evolves EVO, preventing circular loops).

**Goal:** Catch errors at the point they occur, not after context is lost. Transform evolution from manual/batch to continuous/event-driven. Based on research: agents that analyze retrospectively close to the error outperform batch retrospectives.

## 2026-03-02: Docs agent — dedicated documentation writer

**Context:** Documentation was assigned to Coder via "docs ship with code" rule, but Coder is optimized for code, not writing. Result: docs were frequently forgotten or written as afterthoughts. Acceptance checked for docs presence but not quality. The pipeline had no agent whose primary job was keeping docs in sync.

**Action:** Created Docs agent (agents/docs/) — runs after Acceptance PASS, updates README, CLAUDE.md, docs/, MkDocs. Uses Haiku model (cheap, templated work). Pipeline becomes: Coder → Acceptance → [EVO] → Docs → Done. Added to Eva children table, registry, and all pipeline diagrams.

**Goal:** Eliminate "docs forgotten" failure mode. Dedicated agent = dedicated responsibility. Cheapest agent in the pipeline (Haiku) for the most neglected task.

## 2026-03-02: Defrag agent — rules live where they're enforced

**Context:** Denis asked where the "Don't reinvent the wheel" rule lives. Answer: Eva CLAUDE.md and CLI CLAUDE.md — but NOT in Architect ROLE.md, the agent who actually makes build-vs-buy decisions. Audit of 35 working rules found ~20 misplaced or missing from their enforcing agent. Eva CLAUDE.md had become a dump for all rules regardless of ownership. Documentation had the same fragmentation — overlapping content, stale references, inconsistent descriptions.

**Action:** Created Defrag agent (Haiku, read-only) — scans all CLAUDE.md, ROLE.md, README.md, docs/ for rule drift, missing rules, stale references, doc overlap. Produces DEFRAG-REPORT.md for Eva to act on. Redistributed rules to their enforcing agents: Architect gained 4 rules (reinvent, minimal path, deployment context, verify), Coder gained 5, Acceptance gained 2, EVO gained 2, Researcher gained 2, Docs gained 1. Cleaned Eva CLAUDE.md — split into agent-enforced rules (reference table), Eva's own rules, and operational rules. Added "What if?" rule from user memory.

**Goal:** Single source of truth per rule. Rules live where they're enforced, not in a central dump. Defrag agent prevents future drift.

## 2026-03-02: Unified .ievo/ storage + IEVO.md overlay

**Context:** Pipeline artifacts (REQs, plans, reports, sessions, memory) had no standard home. Paths were scattered across agent ROLE.md files: some used `spec/`, others `plans/`, others `memory/`. Bootstrap example had a flat structure. No single document described the directory layout — each agent duplicated partial knowledge.

**Action:** Created unified `.ievo/` directory structure: `backlog/`, `spec/`, `plans/`, `reports/`, `memory/` (with `sessions/`). Created `.ievo/IEVO.md` as a managed template overlay — pipeline context that agents read for conventions, naming, and lifecycle. Three-layer context model: CLAUDE.md (project) → IEVO.md (pipeline) → ROLE.md (agent). Updated all 8 agent ROLE.md files to reference `.ievo/` paths. Removed duplicated pipeline descriptions from agents — replaced with "See .ievo/IEVO.md". Added `.ievo/version` file for CLI version tracking and auto-migration. Created CLI template source at `cli/src/ievo/templates/IEVO.md`.

**Goal:** Single source of truth for pipeline structure. Agents read IEVO.md for conventions, not duplicate them. CLI auto-migrates projects when updated.
