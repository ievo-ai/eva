# Evolution Log

## 2026-03-01: Re-read YAML files between sequential edits

**Context:** While hardening GitHub Actions workflow files (quoting shell vars, moving `${{ }}` into `env:` blocks), two sequential Edit calls on `eva-scan.yml` without re-reading between them created a duplicate `env:` block — corrupting the YAML structure. Separately, a security hook blocked an edit to `eva-on-issue.yml` but I proceeded without verifying, requiring another edit cycle.

**Action:** Added "Editing rules" section to CLAUDE.md: (1) always re-read YAML workflow files between sequential edits, (2) when a hook blocks an Edit, verify file state before proceeding.

**Goal:** Prevent YAML file corruption from blind sequential edits. Prevent wasted edit cycles when hooks block changes.
