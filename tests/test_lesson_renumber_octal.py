"""eva#250/#255: lesson-ID renumber arithmetic must parse NN as base-10.

``%02d``-formatted lesson IDs produce ``08``/``09``, which bare
``$((CUR + 1))`` rejects as invalid octal ("value too great for base") —
under ``set -uo pipefail`` in eva-conflict-scan.yml that aborts the whole
sweep as soon as a date holds 8+ lessons. Guard all three copies of the
renumber recipe against regression to bare arithmetic, and prove the
base-10 form survives the exact failing input.
"""

import re
import subprocess
from pathlib import Path

RENUMBER_COPIES = [
    ".github/workflows/eva-conflict-scan.yml",
    ".github/prompts/eva-fix-pr.md",
    ".github/prompts/eva-implement.md",
]

BARE_INCREMENT = re.compile(r"\$\(\((?:CUR|cur) \+ 1\)\)")
BASE10_INCREMENT = re.compile(r"\$\(\(10#\$(?:CUR|cur) \+ 1\)\)")


def test_no_copy_regresses_to_bare_octal_prone_increment() -> None:
    for rel in RENUMBER_COPIES:
        text = Path(rel).read_text(encoding="utf-8")
        assert not BARE_INCREMENT.search(text), (
            f"{rel}: renumber increment must use $((10#$CUR + 1)) — "
            "bare $((CUR + 1)) chokes on 08/09 (octal parse)"
        )
        assert BASE10_INCREMENT.search(text), (
            f"{rel}: expected the base-10 renumber increment to be present"
        )


def test_base10_increment_survives_leading_zero_eight() -> None:
    result = subprocess.run(
        ["bash", "-c", "set -uo pipefail; CUR=08; echo $((10#$CUR + 1))"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "9"
