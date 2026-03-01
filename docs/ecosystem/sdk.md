# SDK

The iEvo SDK provides tools for creating, validating, and testing agent packages.

**Repo**: [ievo-ai/sdk](https://github.com/ievo-ai/sdk)

## Commands

| Command | Purpose |
|---------|---------|
| `ievo-sdk new <name>` | Scaffold a new agent package from templates |
| `ievo-sdk validate <path>` | Validate agent package structure and schema |
| `ievo-sdk inspect <path>` | Show agent metadata and dependencies |

## Scaffolding

```bash
ievo-sdk new my-agent
```

Generates the full agent package structure with:

- `agent.yaml` from Jinja2 templates
- `ROLE.md` with placeholder instructions
- `memory/` directory with empty files
- `skills/evo/SKILL.md` with EVO workflow
- `EVOLUTION_LOG.md`

## Validation

```bash
ievo-sdk validate agents/my-agent/
```

Checks:

- JSON Schema compliance for `agent.yaml`
- Required files exist (ROLE.md, memory/, skills/)
- YAML syntax validity
- Model field values (opus/sonnet/haiku)

## Schema

The agent schema is defined in `schemas/agent.schema.json` and enforces:

- Required fields: name, version, model, dependencies
- Model must be one of: opus, sonnet, haiku
- Dependencies must be a list of strings
- MCP/plugin dependency format validation
