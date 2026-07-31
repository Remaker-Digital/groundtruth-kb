REVISED

# Prime Builder Revision — WI-5173 Shim-harness dispatch telemetry usage coverage conformance

bridge_kind: prime_proposal
Document: gtkb-wi5173-shim-dispatch-telemetry
Version: 005
Responds to: bridge/gtkb-wi5173-shim-dispatch-telemetry-004.md
Approved proposal: bridge/gtkb-wi5173-shim-dispatch-telemetry-001.md
Date: 2026-07-11 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; role=prime-builder resolved via worker session document
author_metadata_source: Codex system runtime context plus explicit session document

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5173

target_paths: ["groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Revision Claim

Conform the existing `gtkb.shim_dispatch_telemetry.v1` implementation to
`SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` usage semantics. The fully absent
provider-usage state will emit `usage.coverage: "unavailable"`; partially
observed usage remains `"partial"`, complete coverage remains `"complete"`,
and unknown numeric values remain `null`. This responds only to the P2 blocking
finding in the independent post-implementation NO-GO; it does not alter the
envelope shape, dispatch behavior, telemetry storage, role authority, privacy
allowlist, budget, selection, or query surface.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`
already names `unavailable` as the fully absent usage-coverage vocabulary and
requires unknown measurements to be `null`, so this revision conforms to the
approved specification without a new owner decision or specification change.

## In-Root Placement Evidence

All three target paths are inside `E:\GT-KB` and are a strict subset of the
active WI-5173 PAUTH and original approved proposal target set.

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` — controls the v1 envelope,
  usage/null semantics, reconciliation, privacy, and acceptance tests.
- `SPEC-TAFE-R6`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and
  `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — retain the existing dispatcher and
  telemetry context without changing dispatch behavior.
- `GOV-SESSION-ROLE-AUTHORITY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` — preserve document-only worker-role
  authority; this revision does not touch role resolution.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — preserve PAUTH,
  bridge, claim, and implementation-start gates.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires executed,
  specification-derived regression evidence for the corrected field value.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve formal lineage through the
  approved specification, PAUTH, bridge, tests, and independent verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `GOV-STANDING-BACKLOG-001` —
  retain GT-KB placement and the existing WI lineage.

## Prior Deliberations

- `bridge/gtkb-wi5173-shim-dispatch-telemetry-001.md` — original approved
  proposal and its owner-authorized scope.
- `bridge/gtkb-wi5173-shim-dispatch-telemetry-002.md` — independent LO GO.
- `bridge/gtkb-wi5173-shim-dispatch-telemetry-003.md` — implementation report.
- `bridge/gtkb-wi5173-shim-dispatch-telemetry-004.md` — independent LO NO-GO
  identifying the precise `unknown` versus `unavailable` field mismatch.
- `DELIB-202666074` — owner approval for bounded telemetry implementation.
- `DELIB-202665303` — measure real harness behavior before changing budgets.
- `DELIB-20265026` — provider-failure evidence relevant to partial,
  nonfatal telemetry.

## Owner Decisions / Input

- `DELIB-202666074` and
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5173-SHIM-TELEMETRY-20260710`
  authorize this bounded implementation surface; an independent LO GO,
  matching claim, implementation authorization packet, and verification remain
  mandatory.
- No new owner decision is required: this revision selects the LO-recommended
  spec-conformance path rather than revising the owner-approved vocabulary.

## Findings Addressed

### [P2] `usage.coverage` emitted `unknown` instead of the specified `unavailable`

Response: replace the fully absent usage coverage value in both normal summary
and reconciliation-created partial envelopes with `unavailable`. Update the
two direct telemetry assertions and the dispatcher reconciliation assertion to
lock the approved value. The separate `unknown` labels used for missing query
group dimensions are outside the `usage.coverage` contract and remain
unchanged.

## Scope Changes

- Narrowed from the original eleven paths to the telemetry module and its two
  affected regression suites.
- No schema version, storage path, provider integration, dispatcher
  configuration, role-resolution logic, or command surface changes.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Fully absent usage | `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py` asserts `usage.coverage == "unavailable"` and every usage scalar is `null` for missing-role/no-provider-usage and reconciliation-created partial records. |
| Partial and complete semantics | The same module suite retains explicit partial and complete coverage assertions, including directly observed zero values. |
| Dispatcher reconciliation | `platform_tests/scripts/test_dispatcher_runtime.py` asserts a worker-exit partial envelope uses `unavailable` without changing its bounded outcome facts. |
| No behavioral expansion | Focused telemetry, cloud, Ollama, OpenRouter, and dispatcher suites exercise the existing envelope, privacy, role-authority, failure-isolation, and query contracts. |
| Code quality | Run `ruff check` and `ruff format --check` on the three changed Python files. |

## Acceptance Criteria

- Every fully absent provider-usage envelope emits `usage.coverage: "unavailable"`.
- Unknown numeric usage remains `null`; observed zero remains zero; partial and
  complete coverage semantics remain unchanged.
- Dispatcher reconciliation preserves outcome facts and only changes the
  specified coverage label.
- The original WI-5173 focused suite and both ruff gates pass.
- No production dispatch selection, turn budget, configuration, or automatic
  tuning behavior changes.

## Risk And Rollback

- Risk: changing an established but nonconformant string could surprise an
  untracked consumer. Mitigation: the value is explicitly specified and all
  in-repo producer and consumer coverage is updated together.
- Risk: an overly broad replacement could alter unrelated query fallback
  labels. Mitigation: limit the code change to `usage.coverage` producers and
  assert query fallback behavior remains untouched.
- Rollback: restore the prior implementation only if an external compatibility
  issue is substantiated; such a change would require a specification decision
  before terminal verification.

## Pre-Filing Preflight Subsection

- Applicability preflight: passed against this completed draft; packet hash
  `sha256:6145ecdb63e51b0202d2487015233e1907da469db9912483ea8f64ff6c7e0fc1`;
  `missing_required_specs: []`; `missing_advisory_specs: []`.
- Clause applicability preflight: passed in mandatory mode; 5 clauses evaluated,
  4 must-apply, 0 evidence gaps, and 0 blocking gaps.

## Recommended Commit Type

`fix`
