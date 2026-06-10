REVISED

# Implementation Report Revision - Implementation-Start Target-Paths Preflight

bridge_kind: implementation_report
Document: gtkb-impl-start-target-paths-preflight
Version: 008
Author: Prime Builder (Codex, harness A)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-impl-start-target-paths-preflight-007.md (NO-GO)
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Work Item: WI-3380

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-pb-2026-06-04T16-48Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Prime Builder implementation revision

target_paths: ["scripts/impl_start_target_paths_preflight.py", "groundtruth-kb/tests/test_impl_start_target_paths_preflight.py", ".claude/hooks/bridge-compliance-gate.py"]
requires_verification: true
implementation_scope: code_fix

## Revision Claim

This revision corrects the root-boundary defect identified by Loyal Opposition
in `bridge/gtkb-impl-start-target-paths-preflight-007.md`.

The target-path preflight no longer converts root-escape candidate syntax such
as `../scripts/impl_start_target_paths_preflight.py` into an approved in-root
path. The implementation now preserves explicit out-of-root syntax for display
and rejects traversal-shaped candidates before matching them against approved
`target_paths`.

## Specification Links

| Spec | Severity | How this revision complies |
|------|----------|----------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | Files this response as the next append-only bridge version and relies on the live `bridge/INDEX.md` chain. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | Keeps the operative GO'd proposal's spec linkage and repeats the directly relevant specs here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | Adds and executes root-boundary regression tests derived from the NO-GO finding and linked isolation spec. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | Rejects explicit root-escape and absolute outside-root candidates instead of normalizing them into approved in-root paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | Keeps the fix within the active WI-3380 authorization and GO-approved target paths. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | Preserves the existing PAUTH-scoped source/test/hook target path envelope. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | Treats the NO-GO, source correction, tests, and implementation response as durable artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | Preserves traceability across the NO-GO, code correction, regression tests, and revised implementation report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | Keeps the blocked-to-revised lifecycle transition explicit in the bridge thread before verification. |

## Prior Deliberations

- `bridge/gtkb-impl-start-target-paths-preflight-004.md` - operative revised
  proposal with PAUTH correction and approved target paths.
- `bridge/gtkb-impl-start-target-paths-preflight-005.md` - Loyal Opposition GO
  authorizing implementation.
- `bridge/gtkb-impl-start-target-paths-preflight-006.md` - implementation
  report that introduced the target-path preflight.
- `bridge/gtkb-impl-start-target-paths-preflight-007.md` - operative NO-GO
  requiring root-boundary correction.

No new owner decision is needed. The correction stays within the GO-approved
implementation surface and existing WI-3380 authorization.

## Findings Addressed

### P1 - Out-of-root candidate syntax is no longer normalized into an approved target

Changes made:

1. `_normalize_candidate()` now preserves explicit fallback syntax with only
   slash normalization. It no longer strips leading `./` or `../` segments.
2. `_match_against_targets()` now rejects traversal-shaped candidates before
   delegating to `path_authorized()`.
3. Regression tests cover:
   - `../scripts/impl_start_target_paths_preflight.py`;
   - an absolute path outside the fixture project root;
   - an in-root non-existing relative path that should still normalize and
     match approved `target_paths`.

The corrected reproduction now prints distinct values:

```text
../scripts/impl_start_target_paths_preflight.py
scripts/impl_start_target_paths_preflight.py
```

The live CLI smoke now returns `out_of_scope_drift` with exit code 5 for the
root-escape candidate, and returns `in_scope` with exit code 0 for the approved
repo-relative candidate.

## Files Changed

- `scripts/impl_start_target_paths_preflight.py`
- `groundtruth-kb/tests/test_impl_start_target_paths_preflight.py`

`.claude/hooks/bridge-compliance-gate.py` remains in the approved target path
set from the GO'd proposal but did not require an additional source change for
this revision.

## Specification-Derived Verification

Executed from `E:\GT-KB`:

| Requirement | Verification | Result |
|-------------|--------------|--------|
| Root-escape candidates remain out of scope | `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_impl_start_target_paths_preflight.py -q --tb=short --basetemp=.gtkb-state\tmp\pytest-target-paths` | PASS: 24 passed, 1 cache warning |
| Source formatting and lint stay clean | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\impl_start_target_paths_preflight.py groundtruth-kb\tests\test_impl_start_target_paths_preflight.py .claude\hooks\bridge-compliance-gate.py` | PASS |
| Formatting remains stable | `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\impl_start_target_paths_preflight.py groundtruth-kb\tests\test_impl_start_target_paths_preflight.py .claude\hooks\bridge-compliance-gate.py` | PASS |
| Exact NO-GO reproduction is corrected | `groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from scripts.impl_start_target_paths_preflight import _normalize_candidate; root=Path('.').resolve(); print(_normalize_candidate(root, '../scripts/impl_start_target_paths_preflight.py')); print(_normalize_candidate(root, 'scripts/impl_start_target_paths_preflight.py'))"` | PASS: distinct root-escape and in-root display |
| Live CLI rejects root escape | `groundtruth-kb\.venv\Scripts\python.exe scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --candidate-paths ../scripts/impl_start_target_paths_preflight.py --json` | PASS: exit 5, `verdict=out_of_scope_drift` |
| Live CLI accepts approved in-root candidate | `groundtruth-kb\.venv\Scripts\python.exe scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --candidate-paths scripts/impl_start_target_paths_preflight.py --json` | PASS: exit 0, `verdict=in_scope` |
| Bridge applicability stays clean | `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight` | PASS |

## Risk And Rollback

Risk is low. The change narrows matching behavior only for explicit traversal
or outside-root candidates; normal in-root relative paths continue to normalize
and match approved `target_paths`.

Rollback is the normal source revert of the two changed files plus this bridge
revision. No database, approval packet, hook registration, or deployment state
was changed by this correction.

## Recommended Outcome

VERIFIED after Loyal Opposition reruns the focused tests and live CLI smoke.
