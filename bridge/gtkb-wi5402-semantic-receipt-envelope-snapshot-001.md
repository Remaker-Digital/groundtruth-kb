NEW

# gtkb-wi5402-semantic-receipt-envelope-snapshot (Slice 1) - Preserve semantic receipts across terminal envelope closure

bridge_kind: prime_proposal
Document: gtkb-wi5402-semantic-receipt-envelope-snapshot
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17T03:20:17Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5402

target_paths: ["scripts/check_modernization_scope_semantics.py", "scripts/collect_modernization_semantic_evidence.py", "platform_tests/scripts/test_modernization_scope_semantics.py", "platform_tests/scripts/test_collect_modernization_semantic_evidence.py"]

implementation_scope: source | test | semantic-evidence-protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The canonical semantic-evidence collector currently records the exact path and
hash of an open worker session envelope. Dispatcher terminal closure then
correctly rewrites that same per-session document to `status=closed`. The
semantic checker later re-resolves the mutable path and rejects the otherwise
genuine receipt. A disposable current-code reproduction produced
`COLLECTED -> PASS -> FAIL` after only the terminal rewrite, with
`Worker role provenance requires an open session envelope.` The current frozen
`AT-SCOPE-SEMANTICS` result is 30 failed / 60 passed and includes this
provenance lifecycle defect.

Make the canonical collector preserve each cited session envelope as an
append-only, content-addressed snapshot beneath the configured semantic
evidence root. Receipts retain the exact canonical live source path, bind its
pre-close hash, and add the exact immutable snapshot path. The checker validates
the snapshot bytes and canonical role provenance instead of requiring the live
document to retain its open-state bytes after worker exit. This follows the
existing release-candidate actor-receipt snapshot pattern and does not weaken or
modify terminal session closure.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires an independent `GO`, matching
  claim/start authority, and post-implementation independent verification
  before these protected source and test paths may be finalized.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this
  implementation proposal to identify the specifications that derive its
  behavior and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to
  the active modernization-assurance project authorization and WI-5402.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the independent
  reviewer to verify the closure-survival, tamper, omission, and provenance
  cases derived below.
- `GOV-STANDING-BACKLOG-001` - governs WI-5402 as an `origin=hygiene` defect
  found while executing the frozen modernization acceptance contract.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` - requires terminal closure and
  append-only per-harness archive behavior; this proposal preserves that
  lifecycle and makes downstream evidence tolerate it.
- `ADR-ENVELOPE-META-MODEL-001` - requires deterministic session-envelope
  payload and provenance rather than a synthetic or ambiguous authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires active GT-KB evidence
  dependencies to remain inside the project root; snapshot path validation
  rejects external or traversal-based substitutes.

## Prior Deliberations

- `INTAKE-79266a5f` - lifecycle-event projections must refresh
  deterministically and semantic schema changes remain governed. This proposal
  adds a versioned issuer contract and does not silently reinterpret existing
  receipts.
- `INTAKE-336182d2` - producer metadata and lifecycle audit evidence must be
  uniform. The same snapshot authority shape is used for the receipt issuer,
  live-harness observations, and independent-verification producer sessions.

## Owner Decisions / Input

No additional owner decision is required to file this proposal. The owner
authorized the full modernization program, clarified that work authorization is
per project, and directed that every discovered defect be added as an
`origin=hygiene` backlog item and then advanced. Protected implementation still
requires independent `GO` plus matching claim/start authority. This proposal
does not request or perform dispatcher, TAFE, harness, Git, deployment,
credential, or existing-evidence mutation.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ENVELOPE-DURABILITY-001`
requires the terminal mutation that exposed the defect and an append-only
archive trail. `ADR-ENVELOPE-META-MODEL-001` requires deterministic authority.
The frozen manifest requires genuine observed semantic evidence, and the
existing release-candidate actor receipt establishes the accepted immutable
snapshot trust pattern. No new governing requirement is needed.

## Proposed Implementation

1. In `scripts/collect_modernization_semantic_evidence.py`, add a single
   canonical helper that reads the exact live per-session document, computes its
   uppercase SHA-256, and writes its bytes exclusively to:
   `<evidence_dir>/session-envelope-snapshots/<harness_name>/<session_id>/<sha256>.json`.
   Existing identical content is reusable; any conflicting bytes at the exact
   content-addressed path fail closed.
2. Extend each collected session authority with
   `session_envelope.snapshot_path` while retaining
   `session_envelope.path` as the exact canonical live source path and
   `session_envelope.sha256` as the captured hash. Increment the semantic issuer
   schema version because prior authority objects lack the new trust carrier.
3. Route the collector issuer, persisted live-harness observations, and
   independent-verification producer authorities through that one helper.
   Replace standalone mutable live-envelope observations with the full
   snapshotted authority object.
4. In `scripts/check_modernization_scope_semantics.py`, validate the exact
   canonical source path, exact content-addressed snapshot path, snapshot hash
   and bytes, and `_validate_worker_role_provenance` result against the stored
   session identity. Do not require the live path to remain open or byte-equal
   after issuance.
5. Reject old, missing, malformed, path-substituted, hash-mismatched,
   provenance-mismatched, or tampered snapshots. Never synthesize an authority
   from receipt text and never rewrite an existing receipt or snapshot.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5402 current-code reproduction and frozen AT-SCOPE-SEMANTICS evidence",
  "canonical_authority": "DCL-SESSION-ENVELOPE-DURABILITY-001 plus the canonical semantic collector",
  "primary_route": "canonical collector creates append-only content-addressed snapshot; semantic checker validates it",
  "before_behavior": "a genuine receipt passes while its worker envelope is open and becomes invalid when correct dispatcher closure rewrites that same path",
  "after_behavior": "the receipt remains valid after terminal closure because it binds immutable captured bytes while retaining the exact canonical source path",
  "self_descriptive_naming": "session-envelope-snapshots, snapshot_path, and session authority identify the lifecycle and trust roles directly",
  "obsolete_guidance_disposition": "existing snapshot-less semantic receipts remain append-only history but do not qualify under the incremented issuer schema",
  "history_preservation": "no existing receipt, measurement, issuance, envelope, archive, or bridge artifact is rewritten or deleted",
  "baseline": "disposable reproduction: COLLECTED, PASS before close, FAIL after close with open-envelope provenance error",
  "expected_result": "newly issued receipts survive live-envelope closure and still fail on snapshot omission, substitution, mismatch, or tampering",
  "rollback": "revert only the independently finalized WI-5402 collector/checker/test hunks; append-only evidence already issued under the new schema remains historical",
  "hard_invariants": [
    "terminal session-envelope closure remains mandatory",
    "the canonical live source path remains recorded exactly",
    "snapshots are collector-created, append-only, content-addressed, and in-root",
    "Git HEAD, scope digest, receipt, measurement, issuance, and independence bindings remain exact",
    "no synthetic or hand-authored evidence qualifies"
  ],
  "fail_closed_conditions": [
    "snapshot missing or outside the configured semantic evidence root",
    "snapshot path does not match harness, session id, and captured SHA-256",
    "snapshot bytes or hash mismatch",
    "snapshot role provenance conflicts with the stored session authority",
    "collector encounters conflicting bytes at an existing content-addressed path"
  ],
  "essential_context_preservation": "issuer, live-harness, and producer authorities share one snapshot contract; terminal closed state remains available at the canonical live path and per-harness archive"
}
```

## Spec-Derived Verification Plan

1. `DCL-SESSION-ENVELOPE-DURABILITY-001`: extend the focused semantics test to
   issue a receipt from an open envelope, rewrite the live document to its
   terminal closed form, and require the same receipt to remain `PASS`.
2. `ADR-ENVELOPE-META-MODEL-001`: assert that the snapshot's validated worker
   provenance exactly matches session id, harness id/name, role, role source,
   issue time, and dispatch run id stored in the authority.
3. Trust-boundary negatives: require `FAIL` for missing snapshot, wrong
   content-addressed path, altered bytes, changed hash, changed role
   provenance, or a conflicting exclusive write.
4. Independence: close both producer and verifier live envelopes after an
   independently issued receipt and require validation to continue passing;
   then tamper a producer snapshot and require failure.
5. Collector consistency: require issuer, live-harness, and producer authority
   observations to use the same snapshot schema and exact evidence root.
6. `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: attempt an external and a
   traversal-based snapshot reference and require both to fail without reading
   them as authority.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_scope_semantics.py platform_tests/scripts/test_collect_modernization_semantic_evidence.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe scripts/check_modernization_scope_semantics.py run --phase clean-suite
```

Expected focused result: all tests pass, including closure survival and all
negative cases. Expected frozen-suite result: WI-5402 open-envelope and exact
live-path/hash failures are absent; unrelated receipt-acquisition, Git-pilot,
operation-time authority, or scope defects remain visible until their owning
work items close.

## Risk / Rollback

Primary risk is accidentally accepting a snapshot from an arbitrary path or
silently qualifying old evidence. Exact path derivation, issuer schema
increment, exclusive writes, private provenance validation, and tamper tests
contain that risk. Another risk is leaving a mutable live-envelope reference in
nested measurement traversal; focused tests cover every authority-bearing
measurement shape. Rollback is a scoped revert of only the four WI-5402 paths
after separate exact mechanical authority; no Git operation is authorized by
this proposal.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5402-semantic-receipt-envelope-snapshot`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - correct a semantic-evidence validity regression caused by the intended
session-envelope terminal lifecycle.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
