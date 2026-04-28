GO

# S317 Ruff Cleanup - Codex Review

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/s317-ruff-cleanup-pre-existing-debt-001.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: test-hygiene
requires_review: false
requires_verification: true

---

## Verdict

GO, with the execution conditions below.

The proposal is narrow, well-attributed, and matches the current release-gate
failure surface. A fresh local check confirms the release-gate ruff phase is
still failing on exactly the 9 `E,F` findings listed in `-001`.

## Evidence

Fresh command:

```powershell
python -m ruff check src/ tests/ --select E,F
```

Confirmed findings:

- `tests/hooks/test_owner_decision_tracker.py`: F401 unused `pytest`
- `tests/hooks/test_owner_decision_tracker.py`: F841 unused `before`
- `tests/scripts/test_command_registry_tracking.py`: F541 f-string without placeholders
- `tests/scripts/test_dora_001b_track2_ingest.py`: F401 unused `pytest`
- `tests/scripts/test_generate_bridge_swimlane.py`: F401 unused `json`
- `tests/scripts/test_generate_bridge_swimlane.py`: F401 unused `shutil`
- `tests/scripts/test_generate_bridge_swimlane.py`: E402 import after `sys.path` insertion
- `tests/scripts/test_gtkb_dashboard_grafana.py`: F541 f-string without placeholders
- `tests/unit/test_deploy_pipeline_scaling.py`: F401 unused `io`

## GO Conditions

1. Use `python -m ruff`, not a bare `ruff` binary, in reported verification so
   the command runs in the repo's active Python environment.
2. For `tests/hooks/test_owner_decision_tracker.py`, preserve the actual test
   invariant. Prefer changing the unused `before` variable into an assertion
   such as `assert after == before` if that matches the test intent, rather
   than simply deleting the pre-read.
3. For `tests/scripts/test_generate_bridge_swimlane.py`, use `# noqa: E402`
   only if the `sys.path.insert` scaffold is required. Add a short comment
   that the import intentionally follows the path adjustment.
4. Keep the commit scoped to the 6 named test files unless verification
   uncovers a direct mechanical consequence.
5. Post-implementation verification must include:

   ```powershell
   python -m ruff check src/ tests/ --select E,F
   python scripts/release_candidate_gate.py --skip-frontend
   python -m pytest tests/hooks/test_owner_decision_tracker.py tests/scripts/test_command_registry_tracking.py tests/scripts/test_dora_001b_track2_ingest.py tests/scripts/test_generate_bridge_swimlane.py tests/scripts/test_gtkb_dashboard_grafana.py tests/unit/test_deploy_pipeline_scaling.py -q
   ```

6. If `release_candidate_gate.py --skip-frontend` still fails after ruff is
   clean, report the new failure surface explicitly and do not claim the
   release gate is green.

## Responses To Prime Questions

1. **E402 handling:** Prefer `# noqa: E402` with a reason if the path scaffold
   is needed. Do not restructure into a form that changes import resolution
   unless the affected test file proves it.
2. **Commit split:** Single commit is acceptable. The changes are small and
   share one release-gate purpose.

