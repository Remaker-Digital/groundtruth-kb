REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Revised Implementation Proposal - Restore governed commit finalization: evidence pre-filter (implemented) + batch prospective-tree materialization (newly authorized)

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 009
Date: 2026-07-23 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-008.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note (addresses NO-GO at -008)

The -008 NO-GO (F1) was correct: version 007 requested the batch materialization
mechanism while the cited authority record -- `DELIB-202667184`, the PAUTH scope
summary, and the WI-5659 record -- named only the verified-evidence pre-filter.
Target-path and mutation-class compatibility are necessary but not sufficient,
and LO was right to refuse to expand implementation authority by interpretation.

Durable authority now exists. All three surfaces the -008 review inspected have
been updated through the governed path BEFORE this refiling:

1. **Owner decision:** `DELIB-202667185` (`source_type=owner_conversation`,
   `outcome=owner_decision`, `work_item_id=WI-5659`), recorded via
   `gt deliberations record` from an AskUserQuestion. The owner selected "Expand
   WI-5659's existing authority" and separately stated: "I approve fixing the
   materialization path."
2. **PAUTH v2:** `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX`
   is now version 2, `status=active`, `owner_decision_deliberation_id=DELIB-202667185`,
   and its scope summary explicitly names BOTH mechanisms, including the
   streaming `git cat-file --batch` prospective-tree materialization and the
   preserved security properties.
3. **WI-5659 v2:** title and description updated to describe both mechanisms and
   the required end-to-end verification.

Nothing else changed from version 007: same two target paths, same mutation
classes, same forbidden operations, same technical scope, same verification plan.

## Diagnosis (unchanged from v007; root cause of the >8-minute finalizer block)

`_evaluate_selected` calls `_load_transaction_verified_evidence` when a VERIFIED
candidate is staged -- true only during a governed VERIFIED finalization, which
is why the v005 evidence never exercised it. That path runs
`_bridge_snapshot(root, bridge_id, index_snapshot)`, whose
`index_snapshot is not None` branch calls `_materialize_index_tree` ->
`_materialize_entries(_index_entries(...))`. `_index_entries` is
`ls-files --stage`, i.e. **every index entry (19,090 files)**, and
`_blob_ledger_entry` spends **two subprocess spawns per entry**.

Measured on this repository (read-only probes, real index entries):

```text
index entries (ls-files)          : 19090
A current path       (150 entries):  23.90s ->  159.4 ms/entry  => 50.7 min full index
B spawn-only, no write/no hash    :  20.47s ->  136.4 ms/entry  => 86% of cost is spawn
C `git cat-file --batch` prototype:   0.16s ->    1.1 ms/entry  => 0.3 min (18s) full index
                                     (still writes every file AND verifies every
                                      object hash; verified=150)  speedup 151x
```

The LO stopped the finalizer at ~8 minutes; at 159.4 ms/entry it was roughly 9%
complete with ~46 minutes remaining. Because 86% of the cost is process spawn
rather than file I/O or hashing, batching is the correct remedy.

Mechanism 1 (the v004-approved pre-filter) is implemented and effective for its
own target: `_load_verified_evidence` went from 460.824s to 9.564s on the live
472-packet load, with 100 checker tests and both ruff gates passing. It is
necessary but not sufficient to restore governed finalization.

## Proposed Scope

Same two target paths; same active PAUTH (now v2). Two mechanisms:

1. **Retained, already implemented:** the `_load_verified_evidence`
   `protected_paths` pre-filter from the v004 GO, unchanged.
2. **Newly authorized:** replace the per-entry two-spawn materialization loop
   with a single streaming `git cat-file --batch` process that reads all
   requested object ids and writes each blob to its destination.

Mechanism 2 changes only HOW blobs are fetched, never WHAT is materialized.
Preserved by construction and asserted by tests:

- **index-completeness** of the prospective tree; existing
  `test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper`
  must pass unchanged;
- per-blob declared-size check and per-blob object-hash verification
  (`blob <size>\0` + content hashed and compared to the index oid);
- `MAX_BLOB_BYTES` per-blob and `MAX_TREE_BYTES` cumulative limits;
- destination path/link-safety checks (`_path_is_linklike`), escape-from-root
  rejection, parent mkdir;
- fail-closed `GateError` on a `missing`/`ambiguous` batch response or any
  hash/size mismatch;
- byte-identical ledger contents, so downstream snapshot-immutability and audit
  checks are unaffected.

Out of scope: any change to what is materialized, any authorization-semantics
change, and any adjacent WI-5657 / WI-5658 / WI-5441 / WI-5440 work.

## Claim

Prime Builder proposes the minimum additional change that lets WI-5659 achieve
its stated purpose -- restoring governed commit finalization -- now backed by
matching durable authority on all three surfaces the -008 review inspected.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667184` authorizes mechanism 1
and `DELIB-202667185` authorizes mechanism 2, both bounded to the same target
paths and mutation classes. No new or revised requirement is needed.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the commit-finalization gate must complete as a pre-commit hook.
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

## Prior Deliberations

- `DELIB-202667185` - owner decision authorizing batch prospective-tree materialization within WI-5659 (the authority the -008 NO-GO required).
- `DELIB-202667184` - owner decision authorizing the bounded WI-5659 finalizer pre-filter fix.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-008.md` - the NO-GO whose F1 authority finding this revision resolves.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-006.md` - the NO-GO that first observed the >8-minute finalizer block.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-004.md` - the GO whose pre-filter scope is retained unchanged.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-002.md` - preceding checker-perf slice (WI-5658), the first spawn-cost reduction in this file.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | END-TO-END: time the real `check_protected_commit_authorization.py --staged` run against a finalization-shaped staged set (source+test+bridge chain+VERIFIED candidate) and assert it completes in seconds, not minutes. This is the evidence -006 required and v005 lacked. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ledger-equivalence test: batch materialization produces a ledger byte-identical to the per-entry path over the same entries. Tamper test: a blob whose content does not hash to its index oid still raises `GateError`. Limit tests: `MAX_BLOB_BYTES` and `MAX_TREE_BYTES` still enforced. Missing-object test: a `missing` batch response fails closed. Existing `test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper` must still pass unchanged. Plus the 5 existing WI-5659 pre-filter tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v2 (naming both mechanisms), project, WI-5659 v2, target paths, and owner decisions `DELIB-202667184` + `DELIB-202667185` all cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files are in-root platform paths. |

## Acceptance Criteria

- The real `--staged` finalization path completes in seconds (target < 60s; measured baseline 50.7 min for materialization alone).
- The prospective tree remains index-complete; the existing tamper/index-completeness test passes unchanged.
- Batch-produced ledger is byte-identical to the per-entry ledger for the same entries.
- Hash-mismatch, missing-object, and size-limit conditions still fail closed with `GateError`.
- All existing checker tests plus the 5 WI-5659 pre-filter tests pass; ruff check and ruff format --check clean.
- The VERIFIED finalizer transaction completes and produces a real commit.

## Risks / Rollback

Risk is moderate-to-high because `_materialize_entries` feeds the hermetic
compliance audit. Mitigation: index-completeness and every per-blob verification
are preserved by construction; ledger-equivalence and tamper tests are the guard.
The streaming parser must be strict about the `<oid> <type> <size>` header, the
exact `size` byte count, and the trailing newline; malformed, `missing`, or
`ambiguous` responses fail closed.

Rollback is a revert of the WI-5659 hunks in the two target paths. Bridge files,
deliberations, and PAUTH records are append-only.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Owner Decisions / Input

- `DELIB-202667185` - owner AUQ decision (2026-07-23) authorizing batch prospective-tree materialization as an expansion of WI-5659's existing authority. Owner answer: "Expand WI-5659's existing authority"; owner also stated "I approve fixing the materialization path." This is the authority the -008 NO-GO required.
- `DELIB-202667184` - owner AUQ decision (2026-07-23) authorizing the bounded WI-5659 finalizer pre-filter fix (source+test, no semantic outcome change).
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v2 - active implementation authorization (source+test) whose scope summary explicitly names both mechanisms and the preserved security properties.

## Recommended Commit Type

`perf`
