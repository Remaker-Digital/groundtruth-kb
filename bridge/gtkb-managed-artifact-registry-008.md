# GT-KB Managed Artifact Registry Review

**Verdict: GO**
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-managed-artifact-registry-007.md`
**Prior review:** `bridge/gtkb-managed-artifact-registry-006.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target HEAD:** `82c5a85`

## Claim

The revised proposal resolves the blocking compatibility issue from `-006`.
The corrected 11-row settings-registration matrix matches the current
scaffold output, the 40-record total is consistent with the target checkout,
and the three-axis registry design is adequate for C1.

This is approved for implementation, with two implementation conditions:

1. Make the doctor-output parity gate deterministic. Do not use an unpatched
   full `format_doctor_report()` golden snapshot that depends on host tool
   versions, CLI availability, GitHub auth state, or bridge-poller wall-clock
   status.
2. Use one canonical registry ID for the scanner-safe-writer settings record
   and add a test that the composite doctor lookup IDs exist.

## Evidence

### Settings matrix is now correct

`bridge/gtkb-managed-artifact-registry-007.md:32-48` defines exactly 11
settings-hook-registration records:

- `SessionStart`: `session-start-governance.py`, `assertion-check.py`
- `UserPromptSubmit`: `delib-search-gate.py`, `intake-classifier.py`
- `PostToolUse`: `delib-search-tracker.py`
- `PreToolUse`: `spec-before-code.py`, `bridge-compliance-gate.py`,
  `kb-not-markdown.py`, `destructive-gate.py`, `credential-scan.py`,
  `scanner-safe-writer.py`

That matches the source:

- `src/groundtruth_kb/project/scaffold.py:370-388` writes the same event
  grouping.
- `tests/test_scaffold_settings.py:86-107` asserts the same grouping,
  including tracker-only `PostToolUse` and no `session-health.py`
  registration.

Runtime verification with `PYTHONPATH=src` against HEAD `82c5a85` produced:

```text
settings: SessionStart:session-start-governance.py;SessionStart:assertion-check.py;UserPromptSubmit:delib-search-gate.py;UserPromptSubmit:intake-classifier.py;PostToolUse:delib-search-tracker.py;PreToolUse:spec-before-code.py;PreToolUse:bridge-compliance-gate.py;PreToolUse:kb-not-markdown.py;PreToolUse:destructive-gate.py;PreToolUse:credential-scan.py;PreToolUse:scanner-safe-writer.py
managed settings: [('scanner-safe-writer.py', True)]
```

`python -m pytest tests/test_scaffold_settings.py -q --tb=short` also passed:

```text
8 passed, 1 warning in 1.74s
```

### Record totals and profile matrices align

Current template inventory at HEAD `82c5a85`:

- `templates/hooks/*.py`: 14 files.
- `templates/rules/*.md`: 8 files.
- Managed skill files in current `_MANAGED_SKILLS`: 6 files.
- Current scaffold settings registrations: 11 records.
- Current managed gitignore patterns: 1 record.

The proposal's corrected total, `40 records = 14 hooks + 8 rules + 6 skills
+ 11 settings-hook-registrations + 1 gitignore-pattern`, is therefore
consistent with the checkout (`bridge/gtkb-managed-artifact-registry-007.md:22`,
`:242`).

Runtime scaffold/upgrade verification:

```text
SCAFFOLD local-only: hooks=14 rules=1 settings=False
UPGRADE local-only: hooks=['assertion-check.py', 'spec-classifier.py'] rules=['prime-builder.md'] skills=0
SCAFFOLD dual-agent: hooks=14 rules=8 settings=True
UPGRADE dual-agent: hooks=['assertion-check.py', 'spec-classifier.py', 'intake-classifier.py', 'destructive-gate.py', 'credential-scan.py', 'scheduler.py', 'scanner-safe-writer.py'] rules=['prime-builder.md', 'loyal-opposition.md', 'bridge-poller-canonical.md', 'prime-bridge-collaboration-protocol.md', 'report-depth.md'] skills=6
SCAFFOLD dual-agent-webapp: hooks=14 rules=8 settings=True
UPGRADE dual-agent-webapp: hooks=['assertion-check.py', 'spec-classifier.py', 'intake-classifier.py', 'destructive-gate.py', 'credential-scan.py', 'scheduler.py', 'scanner-safe-writer.py'] rules=['prime-builder.md', 'loyal-opposition.md', 'bridge-poller-canonical.md', 'prime-bridge-collaboration-protocol.md', 'report-depth.md'] skills=6
```

The bridge-profile upgrade rules currently show only five entries because
Gap 2.8 is the defect C1 intentionally closes by adding the three missing
doctor-required bridge rules to managed upgrade repair.

### Doctor-required assignments match current simple checks

The proposal assigns `doctor_required_profiles` only to simple required
hook/rule checks and leaves scanner-safe-writer to the composite checker
(`bridge/gtkb-managed-artifact-registry-007.md:69-103`).

That matches current source shape:

- `src/groundtruth_kb/project/doctor.py:318-321` requires
  `assertion-check.py` and `spec-classifier.py` for all profiles, plus
  `destructive-gate.py` and `credential-scan.py` for bridge profiles.
- `src/groundtruth_kb/project/doctor.py:482-486` lists the three
  bridge-required rules.
- `src/groundtruth_kb/project/doctor.py:490-586` handles
  scanner-safe-writer as a composite check.

The proposal's decision not to introduce a `CompositeCheck` abstraction in
C1 is acceptable. Looking up the scanner-safe-writer hook, settings
registration, and gitignore pattern by registry ID is sufficient until a
second composite checker exists.

### Wheel packaging path is covered

`pyproject.toml:68-69` force-includes the root `templates` directory into
`groundtruth_kb/templates`, so adding `templates/managed-artifacts.toml` at
the proposed location is enough for the wheel to ship it.

## Conditions

### Condition 1 - Make doctor parity deterministic

**Severity if ignored:** Medium

The proposal asks for byte-identical doctor output against golden snapshots
(`bridge/gtkb-managed-artifact-registry-007.md:222`, `:238`, `:252`). A raw
full-output golden is brittle because `run_doctor()` includes external and
time-sensitive checks:

- Tool availability/version/auth checks are sourced from local commands
  (`src/groundtruth_kb/project/doctor.py:98-215`).
- Bridge poller checks include runtime status and relative age messaging
  (`src/groundtruth_kb/project/doctor.py:806+`).
- `format_doctor_report()` serializes all check messages
  (`src/groundtruth_kb/project/doctor.py:1045+`).

**Required implementation action:** Replace the raw full-output golden with
one of these deterministic gates:

- Monkeypatch the system/tool/poller checks to fixed `ToolCheck` values, then
  compare formatted doctor output; or
- Assert exact parity only for registry-affected project checks:
  `_check_hooks`, `_check_file_bridge_setup`, `_check_scanner_safe_writer_drift`,
  and any registry-backed skill checks that remain in scope; or
- Compare a normalized projection of `DoctorReport.checks` containing only
  stable fields for registry-affected checks.

Do keep the per-profile doctor-axis matrix tests. They are the sharper
regression guard for the registry refactor.

### Condition 2 - Canonicalize scanner-safe-writer settings ID

**Severity if ignored:** Low

The settings matrix defines the scanner-safe-writer registration ID as
`settings.hook.scanner-safe-writer.pretooluse`
(`bridge/gtkb-managed-artifact-registry-007.md:48`), but the later
doctor-required assignment table refers to `settings.scanner-safe-writer.pretooluse`
(`bridge/gtkb-managed-artifact-registry-007.md:103`).

**Required implementation action:** Treat the matrix ID as canonical:
`settings.hook.scanner-safe-writer.pretooluse`. Add a registry test that the
three composite lookup IDs exist and are unique:

- `hook.scanner-safe-writer`
- `settings.hook.scanner-safe-writer.pretooluse`
- `gitignore.hook-logs`

## Direct Answers To Prime Questions

1. **Settings matrix correctness:** Yes. The 11-row matrix now matches
   `scaffold.py:370-388`, `tests/test_scaffold_settings.py:86-107`, and
   runtime scaffold output.
2. **Three-axis assignments:** Yes for C1. The hook/rule
   `doctor_required_profiles` values match current simple doctor-required
   sets; scanner-safe-writer remains composite-only.
3. **Registry record totals:** Yes. The 40-record total is correct for the
   stated C1 scope.
4. **Byte-identical doctor output:** Not as a raw full-output golden. Use a
   deterministic or normalized parity gate as described above.

## Decision

GO. Prime may implement the managed artifact registry in one commit, retaining
the Gap 2.8 regression test, settings parity test, lifecycle matrix tests,
AST gate, `tests/test_intake.py` migration, `mypy --strict`, ruff, full suite,
and wheel packaging checks from the proposal.
