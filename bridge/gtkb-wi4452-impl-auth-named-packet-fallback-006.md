NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Implementation Report - WI-4452 Implementation Authorization Named-Packet Fallback

bridge_kind: implementation_report
Document: gtkb-wi4452-impl-auth-named-packet-fallback
Version: 006
Responds-To: bridge/gtkb-wi4452-impl-auth-named-packet-fallback-005.md
GO-Verdict: bridge/gtkb-wi4452-impl-auth-named-packet-fallback-005.md
Approved-Proposal: bridge/gtkb-wi4452-impl-auth-named-packet-fallback-004.md
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4452
Related Work Item: WI-4443 (related-only; no automatic retirement requested)
target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py"]

Implementation authorization packet:
`sha256:ac1e219b065e27af866e8b7861b0fbe6592c078531e61a3357885af32e76bdb3`

## Implementation Claim

Implemented the approved WI-4452 named-packet fallback fix.

`scripts/implementation_authorization.py::validate_targets()` now normalizes
the protected target set once, accepts a valid `current.json` packet when it
authorizes all targets, otherwise scans
`.gtkb-state/implementation-authorizations/by-bridge/*.json` through
`load_named_packet()` and uses the single valid named packet that authorizes
all targets. The resolver fails closed if no valid packet matches or if
multiple valid named packets authorize the same protected target set.

This preserves the bridge GO requirement, packet expiry validation, GO-file
drift checks, post-GO chain checks, target-path scope checks, and
project-authorization drift checks because every fallback candidate is loaded
through the existing `load_named_packet()` validation path.

`scripts/implementation_start_gate.py` required no source change: the existing
gate path already reports `AuthorizationError` messages from `validate_targets()`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected mutations still require a valid live bridge GO authorization packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the bridge/work-item lifecycle is preserved through this report and the eventual VERIFIED closure path.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-4452 is handled as a small reliability fix under the standing fast-lane PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation stayed inside the approved target paths and carries forward project/work metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is regression-driven and mapped below.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - fallback can select only already-issued, still-valid GO packets and fails closed on ambiguity.
- `GOV-STANDING-BACKLOG-001` - WI-4452 closure is deferred until Loyal Opposition records VERIFIED; WI-4443 remains related-only.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the old current-json-only test contract was explicitly superseded by a bridge-reviewed defect fix.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this report supplies the implementation evidence needed for downstream VERIFIED reconciliation.

## Owner Decisions / Input

No new owner decision was required. Work is covered by
`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` and
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for active reliability project
member `WI-4452`.

## Prior Deliberations And Backlog Evidence

- `bridge/gtkb-wi4452-impl-auth-named-packet-fallback-004.md` - approved revised proposal.
- `bridge/gtkb-wi4452-impl-auth-named-packet-fallback-005.md` - Loyal Opposition GO verdict.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization.
- `WI-4452` - primary P0 defect evidence.
- `WI-4443` - related-only sibling defect; no terminal mutation requested by this implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Gate tests prove a unique valid named packet authorizes a protected mutation and overlapping named packets block as ambiguous. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This implementation report carries the proposal, GO, WI-4452, and related-only WI-4443 evidence forward without mutating backlog state. |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff is limited to implementation-start authorization reliability logic and tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Changed files are limited to approved target paths; `scripts/implementation_start_gate.py` was checked but did not require edits. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full focused pytest pair passed after formatting: 174 tests. Ruff check and format-check passed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Fallback uses `load_named_packet()` for every candidate and fails closed on ambiguity rather than guessing. |
| `GOV-STANDING-BACKLOG-001` | Closure recommendation is WI-4452 only after VERIFIED; WI-4443 remains related-only unless separately authorized. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi4452-impl-auth-named-packet-fallback
```

Result: PASS; packet hash `sha256:ac1e219b065e27af866e8b7861b0fbe6592c078531e61a3357885af32e76bdb3`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
```

Result: PASS; 174 passed in 18.29s.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py
```

Result: PASS; all checks passed.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py
```

Result: PASS; 4 files already formatted.

## Files Changed

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `bridge/INDEX.md`

Checked but unchanged:

- `scripts/implementation_start_gate.py`

## Diff Summary

```text
platform_tests/scripts/test_implementation_authorization.py   | 34 +++++++++-
platform_tests/scripts/test_implementation_start_gate.py      | 73 +++++++++++++++-------
scripts/implementation_authorization.py                       | 57 +++++++++++++++--
3 files changed, 135 insertions(+), 29 deletions(-)
```

## Acceptance Criteria Status

- [x] Two concurrent GO bridge packets with disjoint `target_paths` can both authorize their own protected mutations after the second `begin` overwrites `current.json`.
- [x] A valid named packet alone can authorize a protected mutation only when it is the unique valid named packet covering all protected targets.
- [x] Multiple valid named packets covering the same protected target block with an ambiguity reason and name both candidate bridge IDs.
- [x] Existing missing-packet, out-of-scope target, expired packet, post-GO review freeze, and project-authorization drift protections remain covered by the focused test files.
- [x] WI-4452 can be linked to the final VERIFIED bridge thread for mechanical backlog reconciliation.
- [x] WI-4443 remains related-only unless separately authorized or project-membered.

## Work Item Resolution Recommendation

If Loyal Opposition verifies this report, link `WI-4452` to the final VERIFIED
bridge verdict and let the bridge-verified backlog reconciliation path resolve
WI-4452 only. Do not retire `WI-4443` under this thread.

## Risk And Rollback

Residual risk is bounded to authorization selection. The implementation avoids
broadening authorization by validating every fallback candidate with the same
packet invariants and requiring exactly one match.

Rollback: revert the three changed files. Bridge files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the approved revised proposal and command evidence.
2. Confirm that ambiguity fails closed and that WI-4443 is not claimed for retirement.
3. Return `VERIFIED` if satisfied; otherwise return `NO-GO` with findings.
