REVISED

# gtkb-wi-4251-diagnostic-write-envelope — Allow wrap and hygiene diagnostic writes without opening protected mutation paths

bridge_kind: prime_proposal
Document: gtkb-wi-4251-diagnostic-write-envelope
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: `bridge/gtkb-wi-4251-diagnostic-write-envelope-002.md` (Codex LO NO-GO)
Carries-Forward: `bridge/gtkb-wi-4251-diagnostic-write-envelope-001.md`

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: hygiene-sweep-automation-2026-06-12
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; workspace-write; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4251

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate_diagnostic_write_envelope.py"]

implementation_scope: protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Summary

This REVISED proposal addresses all three NO-GO findings from `-002`:

1. It adds a dedicated non-bulk scope section with the detector evidence tokens needed to keep `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` out of the gate-failing path.
2. It adds `GOV-RELIABILITY-FAST-LANE-001` plus an explicit fast-lane eligibility mapping, since the standing PAUTH is the authorization basis.
3. It narrows the test surface from modifying an existing test module to adding one new focused regression module, keeping the work inside the standing PAUTH mutation classes (`source` + `test_addition`).

The underlying defect statement and source-file repair remain unchanged.

## Summary

This proposal implements `WI-4251` by narrowing one implementation-start gate false-positive class: wrap and hygiene capture commands that only write diagnostic artifacts under `.groundtruth/session/snapshots/**` or `.gtkb-state/**` are currently treated like protected-source mutation because the gate sees the protected script path (`scripts/wrap_capture_transcript.py`, `scripts/wrap_scan_hygiene.py`, `scripts/wrap_scan_consistency.py`) but does not model the actual output surface precisely enough.

The change stays intentionally narrow. It does not relax protection for `scripts/`, `config/`, `platform_tests/`, or other protected source surfaces. Instead, it teaches `scripts/implementation_start_gate.py` to recognize the specific in-root diagnostic output envelope used by the wrap/hygiene tools and to allow commands only when every discovered write target falls inside that diagnostic envelope. Mixed commands that touch both diagnostic outputs and protected paths must continue to block without an authorization packet.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the gate change must be approved and tracked through a canonical bridge thread because it changes protected-mutation enforcement behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposal makes the exact gate change and verification surface explicit before any protected source mutation occurs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the packet carries the required `Project Authorization`, `Project`, and `Work Item` metadata for implementation work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the gate change is verified by focused regression tests proving both the intended allow path and preserved deny paths.
- `GOV-STANDING-BACKLOG-001` — `WI-4251` is a standing backlog defect and this proposal is explicitly non-bulk, single-work-item work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the proposal preserves the implementation-start gate’s protected-source deny behavior and does not create a bypass path.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the standing reliability-fixes PAUTH is the authorization envelope for the repair.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the implementation stays inside the declared project/work-item/target-path envelope.
- `GOV-RELIABILITY-FAST-LANE-001` — the proposal relies on the standing fast-lane PAUTH and therefore must show why this defect fits that eligibility contract.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the wrap/hygiene tools create runtime evidence artifacts, not protected source mutations; the gate must distinguish those classes without silently broadening other lifecycle transitions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the allowed diagnostic outputs remain in-root under the canonical GT-KB runtime-evidence locations.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the repair preserves the boundary between governed source changes and scanner/runtime evidence artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the source change, the new regression module, the implementation report, and the resulting WI closure remain one durable artifact chain.

## Prior Deliberations

- `bridge/gtkb-implementation-gate-friction-hygiene-022.md` — verified prior implementation-start gate hygiene lineage; this proposal is a narrower follow-on, not a restart of the broader thread.
- `WI-4251` backlog row (`python -m groundtruth_kb backlog show WI-4251 --json`) — captures the specific defect statement for read-only wrap and hygiene capture under the implementation-start gate.
- `platform_tests/scripts/test_wrap_capture_transcript.py`, `platform_tests/scripts/test_wrap_scan_hygiene.py`, and `platform_tests/scripts/test_wrap_scan_consistency.py` — existing tool behavior confirms the intended write surfaces are diagnostic outputs, not source edits.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision authorizing the standing reliability fast-lane path used by the cited PAUTH.
- `_No exact Deliberation Archive hits surfaced for the literal WI-4251 query on 2026-06-12; this proposal relies on the live backlog item plus the verified implementation-gate hygiene thread as the governing lineage._`

## Owner Decisions / Input

Owner directive on 2026-06-12: "Please proceed with the cleanup plan and WI-4250 and WI-4251." No additional owner decision is required before review because the repair sits inside `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` and the revised target-path shape does not change project scope beyond the already-open defect.

## Requirement Sufficiency

Existing requirements sufficient. `WI-4251` already defines the defect and the acceptance boundary: wrap capture and hygiene/consistency scan commands may write their diagnostic outputs without implementation authorization, while source/config/test writes must remain blocked. This proposal only translates that requirement into a concrete gate change and regression-test shape.

## Fast-Lane Eligibility

This proposal is eligible for `GOV-RELIABILITY-FAST-LANE-001` because it is a small, bounded defect repair:

- one source file under `scripts/implementation_start_gate.py`;
- one new focused regression test file, not a broad test-suite rewrite;
- no KB mutation, no deploy, no spec deletion, no force-push, and no cross-project application edits;
- a single defect scope: diagnostic-write classification for wrap/hygiene commands.

The proposal does NOT rely on test modification, CLI extension, or batch governance operations.

## Non-Bulk Scope Clarification

This thread is NOT a backlog bulk operation.

- Scope is one work item (`WI-4251`), one review packet, one source file, and one new regression test file.
- No inventory sweep is performed.
- No review-packet bundle is performed.
- No `DECISION DEFERRED` marker is needed because no Phase/Path-deferred bulk action is being proposed.
- No formal-artifact-approval packet is required for a bulk action because this is not a bulk action.

This section is included to make the non-bulk scope explicit for `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` classification.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use only synthetic command strings and local test fixtures; no credentials in fixtures or output paths. | Focused pytest and helper credential scan. | |
| CQ-PATHS-001 | Yes | Keep all changes inside one gate file and one new test file; allow only in-root diagnostic output surfaces. | Target-path review plus focused pytest. | |
| CQ-COMPLEXITY-001 | Yes | Add the narrowest command/path classification change that unblocks wrap/hygiene diagnostics without relaxing protected-source enforcement. | New allow/deny regression tests. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing protected-prefix and runtime-output constants where possible instead of inventing parallel classifiers. | Source inspection and focused pytest. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for any command that also touches protected paths or unknown mutating targets. | Mixed-write deny regression tests. | |
| CQ-DOCS-001 | Yes | Express the envelope precisely in bridge evidence and tests; no prose-only behavior change. | Proposal mapping plus focused pytest. | |
| CQ-TESTS-001 | Yes | Add one new regression file for allowed diagnostic writes and preserved protected-write blocks. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate_diagnostic_write_envelope.py -q --tb=short --basetemp=.gtkb-state/pytest-tmp-wi-4251`. | |
| CQ-LOGGING-001 | Yes | Do not add new logging noise to the gate; preserve existing reason strings except where the new classification requires a clear decision. | Source inspection and focused pytest output assertions. | |
| CQ-VERIFICATION-001 | Yes | Require focused regression evidence before any implementation report claims closure. | Commands listed in the verification plan. | |

## Files Expected To Change

| Path | Status | Purpose |
|---|---|---|
| `scripts/implementation_start_gate.py` | modified | Recognize the bounded diagnostic-write envelope for wrap/hygiene commands while preserving protected-source deny behavior. |
| `platform_tests/scripts/test_implementation_start_gate_diagnostic_write_envelope.py` | new | Focused regression coverage for allowed diagnostic-write commands and preserved deny cases. |

## Specification-Derived Verification Plan

| Specification | Verification command or test | Expected result |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_start_gate_diagnostic_write_envelope.py -q --tb=short --basetemp=.gtkb-state/pytest-tmp-wi-4251` | New focused gate suite passes with allow/deny regression coverage. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Regression tests prove wrap/hygiene commands writing only `.groundtruth/session/snapshots/**` or `.gtkb-state/**` are allowed while mixed protected-path writes still block. | Allow path opens only for diagnostic outputs; bypass path remains denied. |
| `GOV-RELIABILITY-FAST-LANE-001` | Source/test scope inspection plus the target-path list in this proposal. | Proposal remains a small bounded defect repair inside the standing fast-lane envelope. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Regression tests prove diagnostic artifacts are treated as runtime evidence surfaces, not protected source mutation. | Runtime-evidence writes are allowed only in the approved envelope. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Source inspection of `scripts/implementation_start_gate.py` and focused tests. | No out-of-root or `applications/**` paths are introduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi-4251-diagnostic-write-envelope --format json --preview-lines 120` | Thread files and `bridge/INDEX.md` agree; no drift. |

## Risk / Rollback

The main risk is accidentally widening the gate so far that arbitrary `.gtkb-state/**` or `.groundtruth/**` writes become a back door around protected-source authorization. Mitigation: keep the change command-aware, keep the test surface additive, and assert in tests that mixed protected-path writes still block without a packet.

Rollback is a single revert of the gate change and the new regression file if the focused regression suite or source inspection shows the envelope is too broad.

## Bridge Filing (INDEX-Canonical)

This REVISED proposal is filed under `bridge/` and inserted into the existing `gtkb-wi-4251-diagnostic-write-envelope` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix` — this is a behavioral repair to an existing enforcement surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
