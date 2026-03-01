# ievo CLI

The `ievo` command-line tool is the front door to the iEvo platform. It manages projects, agents, and sessions.

**Repo**: [ievo-ai/cli](https://github.com/ievo-ai/cli)

## Install

```bash
# Recommended
uvx ievo --help

# Or install globally
uv tool install ievo
pip install ievo
```

## Commands

| Command | Purpose |
|---------|---------|
| `ievo init [name]` | Create new SDD project scaffold |
| `ievo add <agents...>` | Install agents from marketplace |
| `ievo remove <agent>` | Remove an installed agent |
| `ievo update [agent]` | Update to latest marketplace version |
| `ievo list [--marketplace]` | Show installed or available agents |
| `ievo run <agent>` | Start interactive Claude session with agent |
| `ievo orchestrate` | Run coder agent in automated loop |
| `ievo config set/get/delete` | Manage settings and credentials |
| `ievo deps install/check/list` | Manage MCP/plugin dependencies |
| `ievo learn log/push/status` | Show/share evolution history |

## Architecture

```
src/ievo/
├── cli.py           # Typer app entry point
├── commands/        # 13 command modules
├── core/            # Domain models (project, agent, registry, deps)
├── tui/             # Textual dashboard (4 tabs)
├── hooks/           # Claude Code hooks
└── utils/           # Rich console helpers
```

## Key Concepts

- **Project root detection**: walks up from cwd looking for `ievo.yaml`
- **Agent packages**: `agents/{name}/agent.yaml` + `ROLE.md` + `memory/` + `skills/`
- **Registry**: fetched from marketplace, cached in `~/.ievo/cache/registry.yaml`
- **Model resolution**: CLI flag → project override → agent primary → agent fallback
- **MCP auto-config**: `ievo run` generates `.mcp.json` from agent dependencies

## Stack

- **Python 3.13+** with uv
- **Typer** — CLI framework
- **Rich** — terminal formatting
- **Textual** — TUI dashboard
- **httpx** — async HTTP
- **Pydantic** — data validation
