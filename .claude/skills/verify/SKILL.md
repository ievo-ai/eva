---
name: verify
description: >-
  Verify facts before acting. Check paths, conventions, existing patterns,
  and API state before creating files, rejecting patterns, or making claims.
  Auto-invokes before structural changes. Manual via /verify [claim].
argument-hint: "[claim, path, or pattern to verify]"
---

# Verify

Verify facts before acting. Prevent wrong paths, missed conventions, false rejections, and guessed identifiers.

## When to activate

This skill triggers automatically when about to:
- **Create files or directories** — check where they should go (CLAUDE.md architecture, .gitignore, existing structure)
- **Reject a pattern or skill** — evaluate substance, not just domain name
- **Reference GitHub identifiers** — usernames, labels, repos (check via API)
- **Claim something about project structure** — read the actual files first
- **Make adoption/rejection decisions** — verify the pattern's core principle is truly inapplicable

Also available manually: `/verify "claim or path"`

## Verification workflows

### A. Verify file/directory placement

1. Read `CLAUDE.md` architecture tree
2. Check `.gitignore` for relevant patterns
3. Look at existing similar files — where do they live?
4. If convention exists → follow it. If ambiguous → ask Denis.

### B. Verify a pattern adoption/rejection

1. Read the full skill/pattern, not just the title
2. Extract the **core principle** — strip domain-specific language
3. Ask: "Does this principle apply to Eva's domain?"
4. If rejecting → must cite the specific reason the core principle doesn't apply
5. If adopting → describe what adaptation is needed

### C. Verify GitHub state

1. **Usernames** → `gh api repos/<repo>/collaborators --jq '.[].login'`
2. **Labels** → `gh label list --repo <repo>`
3. **Existing issues** → `gh issue list --repo <repo> --search "<query>"`
4. NEVER guess — always query the API first

### D. Verify before structural changes

Before creating new directories, moving files, or changing project layout:
1. Read CLAUDE.md architecture section
2. Check if a convention already exists for this type of content
3. Verify the target path makes sense in the existing tree
4. If unsure → present options to Denis with reasoning

## Output format

When reporting verification results:

```
## Verify: [topic]

**Claim**: [what was assumed]
**Verdict**: Confirmed | Wrong | Needs clarification

**Evidence**: [what was found]
**Action**: [what was done or what needs decision]
```

## Anti-patterns

- Guessing usernames, labels, or paths instead of querying
- Rejecting skills by domain name without reading content
- Creating files in the wrong directory because "it seemed right"
- Making structural changes without reading existing conventions
