# Marketplace

The marketplace hosts agent packages — the children of the iEvo ecosystem.

**Repo**: [ievo-ai/marketplace](https://github.com/ievo-ai/marketplace)

## Agents

| Agent | Role | Model | Output |
|-------|------|-------|--------|
| **spec-writer** | Human intent → atomic requirements | Sonnet | REQ-xxx.md, Q-xxx.md |
| **architect** | Requirements → implementation plans | Opus | PLAN-REQ-xxx.md |
| **coder** | Plans → TDD code | Sonnet | Code + passing tests |
| **researcher** | AI/SDD literature → improvement proposals | Opus | PROP-*.md |

## Agent Package Format

Every agent follows a standard structure:

```
agents/{name}/
├── agent.yaml           # Package manifest
├── ROLE.md              # Agent instructions
├── EVOLUTION_LOG.md     # Self-correction history
├── memory/
│   ├── CONTEXT.md       # Current state
│   ├── DECISIONS.md     # Decision log
│   ├── VOCABULARY.md    # Domain terms
│   └── HISTORY.md       # Session history
├── skills/
│   └── evo/
│       └── SKILL.md     # Self-evolution skill
└── templates/           # Agent-specific templates
```

## Registry

`registry.yaml` at the root indexes all available agents with metadata:

```yaml
agents:
  - name: spec-writer
    version: "0.1.0"
    description: "Converts features into atomic requirements"
    model: sonnet
    dependencies: []
    category: core
```

## Adding New Agents

1. Create agent directory under `agents/`
2. Follow the standard package format
3. Add entry to `registry.yaml`
4. Submit PR for review
