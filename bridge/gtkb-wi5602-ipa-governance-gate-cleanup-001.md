NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; WI-5492 follow-on: governance-gate cluster from background investigation agent

# Implementation Proposal - WI-5602: governance gates ungate writes to retired independent-progress-assessments/ directory

bridge_kind: prime_proposal
Document: gtkb-wi5602-ipa-governance-gate-cleanup
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5602

target_paths: ["scripts/controlled_artifact_paths.py", "scripts/implementation_authorization.py", "groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_protected_mutation_guard.py"]

implementation_scope: remove/replace stale governance-gate references to the retired independent-progress-assessments/ directory
requires_review: true
requires_verification: true
Recommended commit type: fix:

## Problem Statement

The owner directive (2026-07-17) retired `independent-progress-assessments/`
(contents deleted). WI-5492 and its sub-threads corrected the narrative
surfaces that named it (rules, skills, startup overlays). A background
investigation this session (Explore agent, read-only) surfaced a
higher-severity residual gap: five files in the GT-KB mutation-governance
machinery still treat the retired directory as a legitimate, currently-live,
ungated write target:

1. `scripts/controlled_artifact_paths.py` line 37-40:
   ```python
   ALLOWED_WRITE_PREFIXES = (
       "bridge/",
       "independent-progress-assessments/",
   )
   ```
   This classifier waves through any write under the retired directory as
   pre-approved/ungated (`is_controlled = False`).

2. `scripts/implementation_authorization.py` line 120-122: `PATH_TOKEN_RE`'s
   enumerated-directory alternation includes `independent-progress-assessments`
   alongside `scripts|groundtruth-kb/src|...|bridge|memory`, so prose
   mentioning the retired path is still recognized as a legitimate
   repo-path token by the authorization/preflight tooling that imports this
   regex.

3. `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py` line 107-122:
   `_PROTECTED_PREFIXES` lists `"independent-progress-assessments/"` (the
   retired name) but does NOT list either of the two current archive
   directories now on disk (`BARRED - DO NOT USE - independent-progress-
   assessments/` and `RETIRED-independent-progress-assessments/`, both
   defensively renamed rather than deleted, preserving historical content).
   Net effect: those two archive directories currently have NO protection
   from `gt hygiene reclaim`'s trash/purge operations.

4. `platform_tests/scripts/test_controlled_artifact_paths.py` line 78:
   `test_diagnostic_and_non_status_bridge_paths_remain_open` parametrizes
   `"independent-progress-assessments/report.md"` as a case that must remain
   "open" (uncontrolled), hard-asserting the stale allowance as correct
   behavior.

5. `platform_tests/scripts/test_protected_mutation_guard.py` line 115-123:
   `test_unprotected_targets_allowed` includes
   `"independent-progress-assessments/report.md"` in its unprotected-target
   list, same pattern as #4 in a different guard module.

This is the highest-severity finding of the follow-on investigation: it
means recreation of, or writes into, the retired directory are currently
mechanically *permitted* by two independent governance gates, directly
contradicting the owner directive that the directory "must not be read from
or recreated."

## Requirement Sufficiency

Existing requirements sufficient. This corrects governance-gate code to
match the already-established owner directive and the already-corrected
narrative surfaces (WI-5492); no new specification is required.

## Proposed Changes

### 1. `scripts/controlled_artifact_paths.py`

Remove the retired-directory entry from `ALLOWED_WRITE_PREFIXES`, leaving
only `bridge/`:

```python
ALLOWED_WRITE_PREFIXES = (
    "bridge/",
)
```

### 2. `scripts/implementation_authorization.py`

Remove `|independent-progress-assessments` from the `PATH_TOKEN_RE`
alternation (line 121), leaving the remaining enumerated prefixes
(`scripts|groundtruth-kb/src|groundtruth-kb/tests|platform_tests|tests|
config|.claude/skills|.codex/skills|.claude/hooks|.codex/gtkb-hooks|
.github|bridge|memory`) unchanged.

### 3. `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py`

Replace the retired-directory entry in `_PROTECTED_PREFIXES` (line 117)
with the two current archive directory names, so the historical content
they preserve is protected from `gt hygiene reclaim` trash/purge:

```python
_PROTECTED_PREFIXES = (
    ".claude/hooks/",
    ".claude/rules/",
    ".claude/session/",
    ".codex/gtkb-hooks/",
    ".github/workflows/",
    "BARRED - DO NOT USE - independent-progress-assessments/",
    "RETIRED-independent-progress-assessments/",
    "bridge/",
    "config/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "memory/",
    "platform_tests/",
    "scripts/",
    "tests/",
)
```
(alphabetical placement preserved per the existing tuple's ordering
convention; exact position adjusted to keep the tuple sorted.)

### 4. `platform_tests/scripts/test_controlled_artifact_paths.py`

Remove the `"independent-progress-assessments/report.md"` parametrize case
from `test_diagnostic_and_non_status_bridge_paths_remain_open` (line 78).
The remaining 5 cases (`bridge/design-note.md`, `bridge/example.md`, and
three `.gtkb-state/` diagnostic paths) already exercise the "non-status
bridge / diagnostic paths remain open" intent without relying on a prefix
that no longer exists in `ALLOWED_WRITE_PREFIXES`.

### 5. `platform_tests/scripts/test_protected_mutation_guard.py`

Remove `"independent-progress-assessments/report.md"` from the target list
in `test_unprotected_targets_allowed` (line 118), leaving
`["bridge/some-doc.md"]`, which still validates `allowed is True` /
`reason_code == "not_protected"` for a genuinely-unprotected path.

## Test Plan

- `python -m pytest platform_tests/scripts/test_controlled_artifact_paths.py -q --tb=short` — full suite, confirming the retired-path parametrize case is gone and all remaining cases still pass.
- `python -m pytest platform_tests/scripts/test_protected_mutation_guard.py -q --tb=short` — full suite, confirming `test_unprotected_targets_allowed` still passes with the trimmed target list.
- Manual verification: `classify_controlled_artifact("independent-progress-assessments/report.md")` should now return `is_controlled=True` (or otherwise fall through to the default-protected path) rather than being explicitly waved through.
- Manual verification: a disposable-index or dry-run check that `gt hygiene reclaim plan` (or equivalent read-only preview) now lists both current archive directory names as protected, not the retired name.
- Grep confirmation: `scripts/implementation_authorization.py` no longer contains the literal string `independent-progress-assessments` after the edit.

## Specification-Derived Verification

| Spec | Verification |
| --- | --- |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Both test files run via `python -m pytest` with exit 0 reported in the post-implementation report. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Specification Links below cite every relevant governing spec. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Filed through the governed no-index bridge writer path under an active work-intent claim. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Project and Work Item declared above; WI-5602 added to PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE via `gt projects add-item`. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All 5 target_paths exist on disk and resolve inside `E:\GT-KB`. |
| GOV-STANDING-BACKLOG-001 | WI-5602 tracked in MemBase `work_items`, origin=defect, priority=P1. |

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-STANDING-BACKLOG-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Owner Decisions / Input

- The original WI-5492 retirement directive: "independent-progress-assessments directory has been retired. All contents are deleted... drive this program to conclusion and finish removing all references to the deleted directory and correcting all load-bearing artifacts which referenced it."
- This proposal's existence is itself the direct continuation of that standing directive, surfaced via a background investigation this session and confirmed against live source (exact line numbers read fresh, not assumed).

## Prior Deliberations

- DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT
- bridge/gtkb-retire-ipa-refs-config-gitignore-001.md through -006.md (VERIFIED)
- bridge/gtkb-retire-ipa-refs-rules-skills-001.md through -012.md (VERIFIED)
- bridge/gtkb-retire-ipa-refs-skill-projections-001.md through -005.md


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Acceptance Criteria

- `scripts/controlled_artifact_paths.py`'s `ALLOWED_WRITE_PREFIXES` contains only `"bridge/"`.
- `scripts/implementation_authorization.py`'s `PATH_TOKEN_RE` no longer contains the literal string `independent-progress-assessments`.
- `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py`'s `_PROTECTED_PREFIXES` protects both current archive directory names instead of the retired name.
- Both updated test files pass under `python -m pytest`.
- `ruff check` and `ruff format --check` pass on all 5 changed files.

## Risk And Rollback

Low-to-moderate risk: this narrows an over-broad allowlist/protection-list,
which could theoretically surface a FAIL somewhere else in the suite if
another test relied on the retired-directory allowance incidentally (full
targeted test runs above are designed to catch this). Rollback is a simple
revert of the 5 files; no other system state depends on the change.
