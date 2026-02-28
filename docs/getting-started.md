# Getting Started — First Spec Writer Session

## Quick Start

Initialize a project and add the spec-writer agent:

```bash
ievo init my-project
cd my-project
ievo add spec-writer
```

Start the Spec Writer in conversation mode:

```bash
ievo run spec-writer -m "This is a bootstrap session: we're using you to write specs for the project.

Read CLAUDE.md for full context. Our goals:

1. Core data models and auth
2. API endpoints for CRUD
3. Frontend components
4. Integration tests

Let's discuss and decompose these into atomic REQs (3-7 tests each).
Start with what you think is the right first requirement."
```

## What to Expect

1. Spec Writer reads its memory (CONTEXT, DECISIONS, VOCABULARY, HISTORY)
2. Reads SPEC_INDEX (empty at first)
3. Reads the project's CLAUDE.md
4. Proposes decomposition into atomic REQs
5. Discusses with you, clarifies ambiguities
6. Creates REQ-001.md, REQ-002.md, ... in spec/requirements/
7. Updates spec/SPEC_INDEX.md
8. Saves its memory at session end

## Post-Session Checklist

- [ ] New files appeared in `spec/requirements/`?
- [ ] `spec/SPEC_INDEX.md` updated?
- [ ] `agents/spec-writer/memory/` files updated?
- [ ] Each REQ has 3-7 testable acceptance criteria?
- [ ] Dependencies between REQs are mapped?

## Tips

- Talk to it like a product owner — describe *what* you want, not *how*
- If it proposes a wrong decomposition — push back, it will adjust
- If something is unclear — it should create Q-xxx.md (question), not guess
- At session end, ask "save your memory" if it forgets

## Automated Runs (CI)

After setting up GitHub Actions, create an Issue with the `feature` label:
- Spec Writer automatically processes the issue
- Creates a PR with new REQ files
- Review and change `status: draft` → `status: ready` before merging
