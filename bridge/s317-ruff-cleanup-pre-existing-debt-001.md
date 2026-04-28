NEW

# S317 Ruff Cleanup — Pre-Existing Tech Debt

**Status:** NEW (P2; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Closes (when VERIFIED):** Release-candidate gate red attribution carried forward across [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) and [bridge/harness-state-authority-migration-2026-04-27-010.md](bridge/harness-state-authority-migration-2026-04-27-010.md).

---

## Prior Deliberations

- [bridge/s317-working-tree-triage-007.md](bridge/s317-working-tree-triage-007.md) §3 — first attribution of the 9 pre-existing ruff E,F errors.
- [bridge/s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) — Codex VERIFIED of the attribution analysis.
- [bridge/harness-state-authority-migration-2026-04-27-007.md](bridge/harness-state-authority-migration-2026-04-27-007.md) §6 Q3 — recommended filing as a separate bridge in next session; here.

## §0. Scope

Fix the 9 pre-existing ruff `E,F` errors in 6 test files that have caused `release_candidate_gate.py --skip-frontend` to FAIL across both verified threads of S317.

**In scope:** 9 errors in 6 test files (per [s317-working-tree-triage-008.md](bridge/s317-working-tree-triage-008.md) §"Failure surface"):

| File | Line | Code | Description |
|---|---|---|---|
| tests/hooks/test_owner_decision_tracker.py | 35 | F401 | `pytest` imported but unused |
| tests/hooks/test_owner_decision_tracker.py | 431 | F841 | unused `before` local var |
| tests/scripts/test_command_registry_tracking.py | 107 | F541 | f-string without placeholder |
| tests/scripts/test_dora_001b_track2_ingest.py | 23 | F401 | `pytest` imported but unused |
| tests/scripts/test_generate_bridge_swimlane.py | 12 | F401 | `json` imported but unused |
| tests/scripts/test_generate_bridge_swimlane.py | 14 | F401 | `shutil` imported but unused |
| tests/scripts/test_generate_bridge_swimlane.py | 26 | E402 | module-level import not at top |
| tests/scripts/test_gtkb_dashboard_grafana.py | 232 | F541 | f-string without placeholder |
| tests/unit/test_deploy_pipeline_scaling.py | 34 | F401 | `io` imported but unused |

**Out of scope:** Other ruff rule classes (e.g., I001 import-order); only `E,F` per release-gate config.

## §1. Implementation plan (1 commit)

Per ruff: 7 of 9 are auto-fixable (`--fix` flag); 2 require manual review:
- F841 unused local: remove the assignment line.
- E402 module-level import not at top: investigate test scaffolding around line 24-26 (sys.path.insert pattern) and decide whether to `# noqa: E402` or restructure.

**Approach:**
1. Run `ruff check src/ tests/ --select E,F --fix` for the 7 auto-fixable.
2. Manually fix `tests/hooks/test_owner_decision_tracker.py:431` (delete unused local).
3. Manually inspect `tests/scripts/test_generate_bridge_swimlane.py:24-26` and add `# noqa: E402` if the sys.path.insert pattern is required. If not required, reorder imports.
4. Verify: `python scripts/release_candidate_gate.py --skip-frontend` returns PASS (or at least no ruff E,F errors).

**1 commit:** `tests: Fix 9 pre-existing ruff E,F errors (release-gate green)`.

## §2. Verification

- `python -m ruff check src/ tests/ --select E,F` → exit 0.
- `python scripts/release_candidate_gate.py --skip-frontend` → no E,F failures (other gate steps may still fail unrelated; that's separate).
- All affected test files still pass: `python -m pytest tests/hooks/test_owner_decision_tracker.py tests/scripts/test_command_registry_tracking.py tests/scripts/test_dora_001b_track2_ingest.py tests/scripts/test_generate_bridge_swimlane.py tests/scripts/test_gtkb_dashboard_grafana.py tests/unit/test_deploy_pipeline_scaling.py -q`.
- Per-commit guardrails: 5/5 PASS.

## §3. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Auto-fix removes a deliberately-unused `pytest` import that has side effects | LOW (P3) | pytest doesn't have import-side-effects; if a test fails post-fix, restore the import with `# noqa: F401` and explanatory comment. |
| F841 `before` local was used for debugging or future planned check | LOW (P3) | Read the full test before removing; if intent is unclear, leave with `# noqa: F841` and explanatory comment. |
| E402 fix breaks sys.path.insert ordering | MEDIUM (P2) | Inspect first; prefer `# noqa: E402` if reordering would break the test. |
| Auto-fix introduces an actual regression | LOW (P3) | Per-commit guardrails run the affected tests; CI catches before merge. |

## §4. Codex review questions

1. Use `# noqa: E402` for the sys.path.insert pattern, or restructure imports? Recommendation: noqa with comment explaining the test-scaffold reason.
2. Single commit acceptable, or split auto-fix from manual fixes? Recommendation: single commit; the changes are mechanical and small.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
