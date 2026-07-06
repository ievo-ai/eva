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
