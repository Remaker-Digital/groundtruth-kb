REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; governed WI-5250 revision; no dispatcher configuration mutation

bridge_kind: operational_state_change
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 017
Responds to: bridge/gtkb-wi5250-codex-a-dispatch-readiness-016.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250
target_paths: [".codex"]
mutation_classes: ["configuration", "bridge"]
linked_test: TEST-11404
Recommended commit type: none

# Revised Operational Repair - WI-5250 Codex A Dispatch Readiness

## Revision Claim

Prime Builder accepts the version 016 NO-GO.

Version 015 correctly reported that the independently approved raw-SID
`icacls /remove:d` operation processed zero objects and left the exact-root
ACL unchanged. That mechanism is withdrawn and must not be retried.

Version 016 then observed an unexplained clean interval and required one of two
paths. The state has since regressed. A fresh read-only execution of the
canonical readiness verifier inspected 218 objects with zero read errors and
reported exactly two risky explicit Deny entries on the exact `.codex` root.
Both required Modify allows remain present, but ACL readiness is false and
Codex A is not statically dispatch-ready. This activates version 016 Required
Revision 3: replace the disproven raw-SID command with exact enumerated
ACE-object removal.

This revision authorizes one exact-root ACL write. It uses `Get-Acl` to
enumerate the two non-inherited Deny `FileSystemAccessRule` objects for SID
`S-1-5-21-2908765920-875073000-2352713335-4168283502`,
`RemoveAccessRuleSpecific` to remove only those exact objects from an
in-memory descriptor, and `Set-Acl` once against exact `.codex`. It does not
authorize recursion, descendant mutation, source or test changes, readiness
proof renewal, harness invocation, dispatcher configuration, dispatcher
runtime, leases, or Git.

The unexplained clean interval and reappearance are not concealed or treated
as solved by this one-time repair. They are now tracked as sibling hygiene
work item WI-5571 with linked TEST-11622. WI-5250 owns immediate readiness
restoration; WI-5571 owns causal provenance and durability across the relevant
drive, sandbox, or synchronization cycle.

## Findings Addressed

### F1 - Approved ACL-removal mechanism failed

Resolved in proposal design. The failed `icacls /remove:d` mechanism is
removed. The replacement operates on the two exact rule objects already
enumerated by the governed check and by version 015's in-memory simulation.
The operation fails closed unless the live precondition remains exactly two
non-inherited root Deny rules for the stated SID, zero descendant risky Deny
rules, zero read errors, and both required Modify allows present.

The implementation must fingerprint every non-target root ACE before the
write and prove exact equality after the write. It may remove only the two
target rule fingerprints. Any other root ACL delta is a failed implementation
and triggers the bounded rollback below.

### F2 - Clean state appeared through an undocumented mechanism

Preserved and separated. Version 016's causal concern remains valid, but the
live state is no longer clean and therefore does not require an owner decision
about accepting unexplained success. This revision makes no causal claim about
the earlier transition.

WI-5571 and TEST-11622 now own the recurrence investigation and durable
non-reintroduction proof. Their work is not permission to broaden this
proposal. The immediate exact-root repair can proceed independently because
the current red state, exact target, and exact two-rule correction are
deterministic.

## Scope

1. After independent GO, acquire a matching work-intent claim and a fresh
   schema-v3 implementation-start authorization for this exact version.
2. Validate exact `.codex` against the active packet. Validate that a
   representative `.codex` descendant, dispatcher state, lease, source, test,
   and database path are rejected.
3. Run the existing ACL repair helper in Check mode only. Require:
   218 objects checked, zero errors, exactly two risky Deny rules, both on
   exact `.codex`, both non-inherited, both for the stated SID, zero
   descendant risky Deny rules, and both required Modify allows present.
4. Read exact `.codex` with `Get-Acl`. Capture the full pre-write security
   descriptor in memory and compute stable fingerprints for every ACE using
   identity, access-control type, rights, inheritance flags, propagation
   flags, and inherited state.
5. Select exactly the two non-inherited Deny rule objects for the stated SID.
   Require that they are the same two risky root rules reported by Check mode.
   Stop without writing if selection is zero, one, greater than two, or
   otherwise differs from the precondition.
6. Clone the descriptor in memory, call `RemoveAccessRuleSpecific` once for
   each selected rule object, and prove in memory that:
   the two target fingerprints are absent; every non-target fingerprint is
   unchanged; both required Modify allows remain present; and no new ACE
   exists.
7. Apply the in-memory descriptor once with `Set-Acl -LiteralPath .codex`.
   Do not call `SetAccessRule`, `ResetAccessRule`, inheritance-changing APIs,
   recursive traversal, or any descendant write.
8. Immediately read exact `.codex` again and require:
   zero target Deny fingerprints; exact equality of every non-target ACE
   fingerprint; unchanged owner and inheritance-protection state; and both
   required Modify allows present.
9. Re-run the governed Check mode and require 218 objects checked, zero
   errors, zero risky Deny rules, zero descendant risky Deny rules, both
   required allows present, and `needs_repair=false`.
10. Run `python scripts/verify_codex_dispatch.py --json` read-only. Require
    ACL readiness true. If the then-current independently governed no-window
    proof is still valid and the operative verifier accepts it, also require
    `can_receive_dispatch=true` and `dispatchable=true`. If that separate proof
    has expired or fails under a strengthened verifier, stop and report the
    exact canonical classification; do not renew it under this revision.
11. Use only read-only `gt bridge dispatch status --json`,
    `gt bridge dispatch health --json`, and
    `gt bridge dispatch report --json` for post-repair dispatcher observation.
12. File a canonical implementation report containing only canonical
    identifiers, bounded command-result summaries, the before/after ACE
    fingerprint counts, the test mapping, and the readiness classification.

## Bounded Rollback

Before the write, retain the complete exact-root security descriptor in memory.
If the immediate exact-root readback shows any non-target ACE, owner,
inheritance-protection, or required-Allow change, restore that exact in-memory
descriptor once with `Set-Acl`, re-read it, and file a blocker implementation
report. Rollback does not authorize recursive writes or speculative ACL
normalization.

If the root readback is exact but a later read-only descendant check observes
an unrelated concurrent descendant change, do not overwrite the correct root
repair. Stop and report the discrepancy through the bridge.

## Explicit Exclusions

- No dispatcher configuration, routing, eligibility, roles, models, caps,
  selection order, TAFE state, runtime JSON, leases, locks, quiesce, or live
  worker mutation.
- No change to harness dispatchability. A remains Prime Builder only; D and F
  remain Loyal Opposition.
- No direct or manual harness contact, smoke run, proof renewal, dispatch,
  reoffer, or provider call.
- No source, test, formal-artifact, database, credential, deployment, or
  release mutation.
- No `.codex` descendant ACL or file-content mutation and no recursive
  operation.
- No Git staging, commit, push, history rewrite, cleanup, or adoption of
  unrelated worktree changes.
- No weakening of ACL checks, no-window containment, effective-profile checks,
  diagnostic strictness, or fail-closed readiness.

## Requirement Sufficiency

Existing requirements are sufficient for the immediate repair.
WI-5250, TEST-11404, the active project authorization, and the linked
specifications require exact readiness restoration, A's Prime-Builder-only
role, dispatcher non-mutation, and independent verification. Version 016
supplies the approved correction branch for a regressed ACL state.

The causal durability question is a distinct requirement and is captured in
WI-5571 with TEST-11622. It does not broaden the target or mutation authority
of this proposal.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-202666203` authorizes governed restoration of Codex A readiness while
  preserving bridge, independent review, and dispatcher-state boundaries.
- `DELIB-202666274` supplies the active project authorization and preserves
  exact claim, implementation-start, independent verification, and
  mechanical-operation gates.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-015.md` records the failed
  approved mechanism and unchanged post-attempt state.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-016.md` independently
  authorizes this corrected branch if the ACL state regresses.
- `bridge/gtkb-wi5065-codex-dotdir-acl-drive-sync-durable-fix-004.md` and
  `bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md` are terminal
  predecessors whose verified checks remain preserved.

## Owner Decisions / Input

No new owner decision is required. The state has regressed, so version 016
already identifies the corrected exact-ACE-object path. The owner has also
required Codex A to remain dispatchable and has prohibited treating the
window issue as a reason to disable a harness. This revision preserves those
constraints and the separate standing prohibition on dispatcher configuration
changes.

## Specification-Derived Verification

| Requirement | Executed evidence required in the implementation report |
| --- | --- |
| `TEST-11404`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Exact-root ACL repair passes and the canonical readiness verifier reports ACL readiness true; when the separate no-window proof is current and accepted, A reports dispatchable. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Required current-user and CodexSandboxUsers Modify allows remain present; only the two target Deny rules are removed. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Read-only role/status evidence confirms A remains Prime Builder only. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Independent GO, matching claim, and exact implementation-start authorization precede the write. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact `.codex` is admitted and representative descendants and excluded surfaces are rejected at operation time. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Dispatcher observations are read-only and topology/configuration remains unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reproduces the before/after fingerprint assertions, Check-mode result, and readiness classification before VERIFIED. |
| Canonical-reference boundary | The report contains canonical identifiers and bounded observed command results only. |

## Acceptance Criteria

- Independent GO, matching claim, and schema-v3 implementation-start
  authorization are current for version 017.
- Exact `.codex` is admitted and every representative excluded target is
  rejected.
- The pre-check observes exactly two target root Deny rules, zero descendant
  risky Deny rules, zero read errors, and both required allows.
- Exactly those two rule objects are removed; every non-target root ACE,
  owner, and inheritance-protection property is unchanged.
- The post-check reports zero risky Deny rules, zero read errors, both required
  allows, and `needs_repair=false`.
- The canonical readiness verifier reports ACL readiness true and accurately
  reports the independent no-window proof state without renewal.
- A remains PB-only and selected under the unchanged current topology.
- No excluded mutation or unrelated worktree adoption occurs.
- An independent LO verdict verifies the bounded operational evidence.
- WI-5571 remains open to prove durability; this one-time repair does not claim
  the recurrence cause is solved.

## Pre-Filing Preflight Subsection

The governed revision helper must pass the applicability preflight with no
missing required or advisory specifications and the mandatory clause preflight
with zero blocking gaps against this exact content before publication.

## Risk And Rollback

ACL mutation can accidentally alter permissions beyond the intended Deny
rules. Exact object selection, complete non-target fingerprints, a single root
write, immediate readback, and bounded in-memory rollback constrain that risk.
The operation fails closed if the live state differs from the exact two-rule
precondition.

The repair may still leave A non-dispatch-ready if the separate no-window proof
expires or a strengthened verifier rejects it. That outcome is reported
honestly and routed through its existing governed work; this proposal does not
silently broaden itself into proof renewal.

The shared worktree remains heavily occupied by unrelated owner and peer work.
Exact `.codex` root metadata does not authorize any descendant content, staging,
cleanup, or peer-work adoption.
