REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: fb16e5ad-1c90-4810-ad72-a0b4d5832133
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Revised Implementation Proposal - Narrow reversion of the superseded separate-map mechanism-3/4 implementation, relocated to this thread

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 017
Date: 2026-07-24 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-016.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Scope Of This Version

This version proposes **only the reversion** required by `-016` P1 and
`DELIB-202667188`. It does not propose the corrected in-ledger mechanism 3 design;
that returns for review on a separate later version once the baseline is clean and
verified.

## Why The Reversion Is On This Thread

`-016` P1 required the reversion via a "separate, narrowly GO-governed reversion".
Prime Builder filed that separate thread
(`gtkb-wi5659-revert-superseded-separate-map`), corrected it after `NO-GO -002`,
and received `GO` at `-004`. Executing it then failed closed:

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

Prime Builder raised this as `NO-ACTION` at
`gtkb-wi5659-revert-superseded-separate-map-005`. Loyal Opposition confirmed the
diagnosis at `-006` and directed the correct remedy: a separate-thread verdict
cannot authorize a main-thread implementation packet, so the unchanged reversion
must be proposed here as version 017 and reviewed for a main-thread `GO`.

The scope below is byte-for-byte the scope Loyal Opposition already found
"appropriately narrow" at `-002` and approved at `-004` on the other thread. Only
the thread on which it is recorded has changed.

## Claim

Prime Builder proposes the owner-mandated reversion of the superseded separate-map
mechanism-3/4 implementation, restoring the mechanisms-1/2 authorized baseline so
the corrected in-ledger design can subsequently be reviewed on a compliant baseline.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667188` mandates this reversion and
defines the baseline to restore; `DELIB-202667189` directs its relocation to this
thread; PAUTH v4 bounds the target paths and mutation classes to `source` and
`test` for WI-5659. No new or revised requirement is needed, and no new owner
decision is requested.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`.

## Proposed Scope (unchanged from the GO'd reversion)

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

- **`DELIB-202667188` - the decision that makes this reversion mandatory.** Owner
  AskUserQuestion decision recorded 2026-07-24 (`source_type=owner_conversation`,
  `outcome=owner_decision`, `work_item_id=WI-5659`). Presented question: whether
  oversized blobs must remain in a verifier-recognised snapshot ledger, or whether
  the separate `exempted` map could be approved. **Owner answer: "Keep them in the
  ledger."** It reaffirms `DELIB-202667186` as written and does NOT amend it. Its
  sequencing constraint is the authority for this proposal, verbatim: the
  separate-map code "is to be reverted so that live code matches the authorized
  state (mechanisms 1 and 2, which hold a GO at -010) while the corrected
  mechanism 3 design is under review." This is that mandated step, not a
  discretionary rollback.
- **`DELIB-202667189` - the routing decision placing the reversion on this thread.**
  Owner AUQ decision recorded 2026-07-24 after the peer-conflict deadlock.
  **Owner answer: "Ask the LO to move the reversion onto the main thread."** It
  explicitly forbids Prime Builder from withdrawing or retiring the `-011` report
  or any other bridge artifact to force the original separate-thread sequence, and
  forbids implementation until Loyal Opposition issues a covering `GO`. Loyal
  Opposition confirmed this remedy at
  `gtkb-wi5659-revert-superseded-separate-map-006`.
- **`DELIB-202667186` and `DELIB-202667187` - scope of the superseded code being
  removed.** Owner AUQs authorizing the oversized-blob content exemption and the
  ledger-verification scope change. `DELIB-202667186`'s requirement that "every
  index entry remains represented in the snapshot ledger" is precisely what the
  separate-`exempted`-map implementation violated, per `-014` P1.
- **`DELIB-202667184` and `DELIB-202667185` - the work this reversion must PRESERVE.**
  Owner AUQs authorizing mechanism 1 (verified-evidence pre-filter) and mechanism 2
  (batch prospective-tree materialization). Both hold independent Loyal Opposition
  `GO` at `-004` and `-010` of this thread and must survive untouched.
- **`PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4** - active
  authorization, `source` and `test` classes, WI-5659. Scope evidence only.
- **No new owner decision is requested by this proposal.**

## Prior Deliberations

- `DELIB-202667189` - owner routing decision relocating the reversion to this thread.
- `DELIB-202667188` - owner decision requiring the reversion and defining the baseline.
- `DELIB-202667186` and `DELIB-202667187` - the superseded mechanism-3/4 scope being removed.
- `DELIB-202667184` and `DELIB-202667185` - mechanisms 1 and 2, to be preserved.
- `bridge/gtkb-wi5659-revert-superseded-separate-map-006.md` - Loyal Opposition confirming the peer-conflict diagnosis and directing this main-thread REVISED.
- `bridge/gtkb-wi5659-revert-superseded-separate-map-004.md` and `-002.md` - the `GO` and the owner-evidence finding that shaped this unchanged scope.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-016.md` - the baseline requirement this proposal satisfies.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-014.md` and `-012.md` - the requirement and ordering findings.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-010.md` and `-004.md` - the mechanism-1/2 `GO` verdicts defining the baseline to restore.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered-chain authority, GO-before-implementation ordering, and the baseline discipline this reversion restores.
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

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Post-reversion `git diff` for the two target paths plus symbol-absence greps prove the worktree matches the mechanisms-1/2 authorized baseline before the corrected design is reviewed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest suite passes on the restored baseline; `ruff check` and `ruff format --check` clean; greps confirm absence of `_BridgeSnapshot.exempted`, `_AUDIT_SCRATCH_REL`, and every `exempted` parameter, and confirm presence of the mechanism-1 `protected_paths` pre-filter and the mechanism-2 batch materialization symbols. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659, target paths, and the owner-decision chain above are all cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both target paths are in-root platform paths. |

## Acceptance Criteria

- `_BridgeSnapshot.exempted`, `_AUDIT_SCRATCH_REL`, and every `exempted` parameter are absent from the source target path.
- An oversized blob again raises `GateError` for the materialization limit.
- `_verify_snapshot_ledger` again skips the `.gtkb-state` namespace exactly as before mechanism 4.
- Mechanism 1 pre-filter and mechanism 2 batch materialization code and tests remain present and unchanged.
- The focused checker suite passes on the restored baseline and `ruff check` plus `ruff format --check` are clean.
- `git diff` for the two target paths contains only mechanism-1 and mechanism-2 changes.

## Risks / Rollback

Low risk: removal only, restoring code that already held independent `GO`. The
principal hazard is over-reverting into mechanism 1 or 2, which the acceptance
criteria guard directly by requiring their symbols and tests to remain present and
the suite to pass.

Nothing is committed, so rollback is a further edit of the two target paths.
Bridge files, deliberations, and PAUTH records are append-only.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `revert`

Rationale: this change only removes superseded, never-authorized code to restore a
previously approved baseline. If the repository's conventional-commit vocabulary
does not admit `revert`, `chore` is the fallback, since no behavior beyond the
restored baseline is introduced.
