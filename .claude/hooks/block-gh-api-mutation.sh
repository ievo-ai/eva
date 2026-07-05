#!/bin/bash
# PreToolUse hook (Bash matcher) — deny `gh api` / `gh search` invocations that
# specify a mutating HTTP method (POST/PUT/PATCH/DELETE).
#
# Why a hook instead of a settings.json deny pattern: Claude Code's own docs
# (permissions page, "Bash permission patterns that try to constrain command
# arguments are fragile") show that literal-substring deny rules like
# `Bash(gh api* -X DELETE*)` are bypassable via alternate flag syntax
# (--method=DELETE with no space), case variation (-x delete), or variable
# indirection (M=DELETE && gh api -X $M ...). A hook can apply a
# case-insensitive regex tolerant of `=`/whitespace, which a static glob
# pattern cannot. It still can't resolve arbitrary shell variable expansion
# (no static text tool can), so this is a stronger filter, not a perfect one.
#
# Exit 2 = deny (Claude Code shows stderr as the reason). Exit 0 = no
# opinion, defer to the existing allow/deny rules in settings.json.

set -euo pipefail

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // empty')

if [ -z "$command" ]; then
  exit 0
fi

# Only inspect commands that actually invoke `gh api` or `gh search`
# (word-boundary-ish check via grep -w on "gh" is unreliable for a full
# subcommand match, so match the two-word sequence directly).
if ! echo "$command" | grep -qiE '(^|[;&|]|[[:space:]])gh[[:space:]]+(api|search)([[:space:]]|$)'; then
  exit 0
fi

# Case-insensitive, whitespace-or-equals-tolerant match for a mutating method
# flag: -X/--method followed by (optional =/space) then POST/PUT/PATCH/DELETE.
if echo "$command" | grep -qiE -- '(-X|--method)[[:space:]=]*(POST|PUT|PATCH|DELETE)'; then
  echo "Blocked: gh api/search call specifies a mutating HTTP method (POST/PUT/PATCH/DELETE)." >&2
  echo "This project's gh api/search grant is scoped to read-only discovery/audit use." >&2
  echo "Command: $command" >&2
  exit 2
fi

exit 0
