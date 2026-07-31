REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5441-global-registry-membership-reconciliation - 019

bridge_kind: implementation_report
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 019
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-018.md
Controlling GO: bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md
Prior implementation report: bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md
Approved proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
Recommended commit type: fix:

## Draft Publication Guard

The owner-evidence re-capture required by v018 F1 is complete and cited below.
This revision contains no draft sentinel and is ready for governed publication.

## Revision Claim

This evidence-only revision closes the sole v018 blocker. The owner selected
posture A after the exact question and both options were presented in this
session. The literal answer, `A`, is now preserved through the governed
AUQ-backed deliberation service as `DELIB-202667515`, together with the AUQ id,
source reference, participants, presentation flags, content hash, and formal
approval packet.

No implementation, registry transaction, test, linter, digest, census, or
pre-existing evidence was re-run or changed. This report carries v018 E1-E12
forward as the independent verification of the implementation substance. No
artifact was deleted, moved, renamed, retired, narrowed, or replaced. No
WI-5640 Stage B apply, obsolete-source cleanup, dispatcher activation, commit,
push, release, deployment, credential action, or history rewrite occurred.

## Response To v018 NO-GO

### F1 (P1, blocking) - owner evidence and corrected rationale

The owner-evidence gap is closed by `DELIB-202667515`, version 1. The governed
record preserves all of the evidence v018 required:

- question presented: "How should unreadable, unregistered, and unobserved
  paths affect registry completeness?";
- option A, marked recommended: such paths remain
  `unregistered_disposable` and do not block completeness, while registered or
  observer-selected unreadable paths still block;
- option B: unreadability itself blocks completeness and transient trees must
  instead be excluded by traversal policy;
- literal owner response: `A`;
- AUQ evidence id:
  `AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728`;
- source reference:
  `codex-task:019f863a-acd3-7320-80c0-1831f0936cc0:wi5441-unreadable-path-posture`;
- formal packet fields `presented_to_user: true` and
  `transcript_captured: true`, with explicit change request
  `AUQ AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728: A`;
- record and packet content hash
  `sha256:f5bc036a55f82cf587b27217a2b854d9bf8b260db5bb9571dd93854a89c1432c`.

The corrected rationale now engages
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` point 6 directly
instead of presenting it as generic support for posture A. The owner knowingly
relaxes the full deterministic inventory precondition only for paths that are
simultaneously structurally uninspectable, unregistered, and unobserved. Those
paths can therefore classify as disposable and may later become eligible for
the separately governed quarantine and expiry process in points 8 and 9.

That consequence is explicit rather than inferred away. The decision does not
itself authorize quarantine, deletion, registry mutation, census rerun,
traversal-policy expansion, move, rename, retirement, or coverage reduction.
Every later sweep remains subject to its own mechanical authorization and
operation-time revalidation. Registered unreadable paths remain
`invalid_unknown`; observer-selected unreadable paths remain
`unregistered_load_bearing`; both continue to block completeness.

The earlier
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` remains immutable audit
history but is no longer cited as F1 authority. `DELIB-202667515` is the
controlling owner-evidence record for this posture.

### F2 and F3-F7 - accepted without re-execution

v018 independently confirms that F2 is correctly fixed and that F3-F7 are
closed. This revision makes no implementation or narrative claim that changes
those findings. The exact source, test, registry, census, preflight, and digest
results remain the v018 E1-E12 evidence.

## Non-Blocking Finding Disposition

The v018 findings below are accepted as separate hardening work and are not
implemented in this evidence-only correction:

- F8, F9, and F11 remain one future consistency/portability candidate covering
  Git-managed enumeration, failure semantics, and cache-directory exclusions.
- F10 remains a future operator-visibility candidate for unreadable
  `unregistered_load_bearing` entries.
- F12 remains a future decode-hardening candidate.
- F13 is accepted as a verification-practice correction. v018 independently
  re-ran and confirmed both censuses after the F2/F3 path changes; future
  path-affecting revisions must not carry census evidence across such changes.

These dispositions preserve the durable v018 findings without widening this
revision beyond its expressly authorized disclosure and re-capture scope. No
duplicate backlog rows are created by this report.

## Verified Evidence Carried Forward Without Re-Execution

Per v018, the following are independently verified and must not be redone for
this correction:

- the corrected shared Git-managed inventory and non-admitting failure path;
- the unreadable-candidate guard and unchanged completeness formula;
- 14 reconciliation tests plus both Ruff gates;
- exact reconciliation source and test digests;
- the additive two-record registry transaction and unchanged declarations;
- the 2,348-record registry identity and projection;
- hot-path and deep censuses after the F2/F3 changes;
- both mandatory preflights against v017;
- source retention, no destruction, and the database finalization waiver.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `SPEC-INTAKE-97538b`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

The owner selected option A in this task. That exact answer is now preserved as
`DELIB-202667515` with AUQ id
`AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728`, source reference
`codex-task:019f863a-acd3-7320-80c0-1831f0936cc0:wi5441-unreadable-path-posture`,
and the formal packet's presentation and transcript flags.

The selected posture is bounded: an unreadable path that is both unregistered
and unobserved remains `unregistered_disposable` and does not block
`membership_complete`; registered unreadable paths and observer-selected
unreadable paths continue to block. The owner explicitly accepted the possible
downstream quarantine/expiry consequence while leaving every destructive
operation separately governed.

Existing owner decisions remain in force: the registry is the ultimate
load-bearing membership authority; ordinary owner content edits require no
notation; an audit gap is preferable to platform failure; identity-changing
operations remain separately governed; and obsolete WI-5640 sources remain in
place. No broader owner authorization is inferred.

## Prior Deliberations

- `DELIB-202667515` - controlling AUQ-backed owner evidence for posture A.
- `DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` - historical first
  capture; retained as audit history, not cited as F1 authority.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - point 6 is
  knowingly relaxed only for structurally uninspectable, unregistered, and
  unobserved paths; points 8 and 9 define the disclosed downstream consequence.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE`
- `DELIB-202667356`
- `DELIB-20265258`
- `DELIB-202666060`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-018.md`

## Specification-Derived Verification

| Spec / governing surface | Evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `DELIB-202667515` carries the exact owner posture and explicit point-6 relaxation; v018 E9/E10 independently verified both censuses | PASS |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Governed AUQ-backed record and approval packet contain the literal response, source reference, content hash, and presentation/transcript flags | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `SPEC-INTAKE-97538b` | v018 independently verified policy derivation, shared enumeration, and unreadable candidate handling | PASS carried by reference |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | No registry change in v019; v018 re-confirmed additivity and transaction integrity | PASS carried by reference |
| `GOV-WORK-TREE-HYGIENE-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No code change; v018 independently executed 14 tests, Ruff, digests, and both censuses | PASS carried by reference |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Final-content applicability and clause preflights recorded below | PASS |
| Remaining linked specifications | No governed surface changed; v018 E1-E12 independently verified the unchanged implementation | PASS carried by reference |

## Evidence-Only Commands Run After v018

- Fresh Prime work-intent claim and resumable implementation-start packet;
  packet hash
  `sha256:e2e82dc31c5580a4ed8c0cde09e9672144b915e98b126e53fc3aeb713e7d0066`.
- Governed `gt deliberations record` for source reference
  `codex-task:019f863a-acd3-7320-80c0-1831f0936cc0:wi5441-unreadable-path-posture`,
  AUQ id `AUQ-WI5441-UNREADABLE-PATH-POSTURE-20260728`, and owner answer `A`:
  created `DELIB-202667515`, version 1.
- `gt deliberations show DELIB-202667515 --json`: record id/version,
  `source_type=owner_conversation`, exact source reference, literal response,
  participants, and content hash confirmed.
- Formal approval-packet readback: `presented_to_user=true`,
  `transcript_captured=true`, explicit AUQ request and answer, and matching
  `full_content_sha256` confirmed.
- No implementation suite, linter, digest, reconciliation census, registry
  transaction, or formatting command was run.

## Files Changed

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py`
- `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## By-Reference Finalization Waiver

target_paths: ["groundtruth.db"]

The service-owned database carries the already-verified additive registry
transaction, passive observation revisions, and AUQ-backed deliberation. It
MUST NOT be force-added, staged, placed in `## Files Changed`, or included in
the finalizer commit. This is a finalization-mechanics waiver, not an evidence
waiver. The formal approval packet is service-owned audit evidence and likewise
is not part of the implementation include set.

## Acceptance Criteria Status

- [x] The owner was presented the exact question and both postures.
- [x] The literal owner answer `A` is preserved with AUQ and source-reference evidence.
- [x] The formal packet records presentation, transcript capture, and matching content hash.
- [x] The rationale explicitly states the bounded relaxation of point 6 and the possible points 8/9 consequence.
- [x] The deficient first capture remains audit history but is not used as authority.
- [x] v018 F2 and F3-F7 findings remain closed without re-execution.
- [x] v018 F8-F13 are explicitly dispositioned as separate work.
- [x] The verified registry transaction, implementation, and census evidence are unchanged.
- [x] No registered artifact is deleted, moved, renamed, retired, narrowed, or replaced.
- [x] No WI-5640 Stage B mutation occurs.

## Pre-Filing Preflight

Applicability preflight against the completed content reports
`preflight_passed: true`, no missing required or advisory specifications, no
unclassified target paths, and no blocking errors. Mandatory clause preflight
evaluates five clauses with three `must_apply`, two `may_apply`, zero evidence
gaps, and zero blocking gaps. Both commands exit 0. No owner waiver is needed
or claimed.

## Risk And Rollback

This revision changes evidence only. The principal risk was over-reading the
owner's answer as a destructive authorization; the deliberation and this report
therefore state the exact classification boundary and preserve separate
mechanical authorization for every quarantine, expiry, deletion, registry, and
Stage B operation.

The append-only deliberation and prior deficient capture remain audit history.
The implementation paths remain ordinarily Git-restorable; the additive
registry transaction is untouched and is not rolled back here. WI-5640 Stage B
remains paused until this thread reaches terminal VERIFIED.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
