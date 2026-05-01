REVISED

# Bridge Proposal — GTKB ADR-Evaluation Enforcement S0 (Audit Script; REVISED-1)

**Status:** REVISED (version 003)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30`
**Reviewed prior version:** `bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-04-30-002.md` (Codex NO-GO with F1, F2 blocking findings).
**Parent scoping bridge:** `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-006.md` (Codex GO; clean)

**REVISED-1 summary:** Closes F1 (tag-categorization fixture/heuristic mismatch) by splitting the fixture into two unambiguous test cases each exercising one categorization path. Closes F2 (read-only DB safety) by introducing a factored `_connect_read_only()` helper that uses SQLite's `mode=ro` URI, plus a test that an INSERT through that connection raises `sqlite3.OperationalError`.

**Owner pre-approval:** Yes for the program-level scope per the parent scoping bridge's S324 AskUserQuestion authorization. This implementation bridge requires its own Codex GO before implementation per `.claude/rules/codex-review-gate.md`.

---

## Closure of NO-GO Findings (-002)

### F1 Closure — Tag-Categorization Fixture and Heuristic Aligned

**Original finding:** Heuristic states theme tags appear in `>= 3` records OR contain explicit markers (`design-constraint`, `mechanical-enforcement`, `governance`); topic tags otherwise. The proposed test fixture used tags `["theme-tag", "topic-tag", "theme-tag"]` where `theme-tag` appears 2 times (not 3+) and is not an explicit marker — so the documented heuristic would classify it as topic, not theme.

**Closure:** Replace the single ambiguous fixture with two unambiguous test cases, each exercising one categorization path:

**Test 4a — theme-via-explicit-marker:**
- Fixture: 1 ADR record with `tags=["governance", "lone-topic"]`
- Expected histogram: `governance` categorized as `theme` (via explicit marker), `lone-topic` categorized as `topic` (no marker, count=1)
- Asserts the explicit-marker path of the heuristic

**Test 4b — theme-via-count-threshold:**
- Fixture: 3 ADR records, each with `tags=["common-theme"]`
- Expected histogram: `common-theme` categorized as `theme` (via count >= 3)
- Asserts the count-based path of the heuristic

This separation removes the prior ambiguity (the original `"theme-tag"` token didn't clearly belong to either categorization path) and proves both paths independently. The script's documented heuristic is unchanged.

### F2 Closure — Read-Only DB Connection Proven by Write-Rejection

**Original finding:** The proposal's safety claim (script performs read-only access to `groundtruth.db`) was stronger than the planned test (only mtime-unchanged). A regular SQLite connection running only SELECT queries can leave mtime unchanged while still permitting writes. The mtime check therefore does not enforce the read-only invariant.

**Closure:** Two changes:

1. **Connection helper with explicit `mode=ro` URI** (new in script):
```python
def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    """Open a read-only SQLite connection. SQLite enforces mode=ro;
    any write attempt raises sqlite3.OperationalError ('attempt to
    write a readonly database')."""
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)
```

The audit script uses this helper exclusively. No other connection-opening code path exists.

2. **Test that proves write-rejection** (replaces the prior mtime-only test):
```python
def test_read_only_connection_rejects_writes(tmp_path):
    """Open the audit-script's _connect_read_only against a fresh fixture DB.
    Attempt INSERT; assert sqlite3.OperationalError is raised. This proves
    the connection is genuinely read-only at SQLite enforcement level, not
    merely unmonitored."""
    fixture_db = tmp_path / "test.db"
    with sqlite3.connect(fixture_db) as setup:
        setup.execute("CREATE TABLE specifications (id TEXT, type TEXT)")
    conn = audit_module._connect_read_only(fixture_db)
    try:
        with pytest.raises(sqlite3.OperationalError) as exc_info:
            conn.execute(
                "INSERT INTO specifications (id, type) VALUES (?, ?)",
                ("ADR-TEST", "architecture_decision"),
            )
        # Confirm the error is the read-only enforcement, not some other failure.
        message = str(exc_info.value).lower()
        assert "readonly" in message or "read-only" in message
    finally:
        conn.close()
```

The mtime-unchanged check remains as supplementary evidence (cheap; catches accidental write attempts that somehow succeeded), but it is no longer the primary read-only enforcement proof.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Parent program authorization:**
- `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-005.md` (REVISED-2 of parent) — defines S0 deliverable
- `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-006.md` (Codex GO on parent) — confirms S0 has no upstream dependencies

**Governance specs / records:**
- `.claude/rules/codex-review-gate.md` — protocol authority
- `.claude/rules/file-bridge-protocol.md` — bridge structure
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage gate
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED gate requires spec-derived test mapping (the F2 closure test directly satisfies this for the read-only invariant)
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule

**Existing pattern references:**
- `groundtruth-kb/scripts/audit_types.py` — sibling audit-pattern script
- `groundtruth-kb/scripts/audit_docstrings.py` — sibling audit-pattern script

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

---

## Proposed Changes

### Change 1 — `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` (new)

Standalone Python script that reads `groundtruth.db` (canonical KB) read-only and emits a structured audit report on metadata population state of all ADR and DCL specifications.

**Connection: read-only via factored helper (per F2 closure):**
```python
def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)
```

**Behavior** (unchanged from `-001` except for the connection helper):
- Connects via `_connect_read_only()` exclusively.
- Queries `specifications` table for the latest version per `id` where `type IN ('architecture_decision', 'design_constraint')`.
- For each row, computes per-field population (tags, source_paths, assertions: each populated if non-empty JSON list with at least 1 element).
- Computes per-type aggregates.
- Lists records missing `source_paths` (the principal backfill target).
- Builds tags histogram with categorization per the documented heuristic:
  - Theme via count: tag appears in >= 3 records.
  - Theme via explicit marker: tag is one of `design-constraint`, `mechanical-enforcement`, `governance`.
  - Topic: otherwise.
- Emits the recommendation for the S2 `concern_tags` normalization decision.

**CLI surface (unchanged):**
```
usage: audit_adr_dcl_metadata.py [-h] [--db PATH] [--format {json,markdown}]
                                  [--output PATH] [--frozen-timestamp ISO]
```

**Output schema (unchanged from -001):** JSON shape per the original proposal §"Output schema" block.

**Determinism:** records sorted by `id` ascending; tags histogram sorted by `(category, -count, tag)`; categorization deterministic.

**Risk:** Low. Pure read of `groundtruth.db` via `mode=ro` URI; SQLite enforces read-only at connection level.

### Change 2 — `tests/scripts/test_audit_adr_dcl_metadata.py` (new)

Unit tests covering 10 cases (was 9 in `-001`; the prior single tag-categorization test 4 is split into 4a and 4b per F1 closure):

1. **Idempotency:** Running script twice with same `--frozen-timestamp` against fixed fixture DB produces byte-identical output.
2. **Population computation:** With fixture, asserts `totals` counts match expected.
3. **Missing-source_paths list:** With fixture containing 2 records lacking source_paths, asserts list contains exactly those 2 IDs in sorted order.
4. **(was Test 4) Tags histogram + categorization** — split into:
   - **4a. Theme-via-explicit-marker:** Fixture with `tags=["governance", "lone-topic"]`; asserts `governance` categorized as `theme` and `lone-topic` as `topic`.
   - **4b. Theme-via-count-threshold:** Fixture with 3 records each having `tags=["common-theme"]`; asserts `common-theme` categorized as `theme` (count >= 3).
5. **Format snapshot — JSON:** Snapshot test of JSON output for fixed fixture state.
6. **Format snapshot — markdown:** Snapshot test of markdown rendering for same fixture.
7. **(was Test 7) Read-only connection rejects writes** (replaces mtime-only check per F2 closure): asserts INSERT through `_connect_read_only()` raises `sqlite3.OperationalError` with "readonly" in the message.
8. **(supplementary) DB mtime unchanged after read-only run:** retained as cheap secondary evidence.
9. **CLI: `--output` flag:** Asserts file is written when `--output` is provided.
10. **CLI: missing DB:** Asserts graceful error when `--db` path doesn't exist.

**Test infrastructure:** uses `tmp_path` pytest fixture for isolated DB creation. Test DB seeded via `sqlite3` module directly (no `groundtruth_kb` API dependency for test isolation).

**Risk:** Low. Tests-only file in `tests/scripts/`.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping (revised):**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| Parent S0 deliverable: "produces structured report on tags/source_paths/assertions population" | Tests 2, 3 (population computation + missing-list correctness) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py -k "population or missing" -q` |
| Parent S0 deliverable: "identifies records needing backfill" | Test 3 | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_missing_source_paths_list_correct -q` |
| Parent S0 deliverable: "recommends concern_tags normalization decision" | Tests 4a + 4b (theme-via-marker + theme-via-count both proven; F1 closure) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py -k "categorization" -q` |
| Idempotency check (parent S0 test surface) | Test 1 | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_idempotency -q` |
| Report format snapshot (parent S0 test surface) | Tests 5, 6 (JSON + markdown) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py -k "snapshot" -q` |
| **`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — read-only invariant proof** | **Test 7 (write-rejection through `_connect_read_only`); F2 closure** | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_read_only_connection_rejects_writes -q` |
| Read-only behavior (supplementary) | Test 8 (mtime unchanged) | `pytest tests/scripts/test_audit_adr_dcl_metadata.py::test_db_mtime_unchanged_after_read -q` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | bridge-compliance-gate hook check on this proposal Write | hook check (already passed) |
| Project root boundary | All edited paths inside `E:\GT-KB` | manual verification, see §Project Root Boundary Compliance |
| Code quality (ruff) | ruff clean on new files | `python -m ruff check groundtruth-kb/scripts/audit_adr_dcl_metadata.py tests/scripts/test_audit_adr_dcl_metadata.py` |

**Execution commands (planned for post-impl report):**
```bash
python -m ruff check groundtruth-kb/scripts/audit_adr_dcl_metadata.py tests/scripts/test_audit_adr_dcl_metadata.py
pytest tests/scripts/test_audit_adr_dcl_metadata.py -q
python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --format markdown
python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --format json --output /tmp/audit-sample.json
```

The release-gate command is NOT part of S0's verification surface (release-gate has known infrastructure issues per the parent bridge's S6 prerequisite). Per-test verification via `pytest` plus the explicit read-only-enforcement test is sufficient for this slice.

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md` Mandatory Project Root Boundary Gate:

- All edited files inside `E:\GT-KB`:
  - `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` (new)
  - `tests/scripts/test_audit_adr_dcl_metadata.py` (new)
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- All read targets inside `E:\GT-KB` (`groundtruth.db`, read-only).
- No external paths referenced.

---

## Pre-GO Drift Disposition

Clean fresh implementation. No source-code edits in worktree for this slice. All implementation will be authored after Codex GO.

---

## Implementation Sequence (planned for after Codex GO)

1. Author `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` per the CLI + output schema, using `_connect_read_only()` helper exclusively.
2. Author `tests/scripts/test_audit_adr_dcl_metadata.py` with the 10 test cases listed in Change 2 (note: 4a + 4b split per F1 closure; test 7 write-rejection per F2 closure).
3. Run `python -m ruff check` on both files — expect clean.
4. Run `pytest tests/scripts/test_audit_adr_dcl_metadata.py` — expect 10 passed.
5. Generate sample report against the live `groundtruth.db` for post-impl evidence: `python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --format markdown`.
6. Stage `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` + `tests/scripts/test_audit_adr_dcl_metadata.py` (no other files).
7. Commit with scoped message referencing this bridge thread.
8. File post-impl report; include sample report from step 5 as evidence.

---

## Rollback Notes

If post-impl reveals an unexpected issue:
- Revert the single commit via `git revert <sha>` — covers 2 files.
- Bridge thread is append-only audit history.

Risk surface is small (read-only script; tests-only fixture). Clean revert restores prior state.

---

## Decision Needed From Owner

This REVISED-1 proposal does not require an owner decision. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
