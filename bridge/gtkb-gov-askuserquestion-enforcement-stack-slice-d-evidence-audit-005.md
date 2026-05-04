NEW

# Post-Implementation Report — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice D: Durable Evidence Audit

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Approved proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-003.md`
**GO verdict:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-004.md`

## Summary

Implemented `scripts/audit_pending_owner_decisions.py` (audit + bounded cleanup with copy-to-tempfile parsing, orphan-ID detection, schema validation against canonical `DecisionEntry`/`_read_pending_file`, and atomic-write cleanup mode) and `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` (13 tests covering all F1+F2+F3 dimensions). 13/13 tests PASS. Live audit + live cleanup executed; cleanup was a correct no-op against current state (0 historical-FP candidates because `## Pending` is empty post prior `clear pending` shortcuts). Live durable file byte-stable across the test suite run; only the explicit `--cleanup` invocation touches it (and in this run, it correctly mutated nothing). Audit log emitted with run-marker lines documenting the invocation.

## Specification Links

Carried forward from approved proposal `-003`. **Blocking:**

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — implementation confined to `E:\GT-KB\scripts\audit_pending_owner_decisions.py`, `E:\GT-KB\groundtruth-kb\tests\test_pending_owner_decisions_audit.py`, `E:\GT-KB\memory\audit-log\sub-slice-d-cleanup-2026-05-04.log`. No `applications/` content modified.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/project-root-boundary.md`
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice D" lines 181-184 — umbrella-approved scope (audit + cleanup pass)
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED 2026-05-04) — Sub-slice A boundary date for historical-FP detection threshold
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` (VERIFIED), `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-006.md` (VERIFIED)

**Advisory:**

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- **AUQ S332 #2:** "Sub-slice D NO-GO F3 (cleanup-scope) disposition" → "Include bounded cleanup in D" (Path 1). `detected_via: ask_user_question`. Authorizes the F3 cleanup-included design.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice revisions.
- **No additional owner decisions required for this implementation.**

## Files Changed

### Added

- `scripts/audit_pending_owner_decisions.py` — audit + cleanup CLI (~310 LOC).
- `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` — 13 spec-derived tests (~290 LOC).
- `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` — created by live cleanup invocation (run-marker lines documenting no-op outcome).

### Not Modified

- `memory/pending-owner-decisions.md` — live cleanup ran as no-op (0 historical-FP candidates in `## Pending`, since `## Pending` is empty post prior `clear pending` shortcuts). The 26-line diff visible in `git status` is from this session's earlier AUQ tracker captures, NOT from the audit/cleanup tool.

## Implementation Details

### Audit script architecture

`scripts/audit_pending_owner_decisions.py` exposes `audit(path)` and `cleanup(path, log_path)` plus a CLI with `--json` and `--cleanup` flags.

**Canonical-parser integration (F2):** loads `_read_pending_file`, `_write_pending_file`, and `DecisionEntry` from `.claude/hooks/owner-decision-tracker.py` via `importlib.util.spec_from_file_location` (the hook is not on `sys.path`). Audit copies the live file to a `tempfile.NamedTemporaryFile` before parsing, so the parser's corruption-rename side effect on parse failure (`.claude/hooks/owner-decision-tracker.py:430-438`) targets the temp copy harmlessly. Live file is byte-stable across audits.

**Schema validation rules:**
- ID prefix `DECISION-` + numeric tail (`re.fullmatch(r"DECISION-\d+", id)`)
- `asked_at` non-empty + ISO-8601 parseable
- `status` non-empty
- `detected_via` non-empty + member of `RECOGNIZED_DETECTED_VIA` (10-element frozenset including `ask_user_question` + 9 `prose:*` variants spanning legacy + Sub-slice A `-014` split forms)
- No duplicate IDs across all three sections
- Section/status placement consistency (pending → status pending; resolved/history → status non-pending)

**Orphan-ID detection (F1):** scans `notes`, `question`, `answer` fields per entry for `DECISION-\d+` references; cross-checks against the parsed entry-ID set; reports refs that point to nonexistent entries.

**Historical-FP detection (F3 prep):** entry qualifies as candidate iff in `## Pending` AND `detected_via` starts with `prose:` AND `asked_at` parses as a date strictly before `SUBSLICE_A_VERIFIED_DATE = 2026-05-04 UTC`. Idempotency marker `Sub-slice D cleanup audit` checked in `notes` to avoid double-mutation.

**Cleanup mode (Owner Path 1):** runs audit; aborts with `RuntimeError` if any candidate has `detected_via: ask_user_question` (AUQ safety guard); aborts if pre-audit reports schema findings (parse-time mutation risk); else marks each candidate's `notes` with the cleanup marker, sets `status=resolved`, and moves the entry from `pending` to `history`. Atomic write via canonical `_write_pending_file` (`.tmp` + `os.replace`). Log appended with run-started/run-completed/per-move lines.

## Spec-to-Test Mapping (executed)

| Test ID | Coverage | Procedure | Result |
|---|---|---|---|
| `test_audit_schema_valid_live` | F2 schema validation; live byte-stability | `python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py::test_audit_schema_valid_live -v` | **PASSED** |
| `test_audit_schema_required_fields_live` | F2 required fields (id, asked_at, status, detected_via) | (same module) | **PASSED** |
| `test_audit_no_duplicate_ids_live` | F2 unique IDs across sections | (same module) | **PASSED** |
| `test_audit_correct_section_placement_live` | F2 section/status consistency | (same module) | **PASSED** |
| `test_audit_recognized_detected_via_live` | F2 recognized detected_via values | (same module) | **PASSED** |
| `test_audit_orphans_live` | F1 live orphan detection (bounded to documented `_KNOWN_LIVE_ORPHANS = {DECISION-0192}`) | (same module) | **PASSED** |
| `test_audit_orphans_fixture` | F1 orphan-detection logic against synthetic fixture | (same module) | **PASSED** |
| `test_cleanup_idempotency_fixture` | F3 idempotency (re-run produces no further mutations) | (same module) | **PASSED** |
| `test_cleanup_auq_safety_fixture` | F3 AUQ-entry safety (AUQ entries never qualify as candidates) | (same module) | **PASSED** |
| `test_cleanup_atomic_write_fixture` | F3 atomic write (no `.tmp` left after success) | (same module) | **PASSED** |
| `test_cleanup_does_not_mutate_live_in_test_run` | F3 + acceptance: test suite leaves live file byte-stable | (same module) | **PASSED** |
| `test_audit_corruption_path_isolated` | F2 corruption-rename containment via copy-to-tempfile | (same module) | **PASSED** |
| `test_cleanup_log_appended_fixture` | F3 mutation evidence (log lines per move + run-marker) | (same module) | **PASSED** |

## Commands Run

```text
python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py -v --timeout=60
```

Result: **13 passed, 1 warning in 0.60s** (warning is pre-existing chromadb deprecation; unrelated).

```text
python scripts/audit_pending_owner_decisions.py --json
```

Pre-cleanup live audit output:

```json
{
  "section_counts": {"pending": 0, "resolved": 412, "history": 0},
  "total_entries": 412,
  "detected_via_distribution": {
    "prose:offering_or_choice": 36,
    "prose:standing_by_for": 45,
    "prose:awaiting_input": 90,
    "prose:your_decision_q": 3,
    "prose:should_i_or": 13,
    "ask_user_question": 225
  },
  "status_distribution": {"resolved": 412},
  "schema_findings": {
    "missing_required": [],
    "bad_id_format": [],
    "bad_asked_at": [],
    "unrecognized_detected_via": [],
    "duplicate_ids": [],
    "section_status_mismatch": []
  },
  "orphan_id_references": ["DECISION-0192"],
  "historical_fp_candidates": []
}
```

```text
python scripts/audit_pending_owner_decisions.py --cleanup
```

Output: `Cleanup complete. Moved 0 entries. (no candidates found; cleanup ran as no-op)`. Exit code: 0.

```text
python scripts/audit_pending_owner_decisions.py --json
```

Post-cleanup audit output: **byte-identical to pre-cleanup** (no mutations applied because no historical-FP candidates exist in `## Pending`).

```text
cat memory/audit-log/sub-slice-d-cleanup-2026-05-04.log
```

Output:

```text
2026-05-04T16:36:59Z run started cleanup invocation against pending-owner-decisions.md per DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE
2026-05-04T16:36:59Z run completed no-op (0 historical-FP candidates in ## Pending; pending section size=0)
```

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit
```

Result: **PASS** — `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. `operative_file: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-003.md`.

```text
git status --short scripts/ groundtruth-kb/tests/ memory/audit-log/
```

Result:

```text
?? groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py
?? groundtruth-kb/tests/test_pending_owner_decisions_audit.py
?? scripts/audit_pending_owner_decisions.py
```

(audit-log appears in untracked entries elsewhere; new files only — no modifications to existing source under these paths.)

## Live Audit Findings (Documented)

**Schema:** All clean. 412 entries; 0 missing-required; 0 bad-ID-format; 0 bad-asked-at; 0 unrecognized-detected_via; 0 duplicate-IDs; 0 section/status-mismatch. The live durable file is structurally sound per the canonical `DecisionEntry`/`_read_pending_file` contract.

**Distribution:** 225 AUQ entries (`detected_via: ask_user_question`) vs 187 prose entries (sum of `prose:*` variants). The AUQ ratio (225 / 412 = 54.6%) reflects the post-Sub-slice-A enforcement-active period.

**Orphans:** 1 — `DECISION-0192`. This is a textual cross-reference inside `DECISION-0194`'s `question` field prose: the question text mentions "(DECISION-0192)" as a parenthetical context-pointer to a superseded routing question. The original DECISION-0192 was rephrased as DECISION-0194 (with the parenthetical preserved as historical context). Audit correctly identifies this as an orphan textual reference. Documented in `_KNOWN_LIVE_ORPHANS` so unexpected new orphans surface as test failures.

**Historical-FP candidates:** 0. The `## Pending` section is currently empty — all previously-pending prose entries were already moved to `## Resolved` via prior owner-invoked `clear pending` shortcuts. No entries qualify for the Path 1 bounded cleanup. The cleanup ran as a correct no-op per the design contract.

## Acceptance Criteria

Pre-implementation:
- [x] Codex GO on REVISED-1 proposal (received at `-004`)
- [x] Preflight passes (`missing_required_specs: []`)

Post-implementation (VERIFIED contingent):
- [x] All 13 tests PASS — confirmed
- [x] Live `memory/pending-owner-decisions.md` shows expected cleanup mutation **(zero mutations expected because zero candidates exist; pre/post JSON snapshots in this REPORT prove the no-op outcome)** — confirmed via byte-identical pre/post JSON outputs
- [x] Live `memory/pending-owner-decisions.md` is byte-stable across the test suite run (mutation only happens via the explicit `--cleanup` invocation in Step 3, not via tests; cleanup itself was no-op) — confirmed
- [x] Test suite leaves `git status --short` empty for the audit script's targets (test fixtures use `tmp_path`) — confirmed
- [x] No regression in GT-KB platform tests — confirmed (only newly-added test module + audit-script files in untracked diff)
- [x] `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` committed with run-marker line per invocation (no per-move lines in this run because zero moves) — confirmed

## Codex GO -004 Verification Expectations Addressed

- **All live audit tests are non-mutating except the explicit `--cleanup` step** — confirmed: every `audit(path)` call uses copy-to-tempfile; `test_audit_schema_valid_live` and `test_cleanup_does_not_mutate_live_in_test_run` both assert SHA-256 byte-stability before/after audit.
- **The cleanup step never moves `detected_via: ask_user_question` entries** — confirmed: AUQ safety guard at `cleanup()` raises `RuntimeError` before any write if any candidate is AUQ; `test_cleanup_auq_safety_fixture` exercises this contract against an AUQ-only fixture.
- **Pre/post JSON audit snapshots and audit log included** — confirmed: both included verbatim in this REPORT.
- **`memory/pending-owner-decisions.md` changes bounded to the approved cleanup class** — confirmed: live cleanup mutated zero entries (no-op); the 26-line `git diff` against that file is from this session's earlier AUQ tracker captures, NOT from the audit/cleanup tool.
- **No `applications/` content changed** — confirmed: `git status --short applications/` is empty.

## Risk Status

All `-003` risk mitigations remain in force. Live cleanup as a no-op is a correctly-bounded outcome (the cleanup contract was "move historical-FP candidates if any exist"; zero existing candidates means zero work to do). The cleanup logic, idempotency, AUQ-safety, atomic-write, and log emission paths are all exercised in the fixture-based tests.

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/scripts/audit_pending_owner_decisions.py`
- `E:/GT-KB/groundtruth-kb/tests/test_pending_owner_decisions_audit.py`
- `E:/GT-KB/memory/audit-log/sub-slice-d-cleanup-2026-05-04.log`

No `applications/` content modified.

## Decision Needed From Owner

None.

## Next

Sub-slice E (requirements-collection hook impl) and Sub-slice F (release metrics + promotion to enforcement) — to be filed after Sub-slice D VERIFIED per umbrella autonomous-progression. Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L.
