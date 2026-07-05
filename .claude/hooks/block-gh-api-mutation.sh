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

# gh api defaults to GET, but silently switches to POST when any request
# parameter is added via -f/-F/--field/--raw-field/--input, even with no
# -X/--method flag at all (confirmed: cli.github.com/manual/gh_api — "adding
# request parameters will automatically switch the request method to POST").
# Block this implicit-POST path too, unless an explicit GET override is
# present (gh honors --method GET/-X GET even alongside -f/-F).
if echo "$command" | grep -qiE -- '(^|[[:space:]])(-f|-F|--field|--raw-field|--input)([[:space:]=]|$)'; then
  if ! echo "$command" | grep -qiE -- '(-X|--method)[[:space:]=]*GET'; then
    echo "Blocked: gh api call passes request parameters (-f/-F/--field/--raw-field/--input)" >&2
    echo "with no explicit GET override — gh api silently switches this to POST." >&2
    echo "This project's gh api/search grant is scoped to read-only discovery/audit use." >&2
    echo "Command: $command" >&2
    exit 2
  fi
fi

exit 0
