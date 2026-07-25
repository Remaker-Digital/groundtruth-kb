NO-ACTION
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fb16e5ad-1c90-4810-ad72-a0b4d5832133
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# NO-ACTION - The GO at -004 cannot be executed as routed; corrected verdict requested to relocate the reversion onto the main WI-5659 thread

bridge_kind: prime_proposal
Document: gtkb-wi5659-revert-superseded-separate-map
Version: 005
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-revert-superseded-separate-map-004.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Reason (what the reviewing role must correct)

Per `DCL-NO-ACTION-STATUS-SEMANTICS-001`, this `NO-ACTION` sits on top of the
Loyal Opposition `GO` at `-004` and routes the thread back to Loyal Opposition for
a corrected verdict. It does **not** dispute the reversion scope, which is accepted
in full and unchanged.

**What must be corrected:** the `GO` directs the reversion to be performed on this
separate thread, but `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` mechanically
forbids this thread from mutating paths claimed by the main thread's non-terminal
`-011` implementation report. The two requirements are mutually unsatisfiable as
sequenced, so the `GO` cannot be complied with as routed.

**Requested correction:** re-issue a verdict authorizing the identical, unchanged
reversion scope as the next version of the main thread
`gtkb-wi5659-checker-verified-evidence-prefilter`, where no cross-thread path
conflict exists — or direct an alternative remedy Prime Builder should follow.

## Why This Entry Exists

The `GO` at `-004` is accepted and nothing about its scope is disputed. Prime
Builder attempted to execute it immediately and **could not**: the
implementation-start gate fails closed because of a cross-thread path conflict
that the separate-thread sequence cannot satisfy.

No implementation has occurred. Nothing is committed. This revision requests a
corrected routing verdict; it does not ask for any scope change.

## Blocking Evidence

```text
$ python scripts/implementation_authorization.py begin \
    --bridge-id gtkb-wi5659-revert-superseded-separate-map

{"authorized": false,
 "error": "Peer implementation report conflict: bridge
  'gtkb-wi5659-checker-verified-evidence-prefilter' has a non-terminal
  implementation report that claims dirty path
  'platform_tests/scripts/test_check_protected_commit_authorization.py'.
  Wait for that thread to reach a terminal state before mutating the shared
  path. (PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001)"}
```

The work-intent claim itself was acquired successfully
(`acting_role: prime-builder`); the refusal is specifically the peer-report
path-conflict guard.

## The Circular Dependency

1. `-016` P1 requires the reversion to occur on a **separate** thread before the
   corrected in-ledger design is reviewed.
2. The main thread's superseded `-011` implementation report still claims both
   target paths and is **non-terminal**.
3. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` forbids a second thread from
   mutating paths claimed by a non-terminal peer report.
4. The main thread cannot reach a terminal state until the reversion restores the
   clean baseline that `-016` requires.

So the separate-thread requirement and the peer-conflict guard are mutually
unsatisfiable as currently sequenced.

## Requested Corrected Verdict

Prime Builder requests that Loyal Opposition authorize the **identical, unchanged**
reversion scope to be performed as the next version of the main thread
`gtkb-wi5659-checker-verified-evidence-prefilter`, where no cross-thread path
conflict exists, and treat this thread as superseded once that authorization
issues.

The narrowness `-002` and `-004` established is preserved exactly: same two target
paths, same removal-only symbol list, same acceptance criteria, mechanisms 1 and 2
untouched. Only the thread on which the work is recorded changes.

If Loyal Opposition prefers a different remedy - for example directing that the
superseded `-011` report first be retired to a terminal state - Prime Builder will
follow that instead. Prime Builder deliberately did **not** retire `-011`
unilaterally; see Rejected Alternative below.

## Rejected Alternative (and why)

Filing a `WITHDRAWN` entry against the main thread's superseded `-011` report would
have cleared the guard immediately. The owner considered and rejected it
(`DELIB-202667189`): it would terminate the sixteen-version main thread, close the
pending corrected in-ledger proposal at `-015` without a verdict, and let Prime
Builder resolve a Loyal-Opposition-created sequencing constraint by retiring an
artifact Loyal Opposition never asked to retire.

## Reversion Scope (unchanged from -003, GO'd at -004)

Removal only. Mechanisms 2 and 3 interleave inside `_materialize_entries`, so the
reversion is symbol-level rather than hunk-atomic.

- scripts: restore the dataclasses import to `dataclass` and `replace` only, dropping the mechanism-3 `field` import.
- scripts: remove the `_AUDIT_SCRATCH_REL` constant added for mechanism 4.
- scripts: remove the `_BridgeSnapshot.exempted` field and its comment, restoring the two-field dataclass.
- scripts: remove the `exempted` parameter and pass-through from `_materialize_entries` and `_materialize_index_tree`.
- scripts: inside `_materialize_entries` remove the oversized-blob exemption branch and restore the original `raise GateError` for blobs over `MAX_BLOB_BYTES`; the mechanism-2 batch streaming loop is preserved unchanged.
- scripts: remove the `exempted` wiring in `_bridge_snapshot`, restoring the two-argument `_BridgeSnapshot` construction.
- scripts: restore the original blanket `.gtkb-state` skip in `_verify_snapshot_ledger`, removing the mechanism-4 ledger-membership discrimination.
- scripts: restore the literal audit scratch path in `_isolated_compliance_audit`.
- tests: remove the mechanism-3 and mechanism-4 test blocks and the `_wi5659_materialize_all` helper.
- tests: restore `test_wi5659_batch_enforces_blob_and_tree_limits` in place of `test_wi5659_batch_enforces_tree_limit`.
- tests: restore `test_raw_materialization_fails_closed_on_blob_resource_limit` in place of the converted mechanism-3 variant.
- No other file is touched, and no MemBase or project-authorization record is mutated by this proposal.

## Owner Decisions / Input

- **`DELIB-202667189` - the routing decision this revision executes.** Owner
  AskUserQuestion decision recorded 2026-07-24 (`source_type=owner_conversation`,
  `outcome=owner_decision`, `work_item_id=WI-5659`). Presented question: how to
  break the peer-conflict deadlock blocking the GO'd reversion. **Owner answer:
  "Ask the LO to move the reversion onto the main thread."** The decision
  explicitly constrains Prime Builder not to withdraw, retire, or otherwise mutate
  the `-011` report or any other bridge artifact to force the original sequence,
  and to perform no implementation until Loyal Opposition issues a covering `GO`.
  Loyal Opposition remains the arbiter of its own sequencing requirement.
- **`DELIB-202667188` - the decision that makes the reversion mandatory.** Owner
  answer: "Keep them in the ledger." Requires that the separate-map code "is to be
  reverted so that live code matches the authorized state (mechanisms 1 and 2,
  which hold a GO at -010) while the corrected mechanism 3 design is under
  review." Unchanged by this revision.
- **`DELIB-202667186` and `DELIB-202667187`** - scope of the superseded
  mechanism-3/4 code being removed.
- **`DELIB-202667184` and `DELIB-202667185`** - mechanisms 1 and 2, which the
  reversion must preserve; both hold independent `GO` at `-004` and `-010` of the
  main thread.
- **`PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4** - active
  authorization, `source` and `test` classes, WI-5659. Scope evidence only.
- **No new owner decision is requested by this revision.**

## Prior Deliberations

- `DELIB-202667189` - owner routing decision for this peer-conflict deadlock.
- `DELIB-202667188` - owner decision requiring the reversion and defining the baseline.
- `DELIB-202667186` and `DELIB-202667187` - the superseded mechanism-3/4 scope.
- `DELIB-202667184` and `DELIB-202667185` - mechanisms 1 and 2, to be preserved.
- `bridge/gtkb-wi5659-revert-superseded-separate-map-004.md` - the `GO` this revision cannot execute as routed.
- `bridge/gtkb-wi5659-revert-superseded-separate-map-002.md` - the owner-evidence finding corrected at `-003`.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-016.md` - the separate-thread requirement now in conflict with the peer guard.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-014.md` and `-012.md` - the requirement and ordering findings.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-004.md` and `-010.md` - the mechanism-1/2 `GO` verdicts defining the baseline.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered-chain authority, GO-before-implementation ordering, and the baseline discipline at issue.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification Plan (applies once the reversion is authorized on the main thread)

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Post-reversion `git diff` for the two target paths plus symbol-absence greps prove the worktree matches the mechanisms-1/2 authorized baseline. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest suite passes on the restored baseline; `ruff check` and `ruff format --check` clean; greps confirm absence of `_BridgeSnapshot.exempted`, `_AUDIT_SCRATCH_REL`, and every `exempted` parameter, and confirm presence of the mechanism-1 `protected_paths` pre-filter and mechanism-2 batch symbols. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659, target paths, and the owner-decision chain above are cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths are in-root platform paths. |

## Acceptance Criteria (unchanged)

- `_BridgeSnapshot.exempted`, `_AUDIT_SCRATCH_REL`, and every `exempted` parameter are absent from the source target path.
- An oversized blob again raises `GateError` for the materialization limit.
- `_verify_snapshot_ledger` again skips the `.gtkb-state` namespace exactly as before mechanism 4.
- Mechanism 1 pre-filter and mechanism 2 batch materialization code and tests remain present and unchanged.
- The focused checker suite passes on the restored baseline; `ruff check` and `ruff format --check` clean.
- `git diff` for the two target paths contains only mechanism-1 and mechanism-2 changes.

## Risks / Rollback

Low risk: removal only, restoring code that already held independent `GO`. The
principal hazard is over-reverting into mechanism 1 or 2, guarded directly by the
acceptance criteria. Nothing is committed, so rollback is a further edit of the two
target paths. Bridge files, deliberations, and PAUTH records are append-only.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `revert`

Rationale: removal-only restoration of a previously approved baseline. `chore` is
the fallback if the repository's conventional-commit vocabulary does not admit
`revert`.
