NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ec695-8ccc-7941-9cbb-76c8f4d7a4ff
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; session role marker restored for owner-declared ::init gtkb pb before GO implementation claim.

# Implementation Report - WI-4548 AXIS-2 ADVISORY Surface Fix

bridge_kind: implementation_report
Document: gtkb-wi4548-axis-2-advisory-surface
Version: 004
Author: Prime Builder (Codex, harness A)
Date: 2026-06-14 UTC

Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION-IMPL
Project: PROJECT-GTKB-BRIDGE-KIND-TAXONOMY-STABILIZATION
Work Item: WI-4548

Responds to GO: bridge/gtkb-wi4548-axis-2-advisory-surface-003.md
Approved proposal: bridge/gtkb-wi4548-axis-2-advisory-surface-002.md

## Implementation Claim

Implemented the AXIS-2 ADVISORY surfacing fix approved in version 003.
`.claude/hooks/bridge-axis-2-surface.py` now keeps ADVISORY entries visible to
the Prime AXIS-2 surface even when `dispatchable=False`, while preserving the
existing compatibility-safe default and terminal-kind GO suppression.

Added a regression test proving an ADVISORY latest-status fixture with
`bridge_kind: loyal_opposition_advisory` is returned by
`_compute_actionable_for_role(ROLE_PRIME)`.

## Files Changed For WI-4548

- `.claude/hooks/bridge-axis-2-surface.py`
- `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py`
- `bridge/gtkb-wi4548-axis-2-advisory-surface-001.md`
- `bridge/gtkb-wi4548-axis-2-advisory-surface-002.md`
- `bridge/gtkb-wi4548-axis-2-advisory-surface-003.md`
- `bridge/gtkb-wi4548-axis-2-advisory-surface-004.md`
- `bridge/INDEX.md`

The worktree contains unrelated dirty and untracked files from other bridge
threads; they are not part of this implementation report.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-ADVISORY-ROUTING-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
|---|---|
| `DCL-ADVISORY-ROUTING-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | New regression `test_advisory_entry_surfaces_despite_non_dispatchable` confirms ADVISORY appears in Prime AXIS-2 items despite non-dispatchability. |
| Terminal-kind suppression from WI-4278 / `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing governance-review GO regression remains in the focused AXIS-2 lane and passed. |
| Role-aware AXIS-2 contract | `platform_tests/hooks/test_bridge_axis_2_role_aware.py` included in the focused lane and passed. |
| Work-intent visibility contract | `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` included in the focused lane and passed. |
| Hook runtime behavior | `platform_tests/scripts/test_bridge_axis_2_surface.py` included in the focused lane and passed. |

## Commands Run

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py platform_tests\hooks\test_bridge_axis_2_surface_work_intent.py platform_tests\hooks\test_bridge_axis_2_role_aware.py platform_tests\scripts\test_bridge_axis_2_surface.py -q --tb=short
```

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude\hooks\bridge-axis-2-surface.py platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py
```

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .claude\hooks\bridge-axis-2-surface.py platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py
```

## Observed Results

- Focused pytest lane: `34 passed, 1 warning in 36.91s`.
- Pytest warning: existing `PytestConfigWarning: Unknown config option: asyncio_mode`.
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`.

## Acceptance Criteria Status

- ADVISORY entries in Prime AXIS-2 items are included even when
  `dispatchable=False`: PASS.
- Non-ADVISORY `dispatchable=False` entries, especially terminal-kind GO
  entries such as `governance_review`, remain excluded: PASS.
- Existing role-aware, work-intent, cache/dismissal, and emergency-stop behavior
  does not regress in the focused lane: PASS.
- No headless dispatch consumer changed and no ADVISORY entry was made
  dispatchable: PASS.

## Risk / Rollback

Risk is low and isolated to the AXIS-2 prompt surface predicate. Rollback is to
revert `.claude/hooks/bridge-axis-2-surface.py` and the associated regression
test changes; no schema, KB, hook registration, or headless dispatch code was
changed.
