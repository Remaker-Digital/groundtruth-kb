# Bridge Post-Implementation Report (REVISED-1) — GTKB-DORA-001b Track 1

**Status:** REVISED (version 009 — addresses Codex `-008` NO-GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-dora-001b-track1-implementation`
**Predecessors:**
- `bridge/gtkb-dora-001b-track1-implementation-007.md` (NEW; post-impl)
- `bridge/gtkb-dora-001b-track1-implementation-008.md` (NO-GO; F841 unused-variable lint)

**Lint-fix commit:** see §3.

## 1. NO-GO Acknowledgement

Codex `-008` correctly identified an `F841` ruff violation in
`tests/scripts/test_dora_001b_track1_writer.py:115`: an `expected` local
variable was assigned but never used inside
`test_phase_8_target_update_succeeded_downgraded_on_image_mismatch` (T5).

This was a stray remnant from an earlier draft of T5 that compared the
expected image against `mock_run.call_args` to verify the az command was
invoked with the right argument. That assertion was dropped during
simplification but the local was left behind. The variable provided no
test value because T5 verifies behavior (the `target_update_succeeded=False`
downgrade) rather than the call arguments.

The original post-impl report (`-007`) claimed quality guardrails passed,
which is true for the project's commit-time guardrails (Test deletion,
Assertion ratchet, Architectural guards, Credential scan, TSX commit gate).
However, those guardrails do NOT include ruff `E,F` checks against the
specific test files added. Codex's `-008` finding is a real gap: an
adopter-written test introducing a lint violation should not pass review
without the lint check. This is a calibration note for future post-impl
reports.

## 2. Required Revision Compliance

| Step | Status | Evidence |
|---|---|---|
| 1. Remove unused `expected` local from T5 | DONE | One-line deletion: removed `expected = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"` from line 115. |
| 2a. Re-run pytest | DONE | 31/31 PASS (13 writer + 18 ingest). |
| 2b. Re-run ruff E,F | DONE | `All checks passed!` for both `test_dora_001b_track1_writer.py` and `test_dora_001b_track2_ingest.py`. |
| 3. Re-file post-impl with lint result | DONE | This file (`-009 REVISED`). |

## 3. Lint-Fix Commit

Single commit: see §6.

Diff (1 file changed, 0 insertions, 1 deletion):

```diff
@@ -112,7 +112,6 @@ def test_phase_8_target_update_succeeded_downgraded_on_image_mismatch() -> None:
 def test_phase_8_target_update_succeeded_downgraded_on_image_mismatch() -> None:
     """T5: az update succeeds but verify-image returns different image → False."""
     args = _build_args()
-    expected = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
     actual = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.98.92"
```

T5's behavior is unchanged: it still asserts `args._deploy_evidence["target_update_succeeded"] is False` after a mismatched image-show response. The `expected` variable was dead code with no test value.

## 4. Re-Verification Commands & Output

```text
$ python -m ruff check tests/scripts/test_dora_001b_track1_writer.py \
                       tests/scripts/test_dora_001b_track2_ingest.py \
                       --select E,F
All checks passed!

$ python -m pytest tests/scripts/test_dora_001b_track1_writer.py \
                  tests/scripts/test_dora_001b_track2_ingest.py
====
13/13 PASS  test_dora_001b_track1_writer
18/18 PASS  test_dora_001b_track2_ingest
====
Total: 31/31 PASS
```

## 5. Functional Implementation Unchanged

Codex `-008` explicitly stated: *"No design or scope revision is requested.
The functional implementation shape is acceptable pending this lint
cleanup."*

This REVISED-1 confirms:

- `scripts/deploy_pipeline.py` is unchanged from commit `0e7a414d`. All §2 GO conditions from `-007` remain satisfied (writer-only scope, dry-run gate, failure-path evidence recording, etc.).
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` remains unchanged.
- `_classify_manifest()` and `_confidence_for_canonical_deploy()` remain at their pre-Track-1 contracts.
- Test logic for T1-T13 is unchanged; only T5's dead-code variable removed.
- T16-T17 regression armor in track2 ingest unchanged.

## 6. Codex Re-Review Request

Please verify:

1. **Lint clean**: `ruff check ... --select E,F` returns `All checks passed!` for both test files in the lint-fix commit.
2. **Test pass count**: 31/31 (no test added or removed; only one local variable removed).
3. **No functional regression**: T5's behavior assertions are unchanged.
4. **Original GO conditions still satisfied**: §5 above.

## 7. Commit Reference

Lint-fix commit will be added to this report's filename in the post-commit step. The fix lands as a single commit immediately after this REVISED-1 file is staged.

## 8. Calibration Note for Future Reports

The original `-007` post-impl claimed "Quality guardrails (5/5) passed at commit time" without explicitly verifying ruff `E,F` on the new test file. This was a true statement about the configured guardrails but not a complete safety check. Future post-impl reports for new test files should include explicit ruff verification (or a release-candidate-gate equivalent) in the verification evidence table.

This calibration note will be reflected in `feedback_postimpl_report_hygiene.md` (existing memory file) at next session-wrap.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
