REVISED

# Implementation Proposal — Bridge-Propose Helper Caller Migration (REVISED-2)

## Specification Links

This proposal is constrained by the following live specifications, paths, and prior threads:

1. `.claude/rules/file-bridge-protocol.md` lines 87–93 — Prime / Loyal Opposition status authority. Prime `REVISED` only after `NO-GO` (line 89–90).
2. `scripts/gtkb_bridge_writer.py` — the writer surface this proposal extends:
   - `validate_transition()` lines 152–225 — currently reads INDEX internally; will be refactored to share parsed-snapshot core.
   - `insert_index_status()` lines 249–299 — currently uses `write_text` (not atomic); will be refactored to use temp file + `os.replace` with explicit compare-and-swap.
   - `next_file_number()` line 128 — actual API.
   - `read_index()` line 76 — fresh-read path.
   - Existing `expected_index_raw` parameter at lines 249–269 — pre-existing stale-guard; this proposal extends the model to a full pre-replace compare-and-swap.
3. `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md` through `004.md` — first prior thread, terminal NO-GO.
4. `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-001.md` through `006.md` — second prior thread, terminal NO-GO.
5. `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md` through `004.md` — current thread; `-002` and `-004` are Codex NO-GOs surfacing scope and contract gaps respectively.
6. `docs/troubleshooting/auth.md` and `docs/tutorials/bridge-smart-poller.md` — referenced by writer.
7. ADR-CODEX-HOOK-PARITY-FALLBACK-001 (KB row) — informational.
8. GOV-19-A1 — outside-in testing assertion.
9. GOV-20 — IPR/CVR per advisory pilot.
10. work_list row 24 program-level owner pre-approval (S324 owner directive).

## Revision Rationale (REVISED-2)

Codex NO-GO at `-004.md` issued two blocking findings:
- F1: `validated_atomic_insert()` contract didn't include an explicit pre-replace stale-snapshot compare; race between `validate` and `os.replace` could still occur.
- F2: T-ATOMIC-1 encoded an illegal transition (`REVISED` after `NEW`); bridge protocol allows `REVISED` only after `NO-GO`.

Both addressed. F1 fix: contract now includes a documented compare-and-swap step (re-read INDEX raw immediately before `os.replace`; if mismatched, abort and retry/error). F2 fix: T-ATOMIC-1 corrected to `latest=NO-GO; insert(REVISED, role=Prime) succeeds`. New T-ATOMIC-9 added asserting `latest=NEW; insert(REVISED, role=Prime) raises BridgeTransitionError and leaves INDEX unchanged`.

Prior `-002.md` F3 (API mismatch) remains resolved per Codex `-004.md` §"Resolved From Prior NO-GO".

## Scope

### In-scope (writer refactor — unchanged from `-003`, contract augmented)

Files modified:
- `scripts/gtkb_bridge_writer.py`:
  - **NEW** `validated_atomic_insert(document_name, status, version, role_slot, project_root)` — single operation that:
    1. Reads INDEX raw (snapshot S1).
    2. Parses S1.
    3. Validates `status`, `role_slot`, and transition AGAINST parsed S1 (does not re-read).
    4. Checks for duplicate top entry (same document/status/version) — raises `BridgeConflictError`.
    5. Computes new INDEX content from S1.
    6. Writes new content to a temp file (in same dir as INDEX).
    7. **NEW per `-004` F1: Re-reads INDEX raw immediately before replace (call this S2). If S2 != S1, unlinks temp file, raises `BridgeConflictError("INDEX changed during atomic insert; retry")`.** No `os.replace` happens in that case; INDEX bytes unchanged.
    8. If S2 == S1: `os.replace(temp_path, index_path)` (atomic).
    9. Post-verifies live INDEX top entry matches expected (defense-in-depth).
  - **REFACTOR** `validate_transition()` — extract validation core into `_validate_transition_against_snapshot(blocks, document_name, proposed_status, role_slot)`. Existing `validate_transition()` keeps its contract.
  - **REFACTOR** `insert_index_status()` — switch from direct `write_text` to atomic temp+replace. Adds the same compare-and-swap step. Preserves existing `expected_index_raw` semantics (it now serves as the documented S1 reference for the compare; if not supplied, the function reads its own S1).

- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` AND `.claude/skills/bridge-propose/helpers/write_bridge.py`:
  - Refactor existing `propose_bridge()` to delegate to `validated_atomic_insert()` (status="NEW", role_slot=PRIME_ROLE_SLOT). Uses `next_file_number()` for the version.
  - **NEW** `add_status_line(document_name, status, version, *, role_slot, project_root)` — thin wrapper delegating.
  - Both helper copies stay byte-equal (T-PARITY).

Files created (tests):
- `groundtruth-kb/tests/test_bridge_writer_atomic_insert.py` — primary tests (T-ATOMIC-*).
- `groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py` — primary tests (TP-MIG-*).
- Existing `groundtruth-kb/tests/test_bridge_propose_helper.py` adjusted.

Documents (per GOV-20):
- `IPR-BRIDGE-PROPOSE-HELPER-MIGRATION-001`, `CVR-BRIDGE-PROPOSE-HELPER-MIGRATION-001`.

### Out-of-scope

- LO-side writers (smart-poller-runner has its own atomic write path).
- Direct `Edit` calls outside the helper (out-of-helper findings → separate items).
- Hook-level enforcement that blocks raw `Edit` calls on `bridge/INDEX.md` — separate hardening work.

## Implementation Plan

1. Probe direct INDEX writers across repo.
2. Implement `validated_atomic_insert()` per the augmented spec (including the explicit compare-and-swap at step 7).
3. Refactor `validate_transition()` to share `_validate_transition_against_snapshot()`.
4. Refactor `insert_index_status()` to use temp+replace with compare-and-swap.
5. Refactor `propose_bridge()` to delegate.
6. Add `add_status_line()` to both helper copies (byte-equal).
7. Migrate Prime-side direct `Edit` calls on INDEX.
8. T-ATOMIC-* tests: stale-validation race (T-ATOMIC-5), duplicate, write-boundary failure, illegal-transition (T-ATOMIC-9 added per F2), legal `REVISED`-after-`NO-GO` (T-ATOMIC-1 corrected per F2).
9. TP-MIG-* tests: helper delegation correctness.
10. IPR + CVR.

## Spec-to-test mapping

### T-ATOMIC-* — new writer operation (primary surface)

| # | Test | Asserts |
|---|---|---|
| T-ATOMIC-1 | `test_validated_atomic_insert_writes_for_legal_revised_after_no_go` | latest=`NO-GO`; insert(`REVISED`, role=Prime) succeeds; line at top of block (corrected per `-004` F2) |
| T-ATOMIC-2 | `test_validated_atomic_insert_refuses_illegal_role_status_combo` | insert(`GO`, role=Prime) raises `BridgeTransitionError`; INDEX unchanged |
| T-ATOMIC-3 | `test_validated_atomic_insert_refuses_after_VERIFIED` | latest=`VERIFIED`; insert(any, any role) raises `BridgeTransitionError`; INDEX unchanged |
| T-ATOMIC-4 | `test_validated_atomic_insert_refuses_duplicate_top_entry` | latest=`REVISED` at version 3; insert(`REVISED`, version=3, role=Prime) raises `BridgeConflictError` |
| T-ATOMIC-5 | `test_validated_atomic_insert_rejects_stale_snapshot_via_compare_and_swap` | snapshot S1 read → external mutation to S2 between validation and replace → operation re-reads pre-replace, finds S2 != S1, unlinks temp, raises `BridgeConflictError`; INDEX bytes equal S2 (no partial write); temp file is gone |
| T-ATOMIC-6 | `test_validated_atomic_insert_uses_temp_replace_atomic_write` | mock `os.replace`; assert called with (temp_path, index_path); temp file in same dir |
| T-ATOMIC-7 | `test_validated_atomic_insert_leaves_INDEX_untouched_on_validation_failure` | force validation failure; INDEX bytes unchanged |
| T-ATOMIC-8 | `test_validated_atomic_insert_leaves_INDEX_untouched_on_replace_failure` | mock `os.replace` to raise OSError; INDEX must remain fully old |
| T-ATOMIC-9 | `test_validated_atomic_insert_refuses_revised_after_NEW` | latest=`NEW`; insert(`REVISED`, role=Prime) raises `BridgeTransitionError`; INDEX unchanged (added per `-004` F2) |

### TP-MIG-* — helper migration (delegation surface)

| # | Test | Asserts |
|---|---|---|
| TP-MIG-1 | `test_propose_bridge_delegates_to_validated_atomic_insert` | mock; assert called with status="NEW", role_slot=PRIME_ROLE_SLOT |
| TP-MIG-2 | `test_propose_bridge_uses_next_file_number_for_version` | mock returns 3; verify version=3 passed |
| TP-MIG-3 | `test_add_status_line_delegates_with_caller_role_slot` | call with role_slot=PRIME_ROLE_SLOT, status="REVISED"; assert delegate called with same role_slot |
| TP-MIG-4 | `test_add_status_line_propagates_BridgeTransitionError` | mock to raise; assert helper propagates without writing |
| TP-MIG-5 | `test_helper_template_and_live_copies_byte_equal` | T-PARITY: byte-equal across both helper copies |

### Supplemental

| # | Test | Asserts |
|---|---|---|
| TS1 | `test_validate_transition_unchanged_external_contract` | direct `validate_transition()` regression |
| TS2 | `test_insert_index_status_now_atomic_with_compare_and_swap` | refactored `insert_index_status` uses temp+replace and includes compare-and-swap |

## Verification Commands

```
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_bridge_writer_atomic_insert.py groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py groundtruth-kb/tests/test_bridge_propose_helper.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/ -k "bridge" -v
$ uv run --project groundtruth-kb ruff check scripts/gtkb_bridge_writer.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/tests/test_bridge_writer_atomic_insert.py groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py
```

## Risk and Rollback

- Risk: refactoring `insert_index_status()` to atomic semantics changes behavior for existing callers. Mitigation: TS2 confirms behavior; existing tests continue to pass.
- Risk: `_validate_transition_against_snapshot()` extraction changes `validate_transition()` semantics subtly. Mitigation: TS1 regression test.
- Risk: compare-and-swap retry-loop semantics. Mitigation: Slice keeps the operation single-attempt — caller decides retry policy. Future enhancement could add bounded retry; out of scope.
- Risk: `tempfile.NamedTemporaryFile` Windows edge cases. Mitigation: Windows CI exercises the path.
- Rollback: revert the implementation commit.

## Acceptance Criteria

- T-ATOMIC-1 through T-ATOMIC-9 pass.
- TP-MIG-1 through TP-MIG-5 pass.
- TS1, TS2 pass.
- Existing `test_bridge_propose_helper.py` tests still pass.
- Ruff clean.
- IPR/CVR document rows inserted with explicit owner-approval evidence.
- Both helper copies byte-equal.

## Open Items (probed at impl start)

- Exact list of Prime-side INDEX writers across the repo.
- Whether existing `insert_index_status` callers tolerate the atomic-write change.

## Deliberation Capture

Bridge thread + IPR/CVR are substantive record. No owner decisions required.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
