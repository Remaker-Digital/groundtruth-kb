NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex Desktop default reasoning

# Post-Implementation Report - MCP Stable Harness Surface Current-Version Views

bridge_kind: implementation_report
Document: gtkb-mcp-stable-harness-surface-current-version-views
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Implemented from GO: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-004.md`
Approved proposal: `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md`
Implementation authorization packet: `sha256:250981da385ab727dceebda152743b8aa715ba0f19902977b0fcc6254c53218f`

## Implementation Claim

The approved MCP `current_role()` behavior is present and verified in the live checkout: list-form role-set values are normalized through `_canonical_role(...)` to a stable role token instead of being serialized as a Python list repr, legacy scalar role records still read as scalars, and the multi-role single-harness set has deterministic coverage.

During implementation start, the approved behavior and tests were already present in the current checkout. The remaining work inside the GO-authorized two-file scope was to make those files pass the current targeted quality gates: simplify the `role_map_path` assignment in `current_role()`, remove an unused `current_role` import and no-op monkeypatch loop in `test_t12_default_harness_id_does_not_hardcode_claude`, and run the project formatter on the two approved target files only.

Bridge filing also adds this post-implementation report as `bridge/gtkb-mcp-stable-harness-surface-current-version-views-005.md` and updates `bridge/INDEX.md` with a new `NEW:` line for Loyal Opposition verification.

## Files Changed In This Implementation Scope

- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` - verified role-set normalization via `_canonical_role(...)`; simplified the approved target file's `role_map_path` assignment and applied project formatting.
- `groundtruth-kb/tests/test_mcp_surface_foundation.py` - verified T6/T6b/T7/T9 coverage for singleton list role sets, multi-role sets, legacy scalar records, and MCP payload role string shape; removed an unused import/no-op loop and applied project formatting.

## Specification Links

- `ADR-0001` - three-tier memory architecture; the role surface reads canonical harness-state records.
- `GOV-08` - KB / harness-state is truth; `current_role` must report the role accurately from the canonical role-assignment record.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this implementation report as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - the MCP surface is a policy-engine consumer; a correct role token is required for role-aware response labelling.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - the list-form role-set is the active runtime schema; `current_role` consumes that schema.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all touched paths are under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal carried forward governing specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specs to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-3275 is the governed work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, bridge thread, and linked specs form the durable artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the prior NO-GO triggered this defect-fix proposal and verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured through WI, bridge thread, and spec-derived tests.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`, which approved `PAUTH-PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-MEMBASE-EFFECTIVE-USE-BATCH` and included work item `WI-3275`.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` and `WI-3275`.
- `DELIB-1467` - GT-KB MCP Stable Harness Surface Advisory.
- `DELIB-1880` - compressed bridge-thread record for the MCP stable harness surface advisory.
- `DELIB-1502` - Prime Advisory - GT-KB MCP Stable Harness Surface.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-003.md` - approved implementation proposal carried forward.
- `bridge/gtkb-mcp-stable-harness-surface-current-version-views-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Specification / behavior | Test or command | Observed result |
|---|---|---|
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001`; singleton list-form role-set records normalize to a scalar role token | `test_t6_current_role_reads_role_assignments_json` in `tests\test_mcp_surface_foundation.py` | PASS in full targeted suite |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001`; multi-role single-harness set is deterministic and never returns a list repr | `test_t6b_current_role_normalizes_multi_role_single_harness_set` | PASS in full targeted suite |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001`; legacy scalar `acting-prime-builder` remains read-compatible | `test_t7_current_role_accepts_acting_prime_builder_on_read` | PASS in full targeted suite |
| `SPEC-AUQ-POLICY-ENGINE-001`, `GOV-08`; MCP status payload exposes `current_role` as a plain string field | `test_t9_gt_status_summary_payload_includes_expected_fields` | PASS in full targeted suite |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; no regression across the MCP foundation suite | `python -m pytest tests\test_mcp_surface_foundation.py -q --tb=short` | 15 passed in 1.16s |
| Code quality for GO-authorized files | `python -m ruff check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py` | All checks passed |
| Formatting for GO-authorized files | `python -m ruff format --check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py` | 2 files already formatted |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-mcp-stable-harness-surface-current-version-views` - authorization packet issued; approved target paths were exactly `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py` and `groundtruth-kb/tests/test_mcp_surface_foundation.py`.
- `python -m pytest tests\test_mcp_surface_foundation.py -q --tb=short` - 15 passed in 1.16s.
- `python -m ruff check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py` - All checks passed.
- `python -m ruff format --check src\groundtruth_kb\mcp_surface\roles.py tests\test_mcp_surface_foundation.py` - 2 files already formatted.
- `python -m ruff check .` - failed on 12 existing issues outside the approved target files.
- `python -m ruff format --check .` - failed because 42 non-target files would be reformatted.

## Observed Results

The spec-derived MCP slice passes in the two approved files. The exact targeted verification evidence is:

```text
...............                                                          [100%]
15 passed in 1.16s
All checks passed!
2 files already formatted
```

Full-repository quality gates remain red, but the remaining failures are outside this GO's approved target paths. `python -m ruff check .` reports 12 issues in `src\groundtruth_kb\intake.py`, `src\groundtruth_kb\mcp_surface\authority.py`, `src\groundtruth_kb\mcp_surface\server.py`, `src\groundtruth_kb\project\doctor.py`, `src\groundtruth_kb\project\scaffold.py`, `tests\test_doctor_bridge_dispatch_liveness.py`, `tests\test_doctor_cross_harness_trigger.py`, and `tests\test_harness_lifecycle.py`. `python -m ruff format --check .` reports 42 non-target files requiring formatting. I did not modify those files because the implementation-start packet authorized only the two target paths above.

## Acceptance Criteria Status

1. IP-1 role-set normalization is present in `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`; `current_role()` returns `_canonical_role(record.get("role", "unknown"))`.
2. IP-2 coverage is present in `groundtruth-kb/tests/test_mcp_surface_foundation.py`; T6, T6b, T7, and T9 are included in the 15-passing targeted suite.
3. Target paths and verification commands reference only the live `groundtruth_kb/mcp_surface/` surface and `tests/test_mcp_surface_foundation.py`.
4. Legacy scalar role records still return scalar values.
5. Targeted ruff check and targeted format check pass for the two GO-authorized files.
6. Full-repository ruff check and format check are not clean because of unrelated non-target baseline issues; these were observed and preserved rather than repaired outside this bridge authorization.
7. This report cites the approved proposal's advisory and blocking specs for Loyal Opposition verification.

## Risks / Residual Notes

- The full-repository ruff gates remain red outside this implementation scope. A separate bridge proposal should authorize a repository-wide quality-baseline repair if the project wants the exact full `python -m ruff check .` and `python -m ruff format --check .` commands clean at repo scope.
- Formatter changes inside the two approved files are mechanical and intentionally limited to the GO-authorized target paths.
- Rollback path: revert the two approved target files to their previous revision; bridge audit files remain append-only.

## Recommended Commit Type

`fix:` - closes the MCP role-surface bridge thread by verifying and tightening the approved role-set normalization slice.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
