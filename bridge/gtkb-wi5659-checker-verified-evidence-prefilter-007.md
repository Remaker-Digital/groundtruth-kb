REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 87ea6b9f-89d5-4e90-a637-a7f9fe8cb561
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Revised Implementation Proposal - Restore governed commit finalization: evidence pre-filter (done) + batch prospective-tree materialization

bridge_kind: prime_proposal
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 007
Date: 2026-07-23 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-006.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note (addresses NO-GO at -006)

The -006 NO-GO was correct and its F1 finding is confirmed. The v005 report
proved the pre-filter in isolation but never timed the end-to-end
`check_protected_commit_authorization.py --staged` finalization path -- the exact
path the finalizer runs. Diagnosis below identifies a SECOND, much larger
hotspot that the approved pre-filter does not touch. This REVISED proposal
requests scope expansion (same two target paths, same PAUTH) to fix it.

## Diagnosis (root cause of the >8-minute finalizer block)

`_evaluate_selected` calls `_load_transaction_verified_evidence` when a VERIFIED
candidate is staged -- which is true only during a governed VERIFIED
finalization, and was therefore never exercised by the v005 evidence. That path
runs `_bridge_snapshot(root, bridge_id, index_snapshot)`, whose
`index_snapshot is not None` branch calls `_materialize_index_tree` ->
`_materialize_entries(_index_entries(...))`. `_index_entries` is
`ls-files --stage`, i.e. **every index entry (19,090 files)**, and
`_blob_ledger_entry` spends **two subprocess spawns per entry**
(`cat-file -s` + `Popen cat-file blob`).

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
complete and had ~46 minutes remaining. This fully explains F1 and is
independent of the pre-filter.

The v004-approved pre-filter is correct and effective for its own target:
`_load_verified_evidence` went from 460.824s to 9.564s on the live 472-packet
load, and all 100 checker tests plus both ruff gates pass. It is necessary but
not sufficient to restore governed finalization.

## Requested Scope Expansion

Same two target paths and the same active implementation PAUTH (`source`,
`test`). No new protected files. Added technical scope:

1. Replace the per-entry two-spawn materialization loop with a single streaming
   `git cat-file --batch` process that reads all requested object ids and writes
   each blob to its destination.
2. Preserve every existing security and integrity property:
   - **index-completeness** of the prospective tree (all index entries still
     materialized -- `test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper` must still pass);
   - per-blob declared-size check and per-blob object-hash verification
     (`blob <size>\0` + content hashed and compared to the index oid);
   - `MAX_BLOB_BYTES` per-blob and `MAX_TREE_BYTES` cumulative limits;
   - destination path/link-safety checks (`_path_is_linklike`, escape-from-root
     rejection, parent mkdir);
   - fail-closed on a `missing`/`ambiguous` batch response or any hash/size
     mismatch, with the same `GateError` semantics.
3. Keep the ledger contents byte-identical to the current implementation, so all
   downstream snapshot-immutability and audit checks are unaffected.
4. Retain the already-implemented pre-filter (v004 scope) unchanged.

Out of scope: any change to WHAT is materialized (index-completeness is a
deliberate hermetic-audit security property and is preserved), any
authorization-semantics change, and any adjacent WI-5657/WI-5658/WI-5441 work.

## Claim

Prime Builder proposes the minimum additional change that makes WI-5659 achieve
its stated purpose -- restoring governed commit finalization -- by removing the
dominant per-entry process-spawn cost while preserving all hermetic-audit
guarantees.

## Requirement Sufficiency

Existing requirements are sufficient. `DELIB-202667184` authorizes fixing the
real finalizer hang in these two target paths with no semantic outcome change;
the diagnosis shows the real hang has two components. No new requirement is
needed.

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

- `DELIB-202667184` - owner decision authorizing the bounded WI-5659 finalizer fix (source+test, no semantic change).
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-006.md` - the NO-GO whose F1 finding this revision diagnoses and fixes.
- `bridge/gtkb-wi5659-checker-verified-evidence-prefilter-004.md` - the GO whose pre-filter scope is retained unchanged.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-002.md` - preceding checker-perf slice (WI-5658), the first spawn-cost reduction in this file.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | END-TO-END: time the real `check_protected_commit_authorization.py --staged` run against a finalization-shaped staged set (source+test+bridge chain+VERIFIED candidate) and assert it completes in seconds, not minutes. This is the evidence -006 required and v005 lacked. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ledger-equivalence test: batch materialization produces a ledger byte-identical to the per-entry path over the same entries. Tamper test: a blob whose content does not hash to its index oid still raises `GateError`. Limit tests: `MAX_BLOB_BYTES` and `MAX_TREE_BYTES` still enforced. Missing-object test: a `missing` batch response fails closed. Existing `test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper` must still pass unchanged (index-completeness + live-gate-tamper resistance). |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH, project, WI-5659, target paths, owner decision cited above. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files are in-root platform paths. |

## Acceptance Criteria

- The real `--staged` finalization path completes in seconds (target < 60s; measured baseline 50.7 min for the materialization alone).
- The prospective tree remains index-complete; `test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper` passes unchanged.
- Batch-produced ledger is byte-identical to the per-entry ledger for the same entries.
- Hash-mismatch, missing-object, and size-limit conditions still fail closed with `GateError`.
- All existing checker tests plus the 5 WI-5659 tests pass; ruff check and ruff format --check clean.
- The VERIFIED finalizer transaction completes and produces a real commit.

## Risks / Rollback

Risk is moderate-to-high because `_materialize_entries` feeds the hermetic
compliance audit. Mitigation: index-completeness and every per-blob verification
are preserved by construction; the ledger-equivalence and tamper tests are the
guard. A streaming parser must be strict about the `<oid> <type> <size>` header,
the exact `size` byte count, and the trailing newline; malformed or `missing`
responses fail closed.

Rollback is a revert of the WI-5659 hunks in the two target paths. Bridge files
and PAUTH records are append-only.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Owner Decisions / Input

- `DELIB-202667184` - owner AUQ decision (2026-07-23) authorizing the bounded WI-5659 finalizer fix in these two target paths, source+test, no semantic outcome change. The scope expansion requested here stays inside that decision's target paths, mutation classes, and forbidden-operation boundaries.
- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` - active implementation authorization (source+test) for WI-5659.

## Recommended Commit Type

`perf`
