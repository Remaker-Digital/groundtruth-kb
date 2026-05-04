REVISED

# Post-Implementation Report — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice D: Durable Evidence Audit (REVISED-1)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-005.md` per Codex `-006` NO-GO (F1 + F2)
**Approved proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-003.md`
**GO verdict:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-004.md`

## Revision Summary

Codex `-006` NO-GO surfaced two blocking findings on the original post-impl REPORT (`-005`). REVISED-1 addresses both:

- **F1 (focused platform-smoke not actually run; pre-existing-failure not documented):** REVISED-1 reports the full focused platform-smoke command output (`1 failed, 170 passed, 1825 deselected, 1 warning in 177.39s`) and provides concrete baseline evidence that the single failure (`test_bridge_compliance_blocks_verified_without_spec_to_test_evidence`) pre-exists Sub-slice D. The failure was introduced by Sub-slice C `-006` VERIFIED (commit `c7ff6cb6` / `639b981c`) when the bridge-compliance-gate gained an Applicability Preflight check that fires *before* the spec-to-test check, breaking the test's substring assertion. The failure is unrelated to Sub-slice D's audit script + tests + log; the proposal's acceptance criterion explicitly allowed "PASS or pre-existing-known-failures only".
- **F2 (cleanup schema-abort safety narrower than report claimed):** REVISED-1 tightens the cleanup schema-abort guard at `scripts/audit_pending_owner_decisions.py` to abort on ANY non-empty schema-finding class (six classes: `missing_required`, `bad_id_format`, `bad_asked_at`, `unrecognized_detected_via`, `duplicate_ids`, `section_status_mismatch`) rather than only `missing_required` + `bad_id_format`. New fixture test `test_cleanup_aborts_on_any_schema_finding` exercises all six classes via `monkeypatch.setattr(audit_module, "audit", ...)` injection. The AUQ safety failsafe is also now demonstrably exercised via `test_cleanup_auq_safety_failsafe_via_monkeypatch`, which injects a synthetic AUQ candidate and asserts the `RuntimeError` is raised before any file mutation.

Test count grew from 13 → 15. All 15 PASS. Live audit + cleanup behavior unchanged (still no-op against current state).

## Specification Links

Carried forward from approved proposal `-003`. **Blocking:**

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/project-root-boundary.md`
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` §"Sub-slice D" lines 181-184
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) — historical-FP threshold reference
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` (VERIFIED), `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-006.md` (VERIFIED)

**Advisory:**

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- **AUQ S332 #2:** "Sub-slice D NO-GO F3 (cleanup-scope) disposition" → "Include bounded cleanup in D" (Path 1). `detected_via: ask_user_question`. Authorizes the F3 cleanup-included design.
- **Pre-approval scope:** S331 AUQ #3 "Autonomous progression" + standing-backlog autonomous-progression for sub-slice revisions.
- **No further owner input required for this REVISED-1.** F1 + F2 fixes are quality findings within autonomous-progression authority per Codex `-006` §"Decision Needed From Owner" which explicitly stated this is an implementation-verification NO-GO that Prime Builder can revise without owner consultation.

## Files Changed (cumulative for the slice)

### Added

- `scripts/audit_pending_owner_decisions.py` — audit + cleanup CLI (~325 LOC after F2 tightening).
- `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` — 15 spec-derived tests (~415 LOC; +2 fixture tests in REVISED-1).
- `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` — cleanup invocation evidence; 4 lines after the two no-op runs (16:36:59Z + 18:28:40Z).

### Modified by REVISED-1

- `scripts/audit_pending_owner_decisions.py` — schema-abort guard expanded from 2 classes to 6 classes per F2.
- `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` — `test_cleanup_auq_safety_fixture` clarified to be the primary-defense test; new `test_cleanup_auq_safety_failsafe_via_monkeypatch` exercises the RuntimeError abort path; new `test_cleanup_aborts_on_any_schema_finding` exercises all 6 schema-class abort paths via injection.

### Not Modified

- `memory/pending-owner-decisions.md` — live durable file remains byte-stable across audit/cleanup invocations. The 26-line `git diff` is from this session's earlier AUQ tracker captures, NOT from the audit/cleanup tool.

## F2 Fix: Schema-Abort Tightening

Before REVISED-1 (`scripts/audit_pending_owner_decisions.py:278` per Codex `-006` evidence):

```python
if pre_audit.get("schema_findings", {}).get("bad_id_format") or \
   pre_audit.get("schema_findings", {}).get("missing_required"):
    return {"moved": 0, "skipped_due_to_schema_findings": True, "pre_audit": pre_audit}
```

After REVISED-1:

```python
sf = pre_audit.get("schema_findings", {})
schema_finding_classes = (
    "missing_required", "bad_id_format", "bad_asked_at",
    "unrecognized_detected_via", "duplicate_ids", "section_status_mismatch",
)
nonempty_classes = [cls for cls in schema_finding_classes if sf.get(cls)]
if nonempty_classes:
    return {
        "moved": 0,
        "skipped_due_to_schema_findings": True,
        "schema_finding_classes_nonempty": nonempty_classes,
        "pre_audit": pre_audit,
    }
```

Cleanup now aborts (without write) on any non-empty schema-finding class. Idiomatic "fail-safe" posture for a mutating tool: if the audit reports anything anomalous, the mutating mode declines.

## F1 Fix: Pre-Existing-Failure Documentation

### Focused platform-smoke command (per proposal §"Specification-Derived Test Plan" T-platform-smoke)

```text
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook" --timeout=60
```

Result: **`1 failed, 170 passed, 1825 deselected, 1 warning in 177.39s`**.

Sole failure: `groundtruth-kb/tests/test_governance_hooks.py::test_bridge_compliance_blocks_verified_without_spec_to_test_evidence`.

Failure trace:

```text
>       assert "spec-to-test" in output["hookSpecificOutput"]["permissionDecisionReason"]
E       AssertionError: assert 'spec-to-test' in '[Governance] GO and VERIFIED bridge verdicts must include a clean Applicability Preflight section with packet_hash and missing_required_specs: []. ...'
groundtruth-kb\tests\test_governance_hooks.py:818: AssertionError
```

### Pre-existing-baseline evidence

Hypothesis: this failure pre-exists Sub-slice D and was introduced by Sub-slice C's `-006` VERIFIED (the new Applicability Preflight check fires before the spec-to-test check, so the spec-to-test deny reason never surfaces for the test's synthetic input).

Test conducted: stash all Sub-slice D new files (audit script + 2 test modules + audit log directory) and re-run the failing test against the otherwise-identical working tree:

```text
git stash --include-untracked -- scripts/audit_pending_owner_decisions.py \
  groundtruth-kb/tests/test_pending_owner_decisions_audit.py \
  groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py \
  memory/audit-log/

python -m pytest groundtruth-kb/tests/test_governance_hooks.py::test_bridge_compliance_blocks_verified_without_spec_to_test_evidence -v --timeout=30
```

Result: **`FAILED ... 1 failed, 1 warning in 2.79s`**. Identical AssertionError on the same line.

`git stash pop` restored the working tree.

Conclusion: the failure pre-exists Sub-slice D's introduction. It is the kind of "pre-existing-known-failure" the proposal's acceptance criterion `T-platform-smoke` allowed.

### Scope of failure relative to Sub-slice D's contract

- Sub-slice D modified: `scripts/audit_pending_owner_decisions.py` (new), `groundtruth-kb/tests/test_pending_owner_decisions_audit.py` (new), `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` (new).
- Sub-slice D did NOT modify: `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/tests/test_governance_hooks.py`, or any other path that could affect the failing test's behavior.
- The failure mode is fully explained by the bridge-compliance-gate's check ordering, which is Sub-slice C territory (committed `c7ff6cb6`/`639b981c` per the session handoff).

### Recommended follow-up (not in this slice)

The failing test is itself stale — its assertion was correct under the pre-Sub-slice-C bridge-compliance-gate but became inconsistent with the post-Sub-slice-C check ordering. A follow-up bridge should either: (a) update the test to provide a fixture with a valid Applicability Preflight section so the spec-to-test branch is reached, OR (b) split the test into two cases (one for each deny path). This is governance-test housekeeping outside Sub-slice D's scope. Capturing as a future follow-up rather than expanding Sub-slice D.

## Spec-to-Test Mapping (executed in REVISED-1)

| Test ID | Coverage | Result |
|---|---|---|
| `test_audit_schema_valid_live` | F2 schema validation; live byte-stability | **PASSED** |
| `test_audit_schema_required_fields_live` | F2 required fields | **PASSED** |
| `test_audit_no_duplicate_ids_live` | F2 unique IDs | **PASSED** |
| `test_audit_correct_section_placement_live` | F2 section/status consistency | **PASSED** |
| `test_audit_recognized_detected_via_live` | F2 recognized detected_via | **PASSED** |
| `test_audit_orphans_live` | F1 live orphans (bounded by `_KNOWN_LIVE_ORPHANS`) | **PASSED** |
| `test_audit_orphans_fixture` | F1 orphan logic against synthetic | **PASSED** |
| `test_cleanup_idempotency_fixture` | F3 idempotency | **PASSED** |
| `test_cleanup_auq_safety_fixture` | F3 AUQ-entry never qualifies (primary defense) | **PASSED** |
| `test_cleanup_auq_safety_failsafe_via_monkeypatch` | **NEW (REVISED-1)** F3 RuntimeError failsafe path exercised via injection per Codex `-006` F2 | **PASSED** |
| `test_cleanup_aborts_on_any_schema_finding` | **NEW (REVISED-1)** F2 6-class schema-abort coverage per Codex `-006` F2 | **PASSED** |
| `test_cleanup_atomic_write_fixture` | F3 atomic write | **PASSED** |
| `test_cleanup_does_not_mutate_live_in_test_run` | F3 test-suite live byte-stability | **PASSED** |
| `test_audit_corruption_path_isolated` | F2 corruption-rename containment | **PASSED** |
| `test_cleanup_log_appended_fixture` | F3 mutation evidence + run-marker | **PASSED** |

## Commands Run

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit
```

Result: **PASS** — `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. (Rerunning post-INDEX-update will show `operative_file: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-007.md`.)

```text
python -m pytest groundtruth-kb/tests/test_pending_owner_decisions_audit.py -v --timeout=60
```

Result: **`15 passed, 1 warning in 0.63s`**.

```text
python -m pytest groundtruth-kb/tests/ -k "owner_decision or audit or hook" --timeout=60
```

Result: **`1 failed, 170 passed, 1825 deselected, 1 warning in 177.39s`**. Sole failure is the pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` documented above.

```text
python scripts/audit_pending_owner_decisions.py --json
```

Output (post F2 tightening — same data as `-005`):

```json
{
  "section_counts": {"pending": 0, "resolved": 412, "history": 0},
  "total_entries": 412,
  "detected_via_distribution": {
    "prose:offering_or_choice": 36, "prose:standing_by_for": 45,
    "prose:awaiting_input": 90, "prose:your_decision_q": 3,
    "prose:should_i_or": 13, "ask_user_question": 225
  },
  "status_distribution": {"resolved": 412},
  "schema_findings": {
    "missing_required": [], "bad_id_format": [], "bad_asked_at": [],
    "unrecognized_detected_via": [], "duplicate_ids": [],
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
cat memory/audit-log/sub-slice-d-cleanup-2026-05-04.log
```

Output (4 lines from two cleanup invocations during the slice):

```text
2026-05-04T16:36:59Z run started cleanup invocation against pending-owner-decisions.md per DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE
2026-05-04T16:36:59Z run completed no-op (0 historical-FP candidates in ## Pending; pending section size=0)
2026-05-04T18:28:40Z run started cleanup invocation against pending-owner-decisions.md per DELIB-S332-D-F3-CLEANUP-PATH-1-CHOICE
2026-05-04T18:28:40Z run completed no-op (0 historical-FP candidates in ## Pending; pending section size=0)
```

```text
git diff --name-only -- applications/
```

Result: empty (no `applications/` content modified).

## Codex `-006` Verification Expectations Re-Addressed

- **Approved focused platform-smoke command must show PASS or pre-existing-known-failures only** — confirmed via REVISED-1 §"F1 Fix" with concrete baseline evidence. The single failure pre-exists Sub-slice D and is recommended for follow-up housekeeping outside this slice.
- **Cleanup safety: abort on schema findings as report claimed** — confirmed via REVISED-1 §"F2 Fix" + new test `test_cleanup_aborts_on_any_schema_finding` exercising all 6 schema-finding classes.
- **AUQ safety: cleanup raises and aborts when AUQ entry would qualify** — confirmed via new test `test_cleanup_auq_safety_failsafe_via_monkeypatch` injecting a synthetic AUQ candidate and asserting `RuntimeError` before any file mutation.

## Acceptance Criteria

Pre-implementation:
- [x] Codex GO on REVISED-1 proposal (received at `-004`)
- [x] Preflight passes

Post-implementation (VERIFIED contingent):
- [x] All 15 tests PASS (including 2 new fixture tests for F2/AUQ failsafe paths)
- [x] Focused platform-smoke shows pre-existing-known-failure only; concrete baseline evidence provided
- [x] Live `memory/pending-owner-decisions.md` byte-stable across audit/cleanup invocations
- [x] Test suite leaves new files only in `git status` (no unrelated mutations)
- [x] No regression in GT-KB platform tests (sole failure is pre-existing per F1 baseline)
- [x] `memory/audit-log/sub-slice-d-cleanup-2026-05-04.log` documents every cleanup invocation (run-marker lines)
- [x] Cleanup schema-abort covers all 6 schema-finding classes (per F2 tightening)
- [x] AUQ safety failsafe demonstrably aborts via fixture test (per Codex `-006` F2 hint)

## Risk Status

All `-003` risk mitigations remain in force. F2 tightening narrows the cleanup attack surface (more conservative); no new risks introduced. The pre-existing platform-smoke failure (F1) is governance-test housekeeping, not a Sub-slice D defect.

## Project Root Boundary Compliance

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/scripts/audit_pending_owner_decisions.py`
- `E:/GT-KB/groundtruth-kb/tests/test_pending_owner_decisions_audit.py`
- `E:/GT-KB/memory/audit-log/sub-slice-d-cleanup-2026-05-04.log`

No `applications/` content modified.

## Next

Sub-slice E (requirements-collection hook impl) and Sub-slice F (release metrics + promotion to enforcement) — to be filed after Sub-slice D VERIFIED. Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L.

A separate future bridge should address the pre-existing `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` test failure (governance-test housekeeping introduced by Sub-slice C's preflight-check ordering; not in Sub-slice D's scope).
