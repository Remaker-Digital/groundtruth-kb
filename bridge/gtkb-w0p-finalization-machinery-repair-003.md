REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; transcript ::init gtkb pb; harness A; build activity
author_metadata_source: transcript init keyword and Codex runtime system metadata

bridge_kind: prime_proposal
Document: gtkb-w0p-finalization-machinery-repair
Version: 003
Responds to: bridge/gtkb-w0p-finalization-machinery-repair-002.md
Supersedes implementation scope of: bridge/gtkb-w0p-finalization-machinery-repair-001.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5977
implementation_scope: source,test
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/scripts/test_bridge_publication_preimage_scoping.py"]

# WI-5977 Slice D — narrow bridge-publication compensation to the publishing thread

## Revision Disposition

This same-thread revision narrows the approved seven-path program to the independently
implementable WI-5977 Slice D. A fresh implementation-start evaluation of the GO at
`-002` failed closed because another non-terminal implementation report owns
`.claude/skills/gtkb-verify/helpers/write_verdict.py`. The original proposal's other
five targets therefore make one unrelated peer conflict block the root-cause repair
that is currently preventing atomic VERIFIED finalization across the project.

No finding in the `-002` GO is disputed. Slices A, A2, B, and C remain deferred to
their existing carriers and path owners. This revision changes only the executable
cohort: one production source file and one new focused test module for Slice D.

## Summary

Bridge-publication compensation currently binds rollback to a whole-aggregate
preimage. Any unrelated bridge publication during the mint-to-compensate window
changes that aggregate and produces
`BRIDGE_PUBLICATION_REPAIR_REQUIRED: bridge publication aggregate preimage cannot
be restored exactly`. Under normal concurrent harness operation this strands
correct verdict files and poisons their publication capabilities.

Replace the compensation gate with a publishing-thread-scoped preimage. Unrelated
thread additions become benign, while any same-thread predecessor or target-slot
change remains a fail-closed conflict. Preserve the whole-aggregate digest as audit
evidence; it no longer decides whether this thread's target can be compensated.

## Current Evidence And Scope Boundary

- WI-5977 records 57 observed `aggregate preimage cannot be restored exactly`
  rows and the causal whole-aggregate digest over thousands of bridge files.
- `bridge/gtkb-envelope-context-keyed-path-retroclose-008.md` reproduced the
  same failure during a current atomic VERIFIED attempt after all substantive
  verification gates passed.
- WI-6077, WI-5690, WI-6095, and other green implementations are non-terminal
  because the same publication/finalization substrate remains unreliable.
- `registry_control_plane.py` currently contains a separate uncommitted WI-5950
  receipt-recovery hunk. This Slice-D implementation must add a disjoint hunk and
  produce hunk-patch evidence so WI-5950 bytes are never attributed to WI-5977.
- `scripts/gtkb_bridge_writer.py`, the protected-commit checker, finalizer helper,
  TTL values, capability ceilings, and existing recovery APIs are outside scope.
- This proposal performs no database, registry-row, dispatcher, TAFE, deployment,
  credential, Git-history, or external-system mutation.

## Proposed Change

1. In `registry_control_plane.py`, derive compensation preimage evidence from the
   publishing document/thread's numbered bridge files while excluding the exact
   target being compensated.
2. Continue recording the whole-aggregate preimage/digest as an audit observation,
   but do not reject compensation merely because an unrelated thread appended a
   file during the transaction window.
3. Fail closed when the publishing thread's own predecessor set changes, when the
   exact target slot/content no longer matches the expected operation, or when the
   scoped preimage cannot be derived safely.
4. Add `test_bridge_publication_preimage_scoping.py` with deterministic fixtures for
   unrelated-thread concurrency, same-thread concurrency, target-content mismatch,
   and stable audit evidence.
5. Generate a singleton WI-5977 hunk patch for `registry_control_plane.py` and record
   its SHA-256, byte size, and strict cached-apply verification in the implementation
   report. The new test file may be full-file staged.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`, the Mandatory
VERIFIED Commit-Finalization Gate, and WI-5977 define the required durable,
concurrency-safe, fail-closed behavior. This revision narrows an already-approved
implementation and introduces no new requirement.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication and terminal finalization
  must remain durable and auditable under ordinary concurrent use.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the project-layer source change stays
  inside the GT-KB platform root and introduces no adopter coupling.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete linkage for
  this source/test revision.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — every retained requirement
  maps to executed evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, WI, and
  exact target paths remain machine-readable.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — whole-aggregate evidence remains an audit
  observation while the target thread is the operative compensation authority.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the repair removes a concurrency
  deadlock without weakening same-thread or target conflict detection.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — no status or routing semantics change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the defect, decision history,
  implementation hunk, focused tests, report, and verification remain one
  traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the deferred peer-conflicted slices
  and this active narrowed slice are stated explicitly rather than conflated.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the reproduced systemic risk and
  narrowed repair remain durable bridge/work-item evidence.

## Prior Deliberations

- `DELIB-20260806011899` — owner elevated finalization-machinery repair into Wave 1.
- `DELIB-20260806011898` — owner capture of the first custodial finalization incident.
- `DELIB-202668159` — durable cross-process bridge recovery reservation precedent.
- `bridge/gtkb-wi5977-aggregate-preimage-compensation-gates-001.md` — durable root-
  cause advisory: compensation must answer whether this target/thread can be
  restored, not whether every unrelated bridge file is unchanged.
- `bridge/gtkb-w0p-finalization-machinery-repair-001.md` and `-002.md` — approved
  umbrella proposal and independent GO; this revision preserves Slice D and defers
  the peer-conflicted slices.
- `bridge/gtkb-envelope-context-keyed-path-retroclose-008.md` — current reproduction
  of the same aggregate-preimage failure after substantive verification passed.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20260806011899` already prioritizes this
machinery repair, and the owner has directed completion of the blocked bridge-
reliability/session-envelope outcomes. This revision narrows scope and risk; it
does not widen mutation authority.

## Specification-Derived Verification Plan

| Requirement | Executed verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; WI-5977 unrelated concurrency | New focused test inserts an unrelated thread file between mint and compensation | Compensation succeeds; target state and capability evidence are correct |
| Same authority; fail-closed thread integrity | New focused test mutates/adds a same-thread predecessor during the same window | Compensation refuses with a named same-thread conflict |
| Target-slot integrity | New focused test changes the target bytes/slot before compensation | Compensation refuses and preserves forensic evidence |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Focused test inspects scoped and whole-aggregate audit digests | Scoped decision is stable; aggregate observation remains recorded/auditable |
| Existing recovery/writer nonimpairment | `groundtruth-kb/tests/test_registry_control_plane.py` compensation/recovery selection plus `platform_tests/scripts/test_gtkb_bridge_writer.py` | Existing recovery and governed writer tests remain green without modifying those files |
| Python quality | Ruff check and Ruff format check on both target modules | Both independent gates pass |
| Shared dirty-path isolation | Strict cached apply of the declared WI-5977 singleton patch against the approved preimage | Patch contains only Slice-D hunk; WI-5950 hunk excluded |

## Acceptance Criteria

1. An unrelated bridge-thread append during mint-to-compensate no longer causes
   `BRIDGE_PUBLICATION_REPAIR_REQUIRED`.
2. Same-thread predecessor or exact-target conflicts still fail closed.
3. Whole-aggregate evidence remains available for audit but is not an unrelated-
   writer veto over this thread's compensation.
4. Only the two declared target paths change for this slice.
5. The implementation report contains hunk-patch evidence that excludes the
   pre-existing WI-5950 source hunk.
6. Focused and adjacent recovery/writer tests, Ruff lint, Ruff format, and diff
   checks pass.

## Cross-Harness Disposition

The registry control plane is the single shared implementation used by all
harnesses. No harness adapter, role map, projection, or hook copy changes. The
concurrency fixture models two unrelated bridge threads rather than any vendor-
specific behavior.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5977; DELIB-20260806011899; W0-prime GO -002",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "thread-scoped bridge-publication compensation preimage",
  "before_behavior": "any unrelated bridge append invalidates a whole-aggregate compensation preimage",
  "after_behavior": "unrelated appends are benign; same-thread and target conflicts fail closed",
  "self_descriptive_naming": "thread-scoped preimage helpers and tests name the document/thread boundary they enforce",
  "obsolete_guidance_disposition": "the original seven-path umbrella remains historical authority; this revision supersedes only its executable target cohort and defers the other slices",
  "history_preservation": "append-only bridge history and aggregate audit observations remain intact",
  "baseline": {
    "decision_scope": "whole bridge aggregate excluding only the target",
    "observed_failure": "BRIDGE_PUBLICATION_REPAIR_REQUIRED on unrelated concurrent bridge appends",
    "source_conflict": "WI-5950 hunk already present in registry_control_plane.py"
  },
  "expected_result": {
    "decision_scope": "publishing document thread excluding the exact target",
    "unrelated_append": "compensation succeeds",
    "same_thread_or_target_change": "compensation fails closed"
  },
  "hard_invariants": ["same-thread conflict refusal", "target-content refusal", "no TTL or status change"],
  "fail_closed_conditions": ["document/thread identity cannot be parsed", "same-thread preimage changed", "target slot or content changed"],
  "essential_context_preservation": "whole-aggregate digest remains recorded as audit evidence while the target thread is the operative compensation boundary",
  "rollback": "revert the isolated Slice-D hunk and focused test; no data migration"
}
```

## Risks And Rollback

The principal risk is under-scoping a conflict that should block compensation.
The same-thread and target-mismatch tests are therefore blocking acceptance gates,
and any ambiguous document-name parse fails closed. Rollback is a scoped revert of
the WI-5977 hunk and new test. No historical bridge file or capability row is
rewritten by implementation.

## Recommended Commit Type

`fix:` — repairs a concurrency defect in existing publication compensation
without adding a new user-facing capability.

---

When you are finished working, close your session envelope by invoking ::wrap.
