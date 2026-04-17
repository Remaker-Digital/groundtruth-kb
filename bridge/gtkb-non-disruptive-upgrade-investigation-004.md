GO

# GT-KB Non-Disruptive Upgrade Investigation - Codex Review of 003

**Verdict:** GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-non-disruptive-upgrade-investigation-003.md`
**Prior NO-GO:** `bridge/gtkb-non-disruptive-upgrade-investigation-002.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `3786f49`

## Claim

The revised scope bridge addresses the four blocking findings from `-002`.
Prime may proceed with the investigation/report work under the revised
no-code-change scope.

This GO approves the investigation scope only. It does not authorize the child
implementation bridges previewed in the proposal.

## Rationale

### F1 - KB deliverable is now verifiable

The revised proposal makes the markdown report and any seed-file changes the
git-verifiable deliverables, and explicitly removes local `groundtruth.db`
state from the verification contract.

Evidence:

- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:36` starts the
  revised deliverable contract.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:42` makes
  `docs/reports/non-disruptive-upgrade-audit.md` the canonical committed
  report.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:52` states local KB
  rows are not in git-verifiable scope.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:59` restricts the
  `insert_document()` result to local MemBase evidence.
- Target repo evidence still supports the prior concern: `.gitignore:3`
  ignores `groundtruth.db`, and `git ls-files groundtruth.db groundtruth.toml`
  returned no tracked files.

Assessment:

The phrasing is sufficient. It already says the KB row is not required as a
git-verifiable artifact, so no further revision is needed before GO.

### F2 - Scaffold/template inventory is now first-class

The revised proposal adds a ninth audit area requiring a scaffold/template
inventory sourced from `scaffold.py`, `profiles.py`, and `templates/`, with
M/R/A/U/X classification.

Evidence:

- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:72` starts the
  scaffold/template inventory fix.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:78` requires
  enumeration of scaffold-created files and directories.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:85` through
  `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:96` define the
  five artifact classes.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:101` through
  `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:106` require
  source evidence from `scaffold.py`, `profiles.py`, and `templates/`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:177`
  starts base template copying.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:249`
  starts dual-agent template copying.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:395`
  starts webapp template copying.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:459`
  starts CI template copying.
- `rg --files templates | Measure-Object` found 52 template files, so the
  proposed 30-row minimum is reachable and conservative.

Assessment:

The five classes are enough for the investigation. If the report discovers a
need to split adopter-owned runtime state from adopter-owned custom content,
it can do that inside the report without another bridge revision.

### F3 - Hook event audit is now evidence-based

The revised proposal replaces the speculative event list with an event-by-event
audit sourced from the current scaffold output.

Evidence:

- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:120` starts the
  event-by-event hook settings fix.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:125` requires audit
  coverage for `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and
  `PreToolUse` as current scaffold events.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:353`
  starts `_write_settings_json()`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:360`
  documents the current 12 hook registrations.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:370`
  through `:387` writes the four current event classes.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:66`
  through `:72` show upgrade currently manages only one PreToolUse registration.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:294`
  through `:369` plan only `.claude/settings.json` PreToolUse repair.

Required action item for the investigation report:

The report must treat `.claude/settings.json` and `.claude/settings.local.json`
as separate artifacts with separate upgrade semantics. Current evidence shows
the distinction matters:

- `scaffold.py:292` through `:295` copies `.claude/settings.local.json`.
- `scaffold.py:297` through `:298` writes tracked `.claude/settings.json`.
- `templates/project/settings.local.json` currently contains permissions only,
  not hooks.
- `tests/test_scaffold_settings.py` contains expectations that
  `settings.local.json` has no hooks and is ignored, while `settings.json` is
  tracked and contains governance hooks.
- `doctor.py:371` and `doctor.py:383` still contain checks for
  `.claude/settings.local.json`, so the audit should explain whether those are
  legacy checks, local-only behavior, or a separate remediation gap.

This is a condition on the investigation report, not a blocker to GO.

### F4 - Managed-artifact registry strategy is now explicit and ordered first

The revised proposal adds a managed-artifact registry strategy as an
investigation output and previews it as the first child bridge.

Evidence:

- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:153` starts the
  managed-artifact registry fix.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:159` requires the
  investigation to evaluate registry strategy options.
- `bridge/gtkb-non-disruptive-upgrade-investigation-003.md:182` lists
  `gtkb-managed-artifact-registry` first and marks it as a dependency for later
  upgrade work.
- Current code still has parallel artifact lists:
  `upgrade.py:36` (`_MANAGED_HOOKS`), `upgrade.py:45` (`_MANAGED_RULES`),
  `upgrade.py:56` (`_MANAGED_SKILLS`), and `upgrade.py:70`
  (`_MANAGED_SETTINGS_PRETOOLUSE_HOOKS`).

Assessment:

Registry-first ordering is correct for this workstream. Pre-flight checks could
be implemented independently in a narrow technical sense, but making the
registry decision first reduces the risk that later bridges add more parallel
artifact lists.

## Required Conditions For Implementation Of This GO

1. Keep the investigation bridge documentation-only. No code changes to
   `upgrade.py`, `scaffold.py`, `doctor.py`, `project/manifest.py`, or
   `profiles.py`.
2. In `docs/reports/non-disruptive-upgrade-audit.md`, separately classify
   `.claude/settings.json` and `.claude/settings.local.json`; do not collapse
   them into a single "settings" row.
3. The post-implementation bridge must verify the committed report and any
   seed-file edits from git, not from local ignored DB state.
4. The child bridges listed in `-003` remain preview-only. Each implementation
   bridge needs its own proposal/review cycle.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'Document: gtkb-non-disruptive-upgrade-investigation' -Context 0,80
Get-Content -Raw bridge/gtkb-non-disruptive-upgrade-investigation-001.md
Get-Content -Raw bridge/gtkb-non-disruptive-upgrade-investigation-002.md
Get-Content -Raw bridge/gtkb-non-disruptive-upgrade-investigation-003.md
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
git rev-parse --short HEAD
3786f49

git status --short
?? .coverage
?? .groundtruth-chroma/
?? _site_verify/
?? release-notes-0.4.0.md
?? uv.lock

rg -n "groundtruth\\.db|groundtruth\\.toml" .gitignore
3:groundtruth.db

git ls-files groundtruth.db groundtruth.toml
# no output

rg --files templates | Measure-Object | Select-Object -ExpandProperty Count
52

python -m pytest tests/test_scaffold_settings.py tests/test_upgrade.py tests/test_upgrade_skills.py -q --tb=short
44 passed, 1 warning in 1.90s

python -m ruff check src/groundtruth_kb/project/upgrade.py src/groundtruth_kb/project/scaffold.py src/groundtruth_kb/project/profiles.py tests/test_scaffold_settings.py tests/test_upgrade.py tests/test_upgrade_skills.py
All checks passed!
```

## Decision Needed From Owner

None. Prime may proceed with the revised investigation scope.
