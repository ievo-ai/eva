#!/usr/bin/env python3
"""Append a new evolution entry to ievo.ai/docs/evolutions.json.

Usage:
    python publish-evolution.py \
        --id EVO-001 \
        --title "Fixed format validation across agents" \
        --agent eva \
        --type role_patch \
        --target "agents/spec-writer/ROLE.md" \
        --description "Added rule to prevent format_error" \
        --confidence 0.75 \
        --pr "https://github.com/ievo-ai/marketplace/pull/1" \
        --file /path/to/evolutions.json
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Publish evolution to ievo.ai feed")
    parser.add_argument("--id", required=True, help="Evolution ID (e.g. EVO-001)")
    parser.add_argument("--title", required=True, help="Short title")
    parser.add_argument("--agent", default="eva", help="Agent that made the mutation")
    parser.add_argument("--type", default="role_patch",
                        choices=["role_patch", "skill_patch", "memory_update",
                                 "config_patch", "milestone", "best_practice"],
                        help="Mutation type")
    parser.add_argument("--target", default="", help="Target file path")
    parser.add_argument("--description", default="", help="Longer description")
    parser.add_argument("--confidence", type=float, default=0.0, help="Confidence 0.0-1.0")
    parser.add_argument("--pr", default=None, help="PR URL")
    parser.add_argument("--file", required=True, help="Path to evolutions.json")
    args = parser.parse_args()

    path = Path(args.file)
    if path.exists():
        evolutions = json.loads(path.read_text())
    else:
        evolutions = []

    entry = {
        "id": args.id,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "title": args.title,
        "agent": args.agent,
        "type": args.type,
        "target": args.target,
        "description": args.description,
        "confidence": args.confidence,
        "pr": args.pr,
    }

    evolutions.append(entry)
    path.write_text(json.dumps(evolutions, indent=2, ensure_ascii=False) + "\n")
    print(f"✓ Published {args.id}: {args.title}")


if __name__ == "__main__":
    main()
