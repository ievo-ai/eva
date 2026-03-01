---
name: evo
description: >-
  Analyze Eva's mistakes and evolve her rules to prevent recurrence.
  Use when Denis identifies a mistake, says "/evo", or when an error
  pattern is detected. Targets ROLE.md, CLAUDE.md, and agent memory.
---

# EVO: Eva's Self-Evolution

Analyze mistakes, extract lessons, and update Eva's governing documents to prevent recurrence.

## Workflow

### 1. Identify the Error

If not already clear, ask Denis to describe or reference the mistake. Review recent conversation context. Classify:

| Type | Description | Example |
|------|-------------|---------|
| **Detection error** | False positive or miscalibrated threshold | Pattern flagged at 40% confidence but was noise |
| **Mutation error** | Pattern real, but proposed change was wrong | ROLE patch contradicted existing safety rule |
| **Pattern miss** | Issue existed across signals but Eva didn't detect it | Recurring issue in 3 repos, no frequency trigger |
| **Safety failure** | Violated one of Eva's 8 safety rules | Auto-merged without human review |
| **Communication error** | Misunderstood Denis's intent or platform context | Proposed CLI change when marketplace was the target |
| **Process error** | Skipped validation, didn't run tests, wrong workflow | Created mutation without checking existing PRs |

### 2. Root Cause Analysis

Identify the **root cause**, not the symptom:
- What assumption was wrong?
- What signal was misread or missed?
- What threshold was miscalibrated?
- What information was missing?
- Was there a recognizable pattern?

### 3. Formulate the Lesson

Write a concise, actionable rule. It must be:
- **Specific** — addresses the exact failure mode
- **Actionable** — clear steps to follow
- **Testable** — can verify compliance
- **Minimal** — no unnecessary process

### 4. Review Target Documents

Read the appropriate target document and find the right section:

| Document | Sections |
|----------|----------|
| `agent/ROLE.md` | Identity, Platform, Evolution Levels, Children, Pipeline, Sources, Mutations, Safety Rules, Deployment, Research Loop, Quality Checklist |
| `CLAUDE.md` | Project context, Architecture, Commands, Deployment, Key patterns |
| `agent/memory/CONTEXT.md` | Platform state, Family, Architecture, Sources, Known Patterns |

Check if a similar rule already exists that should be **updated** instead of duplicated.

### 5. Propose the Update

Show Denis the proposed addition/modification. Explain:
- What rule would have prevented this error
- Where exactly it will be inserted
- How it interacts with existing rules

**Get explicit approval before making changes.**

### 6. Apply the Update

After approval:
1. Edit the target document with the approved change
2. Run `uv run pytest tests/` to verify nothing breaks
3. Summarize the change

### 7. Log the Evolution

Append to `agent/EVOLUTION_LOG.md` using Context / Action / Goal format:

```markdown
## YYYY-MM-DD: Brief title

**Context:** What went wrong and why.

**Action:** What rule was added/modified and where.

**Goal:** What this change prevents in the future.
```

### 8. Create GitHub Issue

Create a GitHub issue in `ievo-ai/eva` to track the evolution step:

```bash
gh issue create \
  --repo ievo-ai/eva \
  --title "evo: <brief title>" \
  --label "evolution" \
  --body "<Context/Action/Goal from step 7>"
```

This creates a traceable record. When children agents are ready, Eva can propagate these lessons to them via their own repos.

### 9. Confirm Understanding

Restate the lesson learned. Acknowledge the error and commit to following the new rule. Do not apologize — act.
