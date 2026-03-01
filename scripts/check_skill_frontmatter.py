#!/usr/bin/env python3
"""Pre-commit hook: validate YAML frontmatter in SKILL.md files.

Checks:
- Frontmatter exists (--- delimiters)
- YAML parses without errors
- Required fields present: name, description
"""

import sys
from pathlib import Path

import yaml

REQUIRED_FIELDS = {"name", "description"}


def check_file(path: Path) -> list[str]:
    errors = []
    content = path.read_text()

    if not content.startswith("---"):
        errors.append(f"{path}: missing YAML frontmatter (must start with ---)")
        return errors

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{path}: malformed frontmatter (missing closing ---)")
        return errors

    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"{path}: invalid YAML in frontmatter: {e}")
        return errors

    if not isinstance(meta, dict):
        errors.append(f"{path}: frontmatter must be a YAML mapping, got {type(meta).__name__}")
        return errors

    missing = REQUIRED_FIELDS - set(meta.keys())
    if missing:
        errors.append(f"{path}: missing required fields: {', '.join(sorted(missing))}")

    return errors


def main() -> int:
    files = [Path(f) for f in sys.argv[1:] if f.endswith("SKILL.md")]
    if not files:
        return 0

    all_errors = []
    for f in files:
        all_errors.extend(check_file(f))

    for err in all_errors:
        print(err, file=sys.stderr)

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
