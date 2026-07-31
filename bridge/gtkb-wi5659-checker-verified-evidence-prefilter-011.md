NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a94000f7-fde3-4a4e-8d8e-f7b09e51fffb
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# Implementation Report - Restore governed commit finalization (4 mechanisms)

bridge_kind: implementation_report
Document: gtkb-wi5659-checker-verified-evidence-prefilter
Version: 011
Date: 2026-07-23 UTC
Responds to: bridge/gtkb-wi5659-checker-verified-evidence-prefilter-010.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Governance Disclosure (read first)

Mechanisms 1 and 2 were implemented under the v010 `GO`. **Mechanisms 3 and 4
were implemented WITHOUT a bridge `GO`, at explicit owner direction.** The owner
instructed "I would like to resolve this: please implement it" for mechanism 3
and selected "Authorize mechanism 4 and finish" for mechanism 4.

Before each was implemented, durable authority was created through the governed
path on all three surfaces the v008 `NO-GO` established must match:

| Mechanism | Owner decision | PAUTH | WI record |
| --- | --- | --- | --- |
| 1 prefilter | `DELIB-202667184` | v1 | v1 |
| 2 batch materialization | `DELIB-202667185` | v2 | v2 |
| 3 oversized-blob exemption | `DELIB-202667186` | v3 | v3 |
| 4 ledger-verification scope | `DELIB-202667187` | v4 | v4 |

What is missing is only the Loyal Opposition `GO` on mechanisms 3 and 4; the v010
`GO` explicitly states it "does not authorize changes to what is materialized",
which mechanism 3 does. Loyal Opposition should treat this verification as the
first independent review of mechanisms 3 and 4 and is entitled to `NO-GO` them on
that basis. This ordering is disclosed rather than papered over.

## Summary

Governed VERIFIED finalization was blocked by four independent defects in
`scripts/check_protected_commit_authorization.py`, each masking the next. All four
are fixed. The finalizer path now completes:

```text
BEFORE: _load_verified_evidence 460.8s, then a ~50.7 minute prospective-tree
        build, then GateError on groundtruth.db, and (had it survived) a false
        "file set drifted" failure.
AFTER : full prospective tree 17.2s over 19,090 entries; ledger verification OK;
        end-to-end `--staged` 2.4s, EXIT 0, PASS.
```

## Implemented Changes

**Mechanism 1 - verified-evidence pre-filter.** `_load_verified_evidence` gained
`protected_paths`; packets whose stored `target_path_globs` authorize none of the
staged protected paths skip the expensive `_bridge_snapshot` +
`resolve_bridge_lifecycle`. `protected_paths=None` preserves the legacy full scan.
`terminal_verified_packets_scanned` still reports the total.

**Mechanism 2 - batch prospective-tree materialization.** `_materialize_entries`
streams every blob through ONE `git cat-file --batch` process instead of two
subprocess spawns per entry. Requests are interleaved one-at-a-time rather than
written up front, because writing all 19,090 object ids first deadlocks git
against a full stdout pipe. `_blob_ledger_entry` is retained as the reference
single-entry implementation the ledger-equivalence test compares against.

**Mechanism 3 - oversized-blob content exemption.** Blobs over `MAX_BLOB_BYTES`
are exempt from CONTENT COPY only: still streamed and hash-verified against the
index object id, recorded in a new `_BridgeSnapshot.exempted` map
(rel_path -> mode/oid/declared size), not written to disk, and excluded from
`MAX_TREE_BYTES` accounting. They are deliberately NOT placed in `ledger`, because
`_verify_snapshot_ledger` requires every ledger entry to exist on disk and
re-hashes its bytes. The exemption is size-triggered only, never path-targeted.

**Mechanism 4 - ledger-verification scope.** `_verify_snapshot_ledger` no longer
skips the entire `.gtkb-state/` namespace. It now discriminates on **ledger
membership** rather than a hardcoded scratch path list, because the audit creates
several scratch subtrees inside the tree at runtime (`compliance-audit/`,
`audit-candidate/`) and a hardcoded list silently drifts - an earlier attempt at
this fix with a single hardcoded prefix broke 5 tests, which is how the
multiple-scratch-subtree behavior was discovered.

## Root-Cause Findings (evidence)

```text
Mechanism 1  _load_verified_evidence over 472 committed packets : 460.824s -> 9.564s

Mechanism 2  materialization cost, real index entries (150-entry samples)
  A current path (2 spawns/entry)  : 159.4 ms/entry -> 50.7 min full index
  B spawn-only, no write/no hash   : 136.4 ms/entry -> 86% of cost is process spawn
  C `git cat-file --batch`         :   1.1 ms/entry -> ~18s full index (151x)

Mechanism 3  groundtruth.db indexed blob : 762,720,256 bytes (727.4 MB), same in HEAD
             MAX_BLOB_BYTES 67,108,864 (64 MB)  -> exceeded 11.4x
             MAX_TREE_BYTES 536,870,912 (512 MB) -> exceeded by this ONE file alone
             observed: GateError "raw blob exceeds 67108864-byte materialization limit"
             => the transaction branch failed closed on EVERY governed finalization
                at any speed. Probable root cause of the file-only VERIFIED class.

Mechanism 4  25 TRACKED .gtkb-state/* files are materialized and enter the ledger,
             but the blanket skip removed them from actual_paths
             observed: GateError "file set drifted; missing=[25 .gtkb-state/... paths]"
             _verify_snapshot_ledger runs at 5 production sites incl. _immutable_snapshot
```

## Verified End State

```text
index entries          : 19090
full tree build        : 17.21s
ledger (materialized)  : 19089
exempted (content skip): 1  -> groundtruth.db mode=100644 size=762720256 oid=53d1543391ce
enumeration complete   : 19090 == 19090 -> True
ledger verification    : OK (no file-set drift)

end-to-end: `check_protected_commit_authorization.py --staged`
  (2 protected paths staged, index reset afterwards)
  -> EXIT 0, 2.40s, "PASS protected-commit authorization (2 protected path(s) cleared)"
```

## Specification Links (carried forward from the approved proposals)

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

## Spec-to-Test Mapping

| Specification | Tests / evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (gate must complete as a pre-commit hook) | End-to-end `--staged` 2.40s EXIT 0 PASS; full real-index tree build 17.21s with ledger verification OK; `test_wi5659_prefilter_scales_past_pre_commit_budget` (450 irrelevant + 1 relevant packet; only the relevant one resolved). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (behavior-derived tests) | Mechanism 1: `..._prefilter_resolves_only_matching_packets`, `..._none_is_full_scan`, `..._preserves_authorization_outcome`, `..._integrated_real_chain_equivalence` (real committed VERIFIED chain). Mechanism 2: `..._batch_ledger_matches_per_entry_reference` (byte-identical files + ledger vs `_blob_ledger_entry`), `..._batch_uses_one_process_for_all_entries`, `..._batch_missing_object_fails_closed`, `..._batch_hash_mismatch_fails_closed`, `..._batch_malformed_terminator_fails_closed`, `..._batch_enforces_tree_limit`. Mechanism 3: `..._oversized_blob_is_exempted_not_fatal`, `..._exempted_blob_is_still_hash_verified`, `..._exempted_blob_excluded_from_tree_size_accounting`, `..._ledger_verification_passes_with_exempted_entry`. Mechanism 4: `..._tracked_gtkb_state_files_are_verified_not_skipped`, `..._audit_scratch_subtree_is_still_ignored`, `..._tampering_with_tracked_gtkb_state_file_is_detected`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH v4, project, WI-5659 v4, target paths, owner decisions 202667184/185/186/187 all cited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files are in-root platform paths. |

## Commands Executed (observed results)

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q
  -> 113 passed, 1 warning in 57.20s
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <both target files>
  -> All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <both target files>
  -> 2 files already formatted
```

## Deliberate Behavior Change Requiring Review

`test_raw_materialization_fails_closed_on_blob_resource_limit` asserted that an
oversized blob raises `GateError("materialization limit")` and aborts the
snapshot. `DELIB-202667186` deliberately supersedes that contract. The test was
**converted, not deleted**, to
`test_raw_materialization_exempts_oversized_blob_per_mechanism_3`, with the
supersession and its rationale recorded in the test body. Loyal Opposition should
review this specifically: it is the one place where a previously fail-closed
security assertion was intentionally relaxed. Fail-closed behavior is retained
for the tree budget and for hash mismatch on exempted blobs, both covered by
tests above.

## Acceptance Criteria Check

- [x] Full prospective tree builds on the real 19,090-entry index including `groundtruth.db`.
- [x] Every index entry represented: 19,089 ledger + 1 exempted == 19,090.
- [x] Exempted blob hash-verified; mismatch fails closed.
- [x] Tracked `.gtkb-state/*` files verified; tampering detected; audit scratch ignored.
- [x] Ledger equivalence for non-exempt blobs retained (byte-identical files).
- [x] 113 tests pass; ruff check and ruff format --check clean.
- [ ] A real governed VERIFIED finalizer transaction completes and produces a commit - this is what Loyal Opposition's own finalization of THIS report will demonstrate.

## Owner Decisions / Input

- `DELIB-202667187` - owner AUQ authorizing mechanism 4 (ledger-verification scope). Answer: "Authorize mechanism 4 and finish".
- `DELIB-202667186` - owner AUQ authorizing mechanism 3 (oversized-blob content exemption). Answer: "Exempt oversized blobs from content copy"; owner also directed "please implement it".
- `DELIB-202667185` - owner AUQ authorizing mechanism 2 (batch materialization).
- `DELIB-202667184` - owner AUQ authorizing mechanism 1 (verified-evidence pre-filter).
- `PAUTH-...-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` v4 - active, source+test, naming all four mechanisms.

## Prior Deliberations

- `bridge/...-010.md` - GO for mechanisms 1 and 2.
- `bridge/...-008.md` - NO-GO establishing that authority must exist BEFORE proposing a new mechanism; that discipline was followed for mechanisms 3 and 4 (authority created first), except for the LO GO itself, as disclosed above.
- `bridge/...-006.md` - NO-GO requiring end-to-end finalizer evidence rather than component timings; this report provides it.
- `bridge/gtkb-wi5658-protected-commit-checker-performance-002.md` - preceding checker-perf slice.

## Files Changed

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

Recommended commit type: `perf`

Rationale: the change is performance and availability restoration of the
commit-finalization gate; no new capability surface is added. `fix` would also be
defensible given that mechanisms 3 and 4 repair outright breakage rather than
slowness, and Loyal Opposition may prefer it; the diff adds no new feature.
