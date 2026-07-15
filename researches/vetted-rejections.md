# Vetted Rejections

Append-only log of finding **candidates** Eva considered during a research
run's category audit (Step 3) or feature-gap discovery (Step 4b) but
self-vetoed during Step 3b's vet pass — **before** ever opening a PR or
filing an issue for them.

This is Eva's own recon+audit+vet discipline, adapted (eva#187) from
[shadcn/improve](https://github.com/shadcn/improve) (MIT): "re-read every
cited location itself before showing you anything — false positives get
dropped, wrong attributions get corrected, rejections get recorded." See
`.github/workflows/eva-research.yml` Step 3b for the full instructions.

This complements, not replaces, `eva-backlog-retriage.yml` (eva#167): that
workflow re-verifies findings **after** they became issues in
`ievo-ai/skills`; this file catches the ones that never should have become
issues in the first place — cheaper, since a self-vetoed candidate costs one
Edit call instead of a filed issue plus a Router triage cycle.

## Format

Each rejection is a Markdown section:

```yaml
id: R-YYYY-MM-DD-NNN          # date + zero-padded sequence within day
rejected_at: <ISO 8601 UTC>
run_id: <GitHub Actions run ID that rejected this>
source_step: audit | feature-gap   # Step 3 category audit vs Step 4b discovery
category: correctness | security | performance | test-coverage | tech-debt
        | dependencies-migrations | dx | docs | direction
title: <one-line candidate that was rejected>
```

<one-line premise the candidate claimed>, disproved by <cited file:line or
URL that shows the premise doesn't hold>.

---

## How Eva uses this file per run

- **Pre-audit (Step 1):** read the full file. Merge its `title` entries
  into the SAME `discovered_already` dedup set built from
  `findings-backlog.md` — a self-vetoed candidate is skipped exactly like a
  filed-then-rejected one, unless a run has genuinely NEW cited evidence.
- **Post-vet (Step 3b):** for each candidate that does NOT hold up under
  re-reading, append a new section here via the Edit tool. Append-only —
  never rewrite or remove an existing section.

## Constraints

- No cap. A self-vetoed candidate costs one Edit call, unlike a filed issue
  (Router cycle + operator attention) — there is no reason to ration this.
- If a rejected candidate's premise later changes (the disproving file or
  behavior is itself modified), a future run may reconsider it — cite the
  NEW evidence in the re-discovery; don't silently overturn the record.

<!-- Rejections go below this line, newest last. -->

## R-2026-07-15-001 — scan_repo.mjs / security-auditor.md lack bundled-binary/executable detection in candidate repos

```yaml
id: R-2026-07-15-001
rejected_at: 2026-07-15T00:00:00Z
run_id: manual-research-session-2026-07-15
source_step: feature-gap
category: direction
title: Add bundled-executable/binary detection to scan_repo.mjs and security-auditor.md so a candidate repo smuggling a compiled binary isn't silently missed by text-based content review
```

Premise (from HN "Cursor 0day: When Full Disclosure Becomes the Only Protection Left", https://mindgard.ai/blog/cursor-0day-when-full-disclosure-becomes-the-only-protection-left, 348 pts): Cursor IDE auto-executes a malicious `git.exe` planted at a workspace root with zero user interaction (CWE-426/427). By analogy, a candidate repo audited by iEvo could smuggle a compiled binary that `security-auditor`'s text-based LLM review can't meaningfully inspect, then have it executed downstream. Disproved by direct re-read of `/tmp/skills/plugins/ievo/skills/init/SKILL.md:58`: iEvo's install step explicitly copies files via the **Write tool** ("project-scope..., **copy** files via Write tool (NOT symlink...)"), not filesystem `cp`/`git clone` of the raw candidate into the install target. The Write tool requires the model to emit text content — it structurally cannot faithfully reproduce arbitrary binary bytes, so a smuggled compiled executable cannot survive from the scanned candidate repo into the installed `.claude/agents/`/`.claude/skills/` location this way. Distinct from Cursor's bug: Cursor auto-*discovers and executes* a binary already present in an opened workspace as part of its own Git integration; iEvo has no equivalent "search candidate repo for an executable and run it" step anywhere in the pipeline (`scan_repo.mjs` only reads text/frontmatter; `security-auditor` only reads and reports). No matching exploit chain exists in the current codebase — premise does not hold.

