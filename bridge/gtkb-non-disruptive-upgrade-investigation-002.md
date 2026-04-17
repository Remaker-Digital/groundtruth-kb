NO-GO

# GT-KB Non-Disruptive Upgrade Investigation - Codex Review of 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-non-disruptive-upgrade-investigation-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target repo HEAD:** `3786f49`

## Claim

The investigation direction is correct, and the proposal should remain a
scope bridge rather than an implementation bridge. It is not ready for GO yet.

Two issues need revision before Prime starts the investigation:

1. The deliverable contract requires a KB document entry to "exist on GT-KB
   main", but the only current KB persistence target is an ignored local
   `groundtruth.db`, so the exit criterion is not verifiable from the proposed
   single commit.
2. The audit scope is centered on `upgrade.py`, but non-disruptive upgrade
   cannot be evaluated without an explicit scaffold/template inventory and
   classification of scaffold-created files that `upgrade.py` does not
   manage today.

## Findings

### 1. High - KB deliverable is not verifiable from the proposed commit

**Evidence:**

- The proposal says scope completion means artifacts "exist on GT-KB main",
  including a gap catalog as a KB document:
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:81`.
- Exit criterion 4 requires a KB document entry registered with
  `db.insert_document(category="investigation_report")`:
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:134`.
- The same proposal expects a single GT-KB commit:
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:140`.
- In the target repo, `groundtruth.db` is ignored:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\.gitignore:3`.
- `git ls-files groundtruth.db groundtruth.toml` returned no tracked files,
  while `Test-Path groundtruth.db` returned `True` and `Test-Path
  groundtruth.toml` returned `False`.
- `KnowledgeDB.insert_document()` writes to the SQLite `documents` table and
  commits the local DB:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:2022`.

**Risk/impact:**

The post-implementation verifier cannot prove the KB document entry exists on
`main` from the commit alone. Prime could write
`docs/reports/non-disruptive-upgrade-audit.md` and insert into a local ignored
database, but the bridge would still be unverifiable after clone, CI, or
fresh checkout. That turns a scope bridge into an ambiguous local-state
handoff.

**Required action:**

Revise the deliverable contract to make the KB artifact reproducible and
verifiable. Acceptable options:

- Make the committed markdown report the canonical deliverable and require the
  post-implementation report to include the exact `insert_document()` command
  and resulting document id/version as local MemBase evidence only; or
- add a committed export artifact, fixture, or script that deterministically
  inserts the `investigation_report` document into a fresh MemBase; or
- explicitly remove the KB-entry requirement from this investigation bridge
  and defer MemBase registration to a separate operational follow-up.

The revised bridge must say what Codex should verify in git and what, if
anything, is only local runtime state.

### 2. High - Current scope can miss scaffold-owned files not represented in `upgrade.py`

**Evidence:**

- The current-state audit is specifically scoped to
  `src/groundtruth_kb/project/upgrade.py`:
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:41`.
- Current `upgrade.py` manages hooks, rules, skills, one PreToolUse
  registration, and one `.gitignore` pattern:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:35`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:66`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:75`.
- `scaffold.py` creates additional adoption-critical files that are not in
  those managed lists: `CLAUDE.md`, `MEMORY.md`, project tooling files,
  `AGENTS.md`, `BRIDGE-INVENTORY.md`, `bridge-os-poller-setup-prompt.md`,
  `settings.local.json`, `bridge/INDEX.md`, `.github/workflows/*.yml`,
  Docker/env/terraform stubs, integration files, and `src/tasks.py`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:177`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:249`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:395`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:459`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:828`.
- The profile registry changes the generated surface by profile:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\profiles.py:23`.

**Risk/impact:**

An audit that starts and ends at `upgrade.py` can understate the real
non-disruptive upgrade problem. The CTO adopter concern is not only "what does
upgrade manage today"; it is also "which scaffold-created artifacts can drift,
which are adopter-owned, which are safe to repair, and which have no upgrade
story." Without that inventory, the child-bridge catalog can omit whole file
classes or accidentally propose changes against adopter-owned files.

**Required action:**

Revise the scope to require a scaffold/template inventory table sourced from
`scaffold.py`, `profiles.py`, and `templates/`, not only `upgrade.py`. The
table should classify each scaffold-created artifact as one of:

- managed by upgrade today;
- repairable missing-file drift only;
- deliberately adopter-owned and never overwritten;
- unmanaged gap requiring a child bridge;
- out of scope with rationale.

The revised exit criteria should require this table in
`docs/reports/non-disruptive-upgrade-audit.md`.

### 3. Medium - Hook registration audit is under-specified

**Evidence:**

- The proposed child bridge for settings merge says to generalize beyond
  `PreToolUse` to `PostToolUse` / `Stop` / `UserPromptSubmit`:
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:110`.
- Fresh scaffold writes hook registrations for `SessionStart`,
  `UserPromptSubmit`, `PostToolUse`, and `PreToolUse`; it does not currently
  write a `Stop` event:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:353`.
- Current upgrade only has `_MANAGED_SETTINGS_PRETOOLUSE_HOOKS` and only
  repairs `scanner-safe-writer.py`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:66`.
- Doctor already checks several bridge-critical surfaces and skill files that
  rely on upgrade remediation being truthful:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:490`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:589`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:638`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:688`,
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\doctor.py:1026`.

**Risk/impact:**

The child-bridge preview can chase the wrong event taxonomy. Missing
`SessionStart` repair is at least as relevant as `Stop` because it is present
in the current scaffold. The audit should not pre-bake a settings child bridge
that omits a live event class and includes an event class with no current
scaffold evidence.

**Required action:**

Revise the investigation scope to require an event-by-event settings audit:
`SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreToolUse`, and any
additional Claude Code hook events only if supported by current template or
docs evidence. The eventual child bridge may still be called
`gtkb-upgrade-settings-merge`, but its scope should be derived from the audit,
not from the current preview list.

### 4. Medium - Child-bridge sequence lacks a managed-artifact registry step

**Evidence:**

- The current preview jumps directly to pre-flight, rollback, settings merge,
  changelog integration, interactive mode, workflows, and TOML migration:
  `bridge/gtkb-non-disruptive-upgrade-investigation-001.md:100`.
- Existing code already has split manifests that must stay synchronized:
  scaffold-time skill copy list in
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:28`
  and upgrade-time `_MANAGED_SKILLS` in
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\upgrade.py:52`.
- Prior Codex GO for the decision-capture skill explicitly warned that future
  skills must update both lists or consolidate the manifest:
  `bridge/gtkb-skill-decision-capture-010.md`, Condition 5.

**Risk/impact:**

Without an authoritative managed-artifact registry, each child bridge can add
another parallel list or one-off drift detector. That increases the chance of
future non-disruptive upgrade regressions: scaffold creates an artifact,
doctor warns about it, but upgrade either does not know it exists or treats it
with the wrong preservation semantics.

**Required action:**

Add an explicit investigation output and likely child bridge for a managed
artifact registry or manifest strategy. The investigation should decide
whether this registry is a prerequisite before workflow/settings/TOML repair
bridges, or whether those bridges can safely proceed with current lists.

## Non-Blocking Assessment

- Azure taxonomy parallelism is acceptable. I found no dependency requiring
  this investigation to wait for `gtkb-azure-enterprise-readiness-taxonomy`;
  Azure-specific upgrade concerns are reasonably excluded by the proposal.
- The current upgrade baseline is healthy enough for an investigation bridge.
  Targeted verification passed:

```text
python -m pytest tests/test_upgrade.py tests/test_upgrade_skills.py -q --tb=short
36 passed, 1 warning in 0.46s

python -m ruff check src/groundtruth_kb/project/upgrade.py tests/test_upgrade.py tests/test_upgrade_skills.py
All checks passed!
```

## Required Revision Bar

Prime should resubmit a revised proposal that:

1. Defines a verifiable KB-document deliverable, or removes/defer the local
   `groundtruth.db` insert from the bridge exit criteria.
2. Adds scaffold/template inventory as a first-class audit area and exit
   criterion.
3. Requires hook settings audit across the event classes present in the
   current scaffold, including `SessionStart`.
4. Adds managed-artifact registry/manifest strategy to the investigation
   outputs and child-bridge preview.
5. Keeps the no-code-change constraint for this investigation bridge.

## Verification Performed

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-non-disruptive-upgrade-investigation' -Context 8,40
Get-Content -Raw bridge/gtkb-non-disruptive-upgrade-investigation-001.md
Get-Content -Raw bridge/gtkb-hook-scanner-safe-writer-010.md
Get-Content -Raw bridge/gtkb-skill-decision-capture-009.md
Get-Content -Raw bridge/gtkb-skill-decision-capture-010.md
Get-Content -Raw bridge/gtkb-skill-decision-capture-012.md
Get-Content -Raw bridge/gtkb-v060-release-006.md
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

Test-Path groundtruth.toml
False

Test-Path groundtruth.db
True

git ls-files groundtruth.toml groundtruth.db
# no output

python -m pytest tests/test_upgrade.py tests/test_upgrade_skills.py -q --tb=short
36 passed, 1 warning in 0.46s

python -m ruff check src/groundtruth_kb/project/upgrade.py tests/test_upgrade.py tests/test_upgrade_skills.py
All checks passed!
```

## Decision Needed From Owner

None. Prime should revise the scope bridge and resubmit.

