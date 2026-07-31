NEW
::init gtkb lo
::open build

# gtkb-wi5652-impl-start-gate-multipath-drift-fix — Fix false target_classifications drift on multi-path PAUTH packets

bridge_kind: prime_proposal
Document: gtkb-wi5652-impl-start-gate-multipath-drift-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-07-22 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b934dabd-089b-45eb-aa95-f7ef2f9c4db6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5652-GATE-MULTIPATH-DRIFT-FIX-20260722
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5652

target_paths: ["scripts/implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The implementation-start authorization gate falsely rejects every protected write of a **multi-path**
PAUTH packet. In `validate_packet_project_authorization_operation`
(`scripts/implementation_authorization.py`, ~L2371-2394), the drift check computes `current` from the
**write-time** target paths — which, for a `Write` tool call, is always a **single file** — and then
compares `current["target_classifications"]` and `current["normalized_envelope_hash"]` against the
packet's stored snapshot, which was computed over **all declared** target paths. Because a `Write`
touches one file at a time, a packet declaring N>1 targets can never satisfy the strict list-equality
check: `current` has 1 classification entry, the packet has N, so the gate raises
`Project authorization target_classifications drifted since packet creation`.

**Reproduced 2026-07-22** (this session): `validate_packet_project_authorization_operation` on the
live WI-5440 packet passes when given all 3 declared target paths but drifts when given the single
`maintenance.py` path; `validate_targets(root, [single-file], session)` returns exactly that single
path. This blocked WI-5440 (governed git-maintenance actuator, valid GO at
`bridge/gtkb-wi5440-git-maintenance-actuator-002.md`) and, by the same mechanism, any multi-file
implementation performed under a project authorization.

**Fix (single file).** In `validate_packet_project_authorization_operation`, keep the existing
write-time evaluation via `validate_project_authorization_row(..., target_paths=<write-time targets>)`
so per-write authorization is still enforced (it raises if the specific file's mutation class is not
PAUTH-allowed), but recompute the drift-check `current` over the packet's **declared** target paths
(extracted from `project_authorization["target_classifications"]`). This makes both
`target_classifications` and `normalized_envelope_hash` compare like-for-like: a genuine authorization
change still fails closed, while a single-file write of a multi-path packet no longer false-positives.

This proposal is deliberately **single-path** (only `scripts/implementation_authorization.py`) because
the very defect being fixed blocks a two-path (source + test) packet from completing. The committed
regression test lands in an immediate follow-up once this fix unblocks multi-path packets; verification
here is by reproduction plus the existing suite (see Spec-Derived Verification Plan).

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the governing spec: project
  authorization bounds are enforced at every operation. This fix ensures that enforcement is *correct*
  (rejects genuine drift, accepts a single-file write of an authorized multi-path packet) rather than
  false-positive.
- `DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001` — governs path handling in the
  implementation-start gate surface this fix touches.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the fix is an additive, non-impairing repair; all
  existing gate behavior (per-write authorization, genuine-drift fail-closed, single-path packets) is
  preserved.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the verification plan below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governs this section's completeness.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — governs the linkage triple above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs append-only bridge filing and dispatcher/TAFE publication.
- `GOV-STANDING-BACKLOG-001` — WI-5652 is the MemBase backlog authority for this work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect and its fix are captured as durable governed
  artifacts (WI-5652, the owner-decision deliberation, this proposal) rather than an untracked patch.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the fix is tracked through the bridge lifecycle with
  recorded verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle states are explicit: this proposal is `NEW`,
  WI-5652 is `open`, and the dependent WI-5440 keystone remains blocked until this lands.

## Prior Deliberations

- `DELIB-20260722-WI5652-IMPL-START-GATE-MULTIPATH-DRIFT-FIX` — owner decision (2026-07-22): fix this
  defect via a single-path proposal on `scripts/implementation_authorization.py`; establishes that
  WI-5652 is independent of the contended WI-5178 thread. This proposal implements that decision.
- `DELIB-202666764` — the git-bloat + housekeeping-hardening program authorization. WI-5652 is the
  gate defect discovered while implementing that program's keystone (WI-5440); fixing it unblocks the
  program.
- `bridge/gtkb-wi5178-governed-predecessor-closure-008.md` — the NO-GO whose contention analysis
  established that WI-5178's blocked paths (bridge-compliance-gate.py, dispatcher_runtime.py,
  proposal_filing.py) are DISJOINT from this fix's target; this fix does not collide with that thread.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

1. `DELIB-20260722-WI5652-IMPL-START-GATE-MULTIPATH-DRIFT-FIX` (owner AUQ, 2026-07-22): authorized the
   single-path fix approach on `scripts/implementation_authorization.py` with the regression test in a
   now-unblocked follow-up.
2. Owner directive, 2026-07-22: "Continue until this program is landed. Do not stop for me: I authorize
   your necessary actions." — standing authorization to proceed through the bridge protocol
   autonomously (does not waive independent Loyal Opposition review).

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
already specifies that authorization bounds are enforced at every operation; this fix corrects a
false-positive in that enforcement so it matches the specification's intent. No new or revised
requirement is needed before implementation.

## Spec-Derived Verification Plan

Run with the repo venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q --no-header
```

| Specification | Verification | Expected result |
|---|---|---|
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Reproduction A: `validate_packet_project_authorization_operation` on a multi-path packet, given a single declared-set member as the write-time target | No `AuthorizationError`; drift check passes (the current-behavior bug is fixed). |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Reproduction B: same call, but with the stored `project_authorization` snapshot mutated (e.g., a changed classification or bumped version) | `AuthorizationError` still raised — genuine drift still fails closed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing `test_implementation_authorization.py` suite | All pre-existing tests pass — per-write authorization and single-path behavior unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The committed regression test (Reproductions A + B as a pytest case) lands in the immediate multi-path follow-up thread this fix unblocks | Follow-up records the durable regression test; this thread's verification is the executed reproductions plus the existing suite. |

Code-quality gates on the changed file before the post-implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/implementation_authorization.py
```

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/implementation_authorization.py
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5652 under PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS, authorized by PAUTH-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI5652-GATE-MULTIPATH-DRIFT-FIX-20260722 and owner decision DELIB-20260722-WI5652-IMPL-START-GATE-MULTIPATH-DRIFT-FIX (2026-07-22).",
  "canonical_authority": "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, with DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001 for the gate surface.",
  "primary_route": "The implementation-start gate: python scripts/implementation_authorization.py begin plus the PreToolUse implementation_start_gate hook that calls validate_packet_project_authorization_operation.",
  "before_behavior": "The drift check computes current from the write-time single target and compares its target_classifications (1 entry) and normalized_envelope_hash against the packet snapshot computed over all declared targets (N entries), with strict equality. Any multi-path PAUTH packet is therefore falsely rejected as drifted on every single-file write, blocking all multi-file implementation under project authorization.",
  "after_behavior": "The drift check recomputes current over the packet declared target paths, so target_classifications and normalized_envelope_hash compare like-for-like. A single-file write of an authorized multi-path packet passes; a genuine authorization change still fails closed. Per-write authorization (via the retained write-time evaluation) and single-path packet behavior are unchanged.",
  "self_descriptive_naming": "No new public names or CLI surface; an internal logic correction within the existing validate_packet_project_authorization_operation function.",
  "obsolete_guidance_disposition": "No guidance becomes obsolete. The gate's intent (enforce authorization bounds at operation time per DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001) is preserved and made correct; existing do-not-bypass rules remain in force.",
  "history_preservation": "Pure logic fix. No history rewrite, no force-push, no Git LFS, no data migration, no removal of any authorization record.",
  "baseline": "2026-07-22: WI-5440 3-path packet blocked with 'Project authorization target_classifications drifted since packet creation'. Reproduction: validate_packet_project_authorization_operation passes with all 3 declared paths, drifts with the single write-time path; validate_targets returns only the single path.",
  "expected_result": "Existing platform_tests/scripts/test_implementation_authorization.py suite passes; Reproduction A (multi-path packet, single-file write) passes; Reproduction B (genuine authorization change) still fails closed; ruff check and ruff format --check clean on the changed file.",
  "rollback": "Single-commit revert. Pure in-function logic change with no persisted state, so reverting restores the prior behavior exactly.",
  "hard_invariants": [
    "per-write authorization is still enforced (a write whose file mutation class is not PAUTH-allowed still raises)",
    "genuine authorization drift (changed version, classifications, evaluator, or taxonomy hashes) still fails closed",
    "single-path PAUTH packet behavior is unchanged",
    "no history rewrite, no force-push, no Git LFS"
  ],
  "fail_closed_conditions": [
    "project authorization not active or expired",
    "work item excluded by the authorization",
    "spec link excluded by the authorization",
    "target_classifications or normalized_envelope_hash differ from the packet snapshot when both are computed over the packet declared target paths",
    "packet uses a legacy schema version"
  ],
  "essential_context_preservation": "The packet declared target_classifications remain the authorization baseline; the fix restores an apples-to-apples comparison against that baseline rather than weakening or removing the drift check."
}
```

## Risk / Rollback

**Risk surface.** One function in one file. The only behavioral change is the target set used to
recompute the drift-check `current`. The retained write-time evaluation preserves per-write
authorization; the recompute over declared targets preserves genuine-drift detection. Single-path
packets are unaffected (declared set == write-time set). No CLI, schema, or state change.

**Rollback.** Single-commit revert; pure logic, no migration, no state to unwind.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for
`gtkb-wi5652-impl-start-gate-multipath-drift-fix`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — this repairs broken behavior (a false-positive authorization drift that blocks valid
multi-path implementation) with no new capability surface. Not `feat` (no new capability), not
`chore` (it changes load-bearing gate logic).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
