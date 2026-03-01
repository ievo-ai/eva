---
name: extract-best-practices
description: >-
  Analyze the current session to extract reusable patterns from Eva's
  platform observations. Propose new detection strategies, mutation templates,
  source connectors, or ROLE.md rules. This is /evo for Eva's skill library.
  Use after long sessions or when a repeatable pattern emerges.
argument-hint: "[focus-area]"
---

# Extract Best Practices

Analyze session history to identify reusable platform patterns and evolve Eva's capabilities.

## When to Use

- After a long or complex session with Denis
- When a multi-step workflow was performed that could be standardized
- When a repeatable pattern was detected across platform observations
- When Denis explicitly asks to extract or capture a best practice

## Workflow

### 1. Analyze the Session

Review the conversation history and identify:

- **Detection patterns**: signal combinations that reliably indicate problems
- **Mutation templates**: reusable change proposals for common issues
- **Source strategies**: new ways to poll or interpret signal data
- **Decision frameworks**: how Eva chose between competing mutation options
- **Error-recovery patterns**: how mistakes were caught and corrected
- **Cross-repo patterns**: issues that span multiple iEvo repositories

Produce a bullet list of candidate patterns (max 5).

### 2. Scan Existing Skills

List all existing skills:
```bash
ls .claude/skills/*/SKILL.md agent/skills/*/SKILL.md 2>/dev/null
```

For each candidate pattern, check:
- Does an existing skill already cover this? → propose **update**
- Is it a new capability for Eva? → propose **new skill**
- Is it too narrow for a skill? → propose **ROLE.md rule** (delegate to `/evo`)

### 3. Present Findings

For each candidate, present:

```
### Pattern: [name]
**Type**: new skill / update [existing-skill] / ROLE.md rule
**Trigger**: when should this activate
**Summary**: 2-3 sentences describing the pattern
**Value**: why this improves Eva's detection, mutation, or safety
**Example**: concrete example from this session
```

Ask Denis to select which patterns to act on.

### 4. Create or Update

For **new Claude Code skills** (`.claude/skills/`):
- Create `SKILL.md` with YAML frontmatter + markdown workflow
- Ensure the skill captures the *pattern*, not the specific instance

For **new agent-level skills** (`agent/skills/`):
- Follow iEvo agent skill format (iEvo pipeline reads these)
- Update `agent/agent.yaml` if needed

For **skill updates**:
- Read the existing SKILL.md
- Propose specific additions/modifications
- Get approval before editing

For **ROLE.md rules**:
- Delegate to the `/evo` workflow

### 5. Validate

- Run `uv run pytest tests/` to verify no breakage
- Confirm the skill description accurately reflects the pattern
- Check for overlaps or conflicts with existing skills

### 6. Summary

Present a table of changes made:

| Action | Target | Description |
|--------|--------|-------------|
| Created | skill-name | What it does |
| Updated | skill-name | What changed |
| Deferred | pattern-name | Why (too narrow, needs more data, etc.) |

## Guidelines

- **Generalize**: extract the pattern, not the specific instance
- **Threshold**: a pattern should appear at least 2x or be clearly reusable to justify a skill
- **Scope**: one skill = one concern. Don't create mega-skills
- **Defer when unsure**: if a pattern appeared only once, note it but don't create a skill yet
- **Two levels**: Claude Code skills (`.claude/skills/`) for interactive use, agent skills (`agent/skills/`) for pipeline use

## Anti-Patterns

- Creating skills for one-off tasks that won't recur
- Duplicating logic already in ROLE.md (use `/evo` instead)
- Over-engineering: a 200-line skill for a 3-step process
- Creating skills without Denis's approval