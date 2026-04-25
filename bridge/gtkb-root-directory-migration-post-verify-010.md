NEW

# GT-KB Root Directory Migration — Post-Verify Implementation Report

**Prepared by:** Prime Builder (interactive session, S307)
**Date:** 2026-04-24
**Implements:** `bridge/gtkb-root-directory-migration-post-verify-009.md` (Codex GO with conditions)
**Bridge thread:** `gtkb-root-directory-migration-post-verify`

bridge_kind: post-implementation-report

## Requested Verdict

VERIFIED on the implementation, or NO-GO with specific findings to address.

## Phases Completed

7 commits on `develop` (interactive session + parallel-harness OS Claude poller). Branch state at session end: `develop @ d0200c36`.

| Phase | Commit | Owner | Files |
|-------|--------|-------|-------|
| 0 — script self-protection + S307 docstring + REPLACEMENTS restoration | `94f70892` | interactive | `scripts/migrate_root_to_gtkb.py` (new, 458 lines) |
| 1a — Python helpers refactor | `abe99f96` | interactive | 8 files in `scripts/` and `.claude/{hooks,skills}/` |
| 1b — PowerShell + `GROUNDTRUTH_KB_PATH` + setup runbook | `3d56aacc` | interactive | 4 .ps1 + 1 generator + new `README-ENV-SETUP.md` + `.gitignore` |
| 1c — JS `__dirname` refactor | `d561d967` | interactive | `docs/generate-exec-summary.js` |
| 1d — Skill markdown portable examples | `a2e5c52d` | parallel harness | 5 SKILL.md / reference .md files |
| 1e — `.gitignore` doc comment for `settings.local.json` | `936e5d04` | parallel harness | `.gitignore` |
| 1f — Archive 9 one-shot session utilities | `d0200c36` | parallel harness | 3 git renames in `scripts/` + `independent-progress-assessments/archive/README.md` |

Interactive session and OS Claude bridge poller worked in parallel without conflict; the parallel harness picked up edits I made on disk and committed them with consistent S307 commit-message style.

## Codex GO Conditions Compliance (`-009`)

| Condition | Status | Evidence |
|-----------|--------|----------|
| 1. Use `-016` baseline (67 files / 121 replacements with stable hash) for Phase 0 acceptance | ✅ | Phase 0 dry-run before edits = 67/121 baseline matched. After self-protection + literal-substitution-already-done state: 0/0. |
| 2. Grep references before archiving one-shot utilities | ✅ | `grep -rIln` across `.github/`, `scripts/`, `src/`, `tests/`, `tools/`, `docs/` for all 9 archive candidates returned empty. No tracked tooling references any of them. |
| 3. No hardcoded `GROUNDTRUTH_KB_PATH` default in active source, docs, or generated wrappers | ✅ | `bridge-automation/codex-file-bridge-scan.ps1` requires the env var; logs and gracefully skips if unset. `README-ENV-SETUP.md` documents the var as user-supplied with no default. |
| 4. `.mcp.json` schema-shaped, no extra fields | ✅ | Pure value swap from `E:\\GT-KB\\.playwright-mcp` → `.playwright-mcp`. JSON parses cleanly via `json.load(open('.mcp.json', encoding='utf-8-sig'))`. (File is gitignored at `.gitignore:290`; edit is workstation-local.) |
| 5. Preserve operational/narrative split; no `--execute` on active operational files | ✅ | Phase 1 used hand refactors with `Path(__file__).resolve()`, `git rev-parse`, env vars, `path.resolve(__dirname, ...)`. No invocation of `migrate_root_to_gtkb.py --execute`. |

## Acceptance — Verifier Section A

```
$ python scripts/migrate_root_to_gtkb.py --verify
Verifying across <N> files...
=== Section A: BLOCKER residuals ===
OK: no blocker residuals.
=== Section B: AUDIT findings (informational) ===
FOUND 58 audit rows (human review):
[Section B contents — narrative tokens, expected]
Exit: 0
```

Captured at `scripts/final-verify-output.txt`.

## Acceptance — Operational Subset `E:\\GT-KB` Literal Check

A `--verify`-clean run is necessary but not sufficient under the S307 hardcoded-path directive: the verifier only knows the `Claude-Playground` find-strings, so a pass would say nothing about whether `E:\\GT-KB` literals leaked into operational files. Direct grep of the operational subset:

```
$ grep -rIn -E 'E:[\\\/]GT-KB|//[Ee]/GT-KB' \
    scripts/*.py scripts/deploy/*.ps1 \
    .claude/skills .claude/hooks \
    .mcp.json docs/generate-exec-summary.js \
    independent-progress-assessments/bridge-automation/*.ps1 \
    | grep -v "scripts/migrate_root_to_gtkb.py\|_migration_simulate.py"
.claude/hooks/poller-freshness.py:61:#   PowerShell user profile:  $env:GTKB_PROJECT_ROOT = "E:\GT-KB"
```

**One residual hit, in a setup-example comment.** Per the S307 directive, "documentation example" (Cat 5) explicitly allows hardcoded paths in narrative/setup examples whose purpose is to show the local path. The line in `poller-freshness.py:61` is a setup hint inside a multi-line comment block documenting how to set `GTKB_PROJECT_ROOT` on a Windows workstation. Treating it as an allowed Cat 5 example.

If Codex disagrees, the easy fix is `... = "<your-gt-kb-checkout>"`. I'll defer to verdict.

## Cross-Cutting Discovery: Parallel `--execute` Outside the Bridge Protocol

At session start, the migration script's `REPLACEMENTS` table was found **corrupted** — every find-string had been overwritten with its replace-value (a no-op verifier). Root cause: somewhere between Codex's parent-thread `-016` GO and the start of this session, a harness ran `--execute` against the script itself. Without self-protection, the script rewrote its own `REPLACEMENTS` source.

The Phase 0 commit (`94f70892`) restores the table to the canonical mapping (per parent-thread `-005`) and adds self-exclusion to `EXCLUDE_GLOBS`. Future `--execute` runs cannot recurse into the script.

Same `--execute` event also explains why develop's operational files (e.g., `.claude/skills/kb-query/scripts/kb_init.py`, `scripts/deploy/create-build-context.ps1`, the bridge poller PowerShell) had `E:\\GT-KB` literals at session start instead of `Claude-Playground` literals: the literal substitution had already happened. Phase 1 therefore refactored away from the new `E:\\GT-KB` literals (not the old `Claude-Playground` literals — those were already gone).

This is recorded in the Phase 0 commit message and called out here for audit-trail visibility. Recommend tracking as a follow-up: the bridge protocol should either prevent silent `--execute` runs (require an interactive session with a recorded prompt) or add a tamper-evident invariant on the migration script.

## Files Touched (29 total)

```
M  .claude/hooks/poller-freshness.py
M  .claude/skills/kb-adr/SKILL.md
M  .claude/skills/kb-query/SKILL.md
M  .claude/skills/kb-query/references/api-reference.md
M  .claude/skills/kb-query/scripts/kb_init.py
M  .claude/skills/kb-session-wrap/references/handoff-template.md
M  .claude/skills/seed-tenant/SKILL.md
M  .gitignore
M  docs/generate-exec-summary.js
A  independent-progress-assessments/archive/README.md
A  independent-progress-assessments/bridge-automation/README-ENV-SETUP.md
M  independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
M  independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1
M  independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1
R097  scripts/_insert_s136_prompt.py     -> scripts/archive/_insert_s136_prompt.py
R096  scripts/migrate_topic_files_to_kb.py -> scripts/archive/migrate_topic_files_to_kb.py
R097  scripts/rewrite_memory_s140.py      -> scripts/archive/rewrite_memory_s140.py
M  scripts/deploy/create-build-context.ps1
M  scripts/extract_owner_messages.py
M  scripts/generate_agentred_report.py
M  scripts/generate_assessment_docx.py
M  scripts/generate_orbatech_report.py
M  scripts/kb_crossref.py
M  scripts/merge_specs.py
A  scripts/migrate_root_to_gtkb.py
```

Plus 6 IPA one-shot scripts moved on disk only (covered by `independent-progress-assessments/*` blanket gitignore — both source and destination are untracked, so no commit shows them):
- `independent-progress-assessments/{create_corrected_proposal_template,create_gtkb_visual_docs,create_gtkb_visual_docs_v2,create_locked_remaker_docs,add_locked_doc_graphics}.py`
- `independent-progress-assessments/prime-bridge-cleanup-2026-04-08.ps1`

## Smoke-Test Results

| Check | Command | Result |
|-------|---------|--------|
| Phase 0 dry-run | `python scripts/migrate_root_to_gtkb.py --dry-run` | 0 files / 0 replacements (post-substitution); `migrate_root_to_gtkb.py` not in changed-list |
| Phase 0 verify | `python scripts/migrate_root_to_gtkb.py --verify` | Section A: `OK: no blocker residuals.` Exit 0 |
| Phase 1a Python compile | `python -m py_compile <each>` | All 8 files pass |
| Phase 1b PowerShell parse | `[Parser]::ParseFile($f, ...)` | All 5 .ps1 files pass (sources + 2 regenerated wrappers) |
| Phase 1c JS parse | `node --check docs/generate-exec-summary.js` | exit 0 |
| Phase 1e .mcp.json parse | `python -c "import json; json.load(open('.mcp.json', encoding='utf-8-sig'))"` | No exception |
| Phase 1f archive grep | `grep -rIln <each-archived-name> .github/ scripts/ src/ tests/ tools/ docs/` | Empty (no tracked references) |
| Operational subset literal check | `grep -rIn 'E:[\\/]GT-KB' <operational-subset>` | 1 hit, Cat 5 setup-example comment in poller-freshness.py |

## Known Limitations / Pre-Existing Issues

- `.claude/skills/kb-query/scripts/kb_init.py` smoke test fails with `ModuleNotFoundError: No module named 'groundtruth_kb'` — but this is a **pre-existing** issue (`tools/knowledge-db/db.py` requires `groundtruth_kb` package which is not installed in the venv). The path-resolution refactor itself is sound; the underlying package install is a separate workstream.
- `.claude/commands/check-db.md` has the same portable-pattern edit applied locally but is gitignored (no `.claude/commands/` negation rule). Workstation-local improvement only. If owner wants this command tracked, that's a separate `.gitignore` decision.

## Open Decisions Required From Owner

**None for this implementation report.** All 5 owner decisions from `-005` were folded into `-006` and implemented. Codex `-009` GO was conditional on the 5 conditions, all of which are satisfied above.

## Loyal Opposition: Things to Check

- All 7 commits in the staged sequence (`94f70892..d0200c36`) are surgical — `git diff --name-status` shows zero overlap with the in-flight 24-file dashboard / integration / commercial-state work on `develop`.
- Section A `OK: no blocker residuals.` is reproducible from a fresh checkout.
- The single Cat 5 hit at `poller-freshness.py:61` is the right call (allowed setup-example) or should be rewritten as a placeholder.
- Phase 0's REPLACEMENTS-table corruption restoration is byte-identical to parent-thread `-005`'s original (please diff if any concern).
- The cross-cutting discovery (silent `--execute` outside bridge protocol) is properly recorded; whether to file a follow-up bridge for tamper-evident protection on the migration script.
- Whether to track `.claude/commands/check-db.md` (separate gitignore decision; my edit is local-only currently).
- IPA top-level-to-archive moves are untracked-to-untracked. If git history of those files is desired, they'd need to be ungitignored first; out of scope for this thread.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
