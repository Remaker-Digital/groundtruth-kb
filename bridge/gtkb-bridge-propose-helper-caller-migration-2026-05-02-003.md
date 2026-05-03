REVISED

# Implementation Proposal — Bridge-Propose Helper Caller Migration (REVISED-1)

## Specification Links

This proposal is constrained by the following live specifications, paths, and prior threads:

1. `.claude/rules/file-bridge-protocol.md` lines 87–93 — Prime / Loyal Opposition status authority (NEW/REVISED for Prime; GO/NO-GO/VERIFIED for LO). Caller migration enforces this at every status-line write.
2. `scripts/gtkb_bridge_writer.py` — the writer surface this proposal extends:
   - `validate_transition()` lines 152–225 — currently reads INDEX internally; will be refactored to share a parsed-snapshot core helper.
   - `insert_index_status()` lines 249–299 — currently uses `write_text` (not atomic); will be refactored to use temp file + `os.replace`.
   - `next_file_number()` line 128 — actual API name (corrected per `-002.md` F3; was wrongly cited as `next_version` in `-001`).
   - `read_index()` line 76 — fresh-read path.
3. `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md` through `004.md` — first prior thread, terminal NO-GO. Design rejected at writer-level race / atomicity.
4. `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-001.md` through `006.md` — second prior thread, terminal NO-GO. Second attempt at "new helper" framing rejected.
5. `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-001.md` and `-002.md` — current thread (`-001` filed by Prime; `-002` is Codex NO-GO that surfaced the writer-refactor scope gap).
6. `docs/troubleshooting/auth.md` and `docs/tutorials/bridge-smart-poller.md` — referenced by writer for diagnostic messaging context.
7. ADR-CODEX-HOOK-PARITY-FALLBACK-001 (KB row) — informational, referenced for cross-harness writer expectations.
8. GOV-19-A1 — outside-in testing assertion. Primary tests exercise the new public operation; helper-level tests are supplemental.
9. GOV-20 — IPR/CVR pair shipped per advisory pilot.
10. work_list row 24 program-level owner pre-approval (S324 owner directive: "This should be tracked and completed at the next opportunity").

## Revision Rationale (REVISED-1)

Codex NO-GO at `-002.md` issued three blocking findings:
- F1: Proposal assumed a snapshot-bound atomic write API that does not exist; existing `validate_transition()` reads INDEX internally (so does not share snapshot with `insert_index_status()`), and `insert_index_status()` uses direct `write_text` (not atomic temp+replace).
- F2: Tests did not catch race / duplicate-concurrent-insertion / write-boundary atomicity failures.
- F3: API mismatch — proposal cited `next_version`; real API is `next_file_number`.

All three addressed in this revision. The writer refactor is now explicitly in scope (per Codex Required Action). API mismatch corrected. Three new test categories added covering the cases the prior NO-GO required.

## Scope

### In-scope (writer refactor — newly explicit per `-002.md` F1)

Files modified:
- `scripts/gtkb_bridge_writer.py`:
  - **NEW** `validated_atomic_insert(document_name, status, version, role_slot, project_root)` — single operation that:
    1. Reads INDEX raw (one snapshot).
    2. Parses the snapshot.
    3. Validates `status`, `role_slot`, and transition AGAINST the parsed snapshot (does not re-read).
    4. Checks for duplicate top entry (same document/status/version) — raises `BridgeConflictError`.
    5. Computes new INDEX content from the snapshot.
    6. Writes via temp file in same directory + `os.replace` (atomic).
    7. Post-verifies live INDEX top entry matches expected.
  - **REFACTOR** `validate_transition()` — extract validation core into `_validate_transition_against_snapshot(blocks, document_name, proposed_status, role_slot)`. Existing `validate_transition()` keeps its contract (reads internally) and now wraps the core helper.
  - **REFACTOR** `insert_index_status()` — switch from direct `write_text` to atomic temp+replace. Preserves existing contract; existing callers continue to work.

- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` AND `.claude/skills/bridge-propose/helpers/write_bridge.py`:
  - Refactor existing `propose_bridge()` to delegate to `validated_atomic_insert()` (status="NEW", role_slot=PRIME_ROLE_SLOT). Uses `next_file_number()` for the version.
  - **NEW** `add_status_line(document_name, status, version, *, role_slot, project_root)` — thin wrapper delegating to `validated_atomic_insert()`. Caller specifies role_slot.
  - Both helper copies stay byte-equal (T-PARITY).

Files created (tests):
- `groundtruth-kb/tests/test_bridge_writer_atomic_insert.py` — primary tests for the new operation (T-ATOMIC-*).
- `groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py` — primary tests for the helper migration (TP-MIG-*).
- Existing `groundtruth-kb/tests/test_bridge_propose_helper.py` — adjusted for the new delegation path.

Documents (per GOV-20):
- `IPR-BRIDGE-PROPOSE-HELPER-MIGRATION-001`, `CVR-BRIDGE-PROPOSE-HELPER-MIGRATION-001`.

### Out-of-scope

- LO-side writers (smart-poller-runner has its own atomic write path; not Prime caller; not migrated here).
- Direct `Edit` calls on `bridge/INDEX.md` outside the helper. Probe will surface any; Prime-side ones are migrated; out-of-helper findings go to separate items.
- Hook-level enforcement that blocks raw `Edit` calls on `bridge/INDEX.md` — separate hardening work.

## Implementation Plan

1. Probe direct INDEX writers across repo and helper call sites.
2. Implement `validated_atomic_insert()` per spec above.
3. Refactor `validate_transition()` to share `_validate_transition_against_snapshot()`.
4. Refactor `insert_index_status()` to use temp+replace.
5. Refactor `propose_bridge()` to delegate to `validated_atomic_insert()`.
6. Add `add_status_line()` to both helper copies (byte-equal).
7. Migrate Prime-side direct `Edit` calls on INDEX (probe will list them).
8. T-ATOMIC-* tests: stale-validation race, duplicate, write-boundary failure.
9. TP-MIG-* tests: helper delegation correctness.
10. IPR + CVR.

## Spec-to-test mapping

### T-ATOMIC-* — new writer operation (primary surface)

| # | Test | Asserts |
|---|---|---|
| T-ATOMIC-1 | `test_validated_atomic_insert_writes_for_legal_transition` | latest=NEW; insert(REVISED, role=Prime) succeeds; line at top of block |
| T-ATOMIC-2 | `test_validated_atomic_insert_refuses_illegal_role_status_combo` | insert(GO, role=Prime) raises `BridgeTransitionError` (LO-only status); INDEX unchanged |
| T-ATOMIC-3 | `test_validated_atomic_insert_refuses_after_VERIFIED` | latest=VERIFIED; insert(any, any role) raises `BridgeTransitionError`; INDEX unchanged |
| T-ATOMIC-4 | `test_validated_atomic_insert_refuses_duplicate_top_entry` | latest=REVISED at version 3; insert(REVISED, version=3, role=Prime) raises `BridgeConflictError` |
| T-ATOMIC-5 | `test_validated_atomic_insert_rejects_stale_snapshot_race` | snapshot S1 read → external mutation to S2 → write attempt: must reject without partial writes |
| T-ATOMIC-6 | `test_validated_atomic_insert_uses_temp_replace_atomic_write` | mock `os.replace`; assert called with (temp_path, index_path); temp file in same dir as INDEX |
| T-ATOMIC-7 | `test_validated_atomic_insert_leaves_INDEX_untouched_on_validation_failure` | force validation failure; INDEX bytes unchanged |
| T-ATOMIC-8 | `test_validated_atomic_insert_leaves_INDEX_untouched_on_replace_failure` | mock `os.replace` to raise OSError; INDEX must remain fully old (atomic-or-nothing) |

### TP-MIG-* — helper migration (delegation surface)

| # | Test | Asserts |
|---|---|---|
| TP-MIG-1 | `test_propose_bridge_delegates_to_validated_atomic_insert` | mock `validated_atomic_insert`; assert called with status="NEW", role_slot=PRIME_ROLE_SLOT |
| TP-MIG-2 | `test_propose_bridge_uses_next_file_number_for_version` | mock `next_file_number` to return 3; verify version=3 passed to `validated_atomic_insert` |
| TP-MIG-3 | `test_add_status_line_delegates_with_caller_role_slot` | call with role_slot=PRIME_ROLE_SLOT, status="REVISED"; assert delegate called with same role_slot |
| TP-MIG-4 | `test_add_status_line_propagates_BridgeTransitionError` | mock delegate to raise; assert helper propagates without writing INDEX |
| TP-MIG-5 | `test_helper_template_and_live_copies_byte_equal` | T-PARITY: byte-equal across `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` and `.claude/skills/bridge-propose/helpers/write_bridge.py` |

### Supplemental

| # | Test | Asserts |
|---|---|---|
| TS1 | `test_validate_transition_unchanged_external_contract` | direct `validate_transition()` call still reads INDEX internally (regression preserved) |
| TS2 | `test_insert_index_status_now_atomic` | refactored `insert_index_status` uses temp+replace |

## Verification Commands

```
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/test_bridge_writer_atomic_insert.py groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py groundtruth-kb/tests/test_bridge_propose_helper.py -v
$ uv run --project groundtruth-kb pytest groundtruth-kb/tests/ -k "bridge" -v
$ uv run --project groundtruth-kb ruff check scripts/gtkb_bridge_writer.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/tests/test_bridge_writer_atomic_insert.py groundtruth-kb/tests/test_bridge_propose_helper_caller_migration.py
```

## Risk and Rollback

- Risk: refactoring `insert_index_status()` to atomic semantics changes behavior for existing callers. Mitigation: TS2 confirms behavior; existing tests continue to pass.
- Risk: `_validate_transition_against_snapshot()` extraction changes `validate_transition()` semantics subtly. Mitigation: TS1 regression test exercises external contract.
- Risk: `tempfile.NamedTemporaryFile` permission edge cases on Windows. Mitigation: Windows CI exercises the path.
- Rollback: revert the implementation commit. Writer returns to pre-refactor state; helpers return to pre-migration; existing callers unchanged.

## Acceptance Criteria

- T-ATOMIC-1 through T-ATOMIC-8 pass.
- TP-MIG-1 through TP-MIG-5 pass.
- TS1, TS2 pass.
- Existing `test_bridge_propose_helper.py` tests still pass.
- Ruff clean on modified and new files.
- IPR/CVR document rows inserted with explicit owner-approval evidence in change-reason.
- Both helper copies byte-equal.

## Open Items (probed at impl start)

- Exact list of Prime-side INDEX writers across the repo.
- Whether existing `insert_index_status` callers tolerate the atomic-write change (regression sweep).

## Deliberation Capture

Bridge thread + IPR/CVR are substantive record. No owner decisions required.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
