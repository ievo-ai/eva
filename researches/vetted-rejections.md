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

## R-2026-08-31-001 — repo-indexer.md's Step 4 "Other nonzero" branch echoes scan_repo.mjs stderr verbatim with no excerpt containment

```yaml
id: R-2026-08-31-001
rejected_at: 2026-08-31T13:22:30Z
run_id: 33395461927
source_step: audit
category: security
title: repo-indexer.md Step 4 "Other nonzero" branch returns FAILED <owner>/<repo> — <stderr first line> verbatim with no backtick-fencing, letting a crafted scan_repo.mjs stderr line render live Markdown
```

Premise (from this run's `/ievo:vuln-scan` module dispatch on `plugins/ievo/agents`+`plugins/ievo/commands`): `repo-indexer.md`'s Step 4 "Other nonzero" branch returns `FAILED: <owner>/<repo> — <stderr first line>` as its entire unwrapped response, so if `scan_repo.mjs` ever exits with a code other than 0/2 carrying attacker-influenced stderr, that text renders unfenced. Disproved by direct re-read of `/tmp/skills/plugins/ievo/scripts/scan_repo.mjs` in full: the script has exactly three exit paths — `exit(1)` (line 913, invalid `<owner>/<repo>` format, whose echoed value is `args.repo` itself, constrained to the Markdown-inert `OWNER_REPO_RE` charset), `exit(2)` (lines 925/932, inside `main()`'s own try/catch), and `exit(2)` again via `mainSafe()`'s outer catch-all (line 1037), which wraps every call to `main()` including the enumeration functions (`enumerateStandaloneSkills`, `listDirSorted`) the premise's exploit chain depends on. `repo-indexer.md` Step 4 branches only on exit code `0` / `2` / "other nonzero" — the `2` branch returns a **fixed, hardcoded string** ("network unreachable") that never reads or echoes stderr, and no code path in `scan_repo.mjs` can ever produce an "other nonzero" exit. The "Other nonzero" branch this candidate cites is dead code under the script's own current exit-code behavior. This exact premise, exact file/line, was independently filed and same-run-rejected by a prior Eva run (`skills#659`, closed `eva-rejected`) on identical grounds — this run's vuln-scan dispatch re-derived it without checking `scan_repo.mjs`'s actual exit-code surface first, the same verification gap the original rejection's own comment already documents. No new evidence changes this; premise does not hold.

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

## R-2026-08-11-001 — review-retrospective/SKILL.md Step 3 lacks an excerpt-containment rule for the cluster report it displays

```yaml
id: R-2026-08-11-001
rejected_at: 2026-08-11T00:00:00Z
run_id: 31468098986
source_step: audit
category: security
title: review-retrospective/SKILL.md Step 3 renders the sub-agent's cluster report "as-is" with no backtick-fencing rule for quoted PR review/comment excerpts, unlike deep-review/SKILL.md's paired display-verbatim + agent-side-fencing pattern
```

Premise (from this run's `/ievo:vuln-scan` module dispatch on `plugins/ievo/skills`): `review-retrospective/SKILL.md` Step 3 (`plugins/ievo/skills/review-retrospective/SKILL.md:134`) instructs "Present the sub-agent's cluster report to the user **as-is**" with no accompanying excerpt-containment/backtick-fencing instruction, so a crafted `![...](...)`/`[...](...)` in a quoted PR review/comment excerpt could render live in the Claude Code chat UI. Disproved by direct re-read of `/tmp/skills/plugins/ievo/agents/review-retrospective.md:176-236`: the **dispatched sub-agent** (out of the flagging vuln-scanner's module scope, which covered `plugins/ievo/skills` only) carries its own explicit "Excerpt containment for verbatim untrusted text in the report" rule, which the file's own text names as covering exactly the two surfaces the candidate worried about — "rendered as Markdown on two surfaces — the chat preview and the park file, both in `review-retrospective/SKILL.md` (Steps 3 and 4)". This is the same paired pattern `deep-review/SKILL.md`/`deep-reviewer.md` already use elsewhere in this plugin (agent applies backtick-run-sizing before returning; skill's own "display verbatim, don't unwrap" instruction means don't strip the already-applied fencing, not "no fencing exists"). The candidate's own flagging agent noted this gap in its preconditions ("The dispatched review-retrospective sub-agent... does not independently apply the same excerpt-fencing deep-reviewer applies — unverifiable from this file alone") — cross-module re-read (Step 3c.1's `vuln-scan` Phase 3 cross-module correlation, applied manually here since the module dispatches ran independently) resolves that open precondition: the sub-agent DOES apply it. No live gap — premise does not hold.

