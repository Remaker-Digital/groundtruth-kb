NEW

# Defect-Fix Proposal - Keep Date-less NO-GO audit defects visible without blocking the modernization release gate

bridge_kind: prime_proposal
Document: gtkb-wi5085-date-less-no-go-warning
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5085

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_standing_backlog.py"]

## Claim

The frozen modernization release gate currently treats an otherwise-valid latest `NO-GO` verdict with no parseable `Date` line as release-failing missing evidence. Preserve the audit defect as a specific warning and repair obligation, while reserving `FAIL` for absent or unreadable authority needed to evaluate the backlog.

This proposal is filed as the next append-only numbered bridge file, `bridge/gtkb-wi5085-date-less-no-go-warning-001.md`. No existing bridge verdict is edited, replaced, or used as an inferred timestamp source.

## Defect / Reproduction

At HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f` in the authoritative concurrent worktree, the exact frozen command

`python scripts/release_candidate_gate.py --modernization-scope --include-frontend`

stops in standing-backlog health because five latest `NO-GO` verdicts have no parseable `Date` line. The gate does not proceed to its deeper Python, security, frontend, and modernization checks.

`check_standing_backlog_health` currently classifies every Date-less latest `NO-GO` as `kind=missing-evidence`, `severity=FAIL`. That conflates incomplete audit metadata with absence of the bridge directory, unreadable bridge state, or missing `groundtruth.db`, all of which genuinely prevent evaluation.

The owner decision `DELIB-20260715-MODERNIZATION-AUDIT-TRAIL-NONBLOCKING` requires audit-trail flaws to remain visible and be repaired without blocking otherwise-authorized modernization work. It preserves fail-closed behavior when substantive authority or implementation evidence cannot be verified.

## In-Root Placement Evidence

Both target paths are tracked, byte-clean, and inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` at Git blob `9a516b6f2d9f2628d40754d1d5caf8ce8b6f68ef`
- `groundtruth-kb/tests/test_doctor_standing_backlog.py` at Git blob `3bec9825b0b331be554b81ed9cc3966867640d0b`

The Date-less bridge files, verdict writers, release-gate source, dispatcher/TAFE state, harness registry, and all concurrent writer/finalizer changes are verification inputs only and are excluded from mutation.

## Specification Links

- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - Standing-backlog severity must distinguish mechanically evaluable metadata defects from missing governing evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected implementation requires this proposal, an independent GO, matching claim, and implementation-start authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The recurring defect is owned by WI-5085 and the owner policy is captured in a durable deliberation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The exact implementation scope and tests are linked to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED must rerun the mapped doctor and release-gate tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work item, and target paths are explicit above.
- `SPEC-AUQ-POLICY-ENGINE-001` - The owner decision is explicit and durable; no additional policy preference is inferred.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation and verification remain under the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - WI-5085 is the existing durable owner and is now an active member of the Modernization Assurance project.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex filing uses the governed non-bypass helper and compliance audit path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The owner decision, work-item membership, checker repair, tests, report, and independent verdict form the durable packet.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The Date defect remains an explicit warning-state lifecycle signal rather than disappearing.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Real missing authority evidence remains release-failing; bridge content and frozen acceptance scope remain unchanged.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Warning and failure classifications remain deterministic and machine-evaluable.

## Requirement Sufficiency

Existing requirements sufficient.

The standing-backlog health contract already distinguishes `WARN` for stale or incomplete operational state from `FAIL` for missing evidence that prevents evaluation. `DELIB-20260715-MODERNIZATION-AUDIT-TRAIL-NONBLOCKING` resolves the only policy ambiguity: incomplete non-authoritative audit metadata must remain visible and repairable without blocking the modernization program. No specification amendment is required for this bounded severity correction.

## Prior Deliberations

- `DELIB-202666274` - Authorize all required GT-KB modernization blocker repairs while preserving bridge and mechanical gates.
- `DELIB-20260715-MODERNIZATION-AUDIT-TRAIL-NONBLOCKING` - Flawed audit trails require durable repair but do not block otherwise-authorized modernization work unless substantive authority becomes unverifiable.

## Owner Decisions / Input

- The owner authorized the full Modernization Assurance project and explicitly directed that audit-trail defects be fixed without halting implementation.
- This proposal grants no authority to edit historical bridge verdicts, mutate writer paths currently owned by concurrent work, or infer timestamps from mutable file metadata.

## Proposed Scope

1. Reclassify a latest `NO-GO` with no parseable `Date` line from `missing-evidence/FAIL` to a dedicated `missing-verdict-date/WARN` finding.
2. State explicitly that the verdict is excluded from stale-age calculation until governed metadata is supplied; do not substitute filesystem mtime, access time, current time, or Git commit time as verdict authority.
3. Add `missing_verdict_date_count` to the stable summary while preserving `missing_evidence_count` for genuinely unavailable evaluation inputs.
4. Preserve `FAIL` for missing `groundtruth.db`, missing bridge directory, database evaluation failure, and bridge-state evaluation failure.
5. Preserve `WARN` and age calculation for parseable stale `NO-GO` verdicts.
6. Add focused tests for Date-less warning behavior, summary counts, no fabricated `age_days`, existing stale-date behavior, and genuine missing-evidence failure behavior.
7. Rerun focused doctor tests and the exact frozen release gate. The gate must proceed past standing-backlog health while reporting the current Date-less verdict count as warnings.
8. Leave prospective verdict-writer repair and governed correction of historical verdict chains to a non-overlapping follow-up under WI-5085 after concurrent writer/finalizer work is independently finalized.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-MODERNIZATION-AUDIT-TRAIL-NONBLOCKING",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/release_candidate_gate.py --modernization-scope --include-frontend",
  "before_behavior": "A Date-less latest NO-GO is classified as release-failing missing evidence even though its status and path remain mechanically visible.",
  "after_behavior": "A Date-less latest NO-GO produces a dedicated warning, remains visible for repair, and is excluded from stale-age calculation without fabricating a timestamp.",
  "self_descriptive_naming": "missing-verdict-date and missing_verdict_date_count distinguish incomplete verdict metadata from unavailable authority evidence.",
  "obsolete_guidance_disposition": "No finding is suppressed; the generic missing-evidence label is replaced only for the narrower Date metadata condition.",
  "history_preservation": "Historical bridge files remain byte-unchanged and no mutable timestamp is promoted to verdict authority.",
  "baseline": {
    "tracked_target_blobs": [
      "9a516b6f2d9f2628d40754d1d5caf8ce8b6f68ef",
      "3bec9825b0b331be554b81ed9cc3966867640d0b"
    ],
    "current_date_less_latest_no_go_count": 5,
    "release_gate_state": "FAIL before deeper checks"
  },
  "expected_result": {
    "date_less_latest_no_go": "WARN",
    "missing_database_or_bridge": "FAIL",
    "parseable_stale_no_go": "WARN with age_days",
    "fabricated_timestamp_sources": 0,
    "release_gate_standing_backlog_phase": "PASS with warnings"
  },
  "rollback": {
    "instructions": "Remove only the independently reviewed warning classification, summary counter, and focused WI-5085 tests from the two tracked targets.",
    "test": "python -m pytest groundtruth-kb/tests/test_doctor_standing_backlog.py -q --tb=short"
  },
  "hard_invariants": [
    "no bridge verdict mutation",
    "no filesystem or Git timestamp becomes verdict authority",
    "genuine missing evaluation evidence remains FAIL",
    "stale parseable NO-GO remains WARN",
    "frozen modernization acceptance scope remains unchanged",
    "concurrent verdict-writer changes remain untouched"
  ],
  "fail_closed_conditions": [
    "groundtruth.db absent or unreadable",
    "bridge directory absent",
    "latest bridge state cannot be evaluated",
    "unexpected exception while evaluating authority coverage"
  ],
  "essential_context_preservation": "Every Date-less path and document remains surfaced in findings, and writer repair remains open under WI-5085."
}
```

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Prove the dedicated Date defect classification and summary counter are emitted deterministically. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Prove missing DB/bridge evidence still fails and stale parseable NO-GO behavior is unchanged. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Assert stable finding kinds, severities, counts, paths, and absence of fabricated `age_days`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and ADR/DCL clause preflights against this complete proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns focused doctor tests and the exact frozen release gate before VERIFIED. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all test fixtures and outputs remain within pytest-owned in-root or system temporary directories under repository test policy. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify active GO, matching claim, and implementation-start authority before either target is edited. |

## Acceptance Criteria

1. A latest `NO-GO` without a parseable `Date` emits exactly one `missing-verdict-date` finding with `severity=WARN`, document, path, and repair-oriented message.
2. The Date-less finding carries no `age_days` and no filesystem, Git, or current-time fallback.
3. `missing_verdict_date_count` is exact and `missing_evidence_count` excludes Date-only defects.
4. Missing database, missing bridge directory, and evaluation exceptions remain `missing-evidence/FAIL`.
5. A parseable stale `NO-GO` remains `stale-NO-GO/WARN` with deterministic age and threshold fields.
6. The focused doctor suite passes and the exact frozen release gate proceeds past standing-backlog health while reporting the five current warnings.
7. No bridge verdict, verdict writer, release-gate file, dispatcher/TAFE state, harness state, Git state, frozen manifest, or external system is mutated.
8. Only the two tracked, initially clean target files contain this implementation slice.

## Risks / Rollback

- Downgrading all malformed verdict metadata would hide substantive problems. Scope is limited to a missing or unparsable optional `Date` line when latest status/path enumeration already succeeded.
- Mutable timestamp fallback would create false authority. The implementation explicitly refuses every fallback timestamp source.
- The prospective writer defect remains. WI-5085 stays open until canonical verdict writers and affected chains are governed without colliding with concurrent writer work.
- Rollback removes only this warning classification and tests, then reruns the focused suite and exact release gate.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_standing_backlog.py`

## Recommended Commit Type

`fix`
