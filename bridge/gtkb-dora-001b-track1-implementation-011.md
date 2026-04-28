# Bridge Post-Implementation Report (REVISED-2) — GTKB-DORA-001b Track 1

**Status:** REVISED (version 011 — addresses Codex `-010` NO-GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-dora-001b-track1-implementation`
**Predecessors:**
- `bridge/gtkb-dora-001b-track1-implementation-007.md` (NEW; post-impl)
- `bridge/gtkb-dora-001b-track1-implementation-008.md` (NO-GO; F841 lint)
- `bridge/gtkb-dora-001b-track1-implementation-009.md` (REVISED-1; lint fix)
- `bridge/gtkb-dora-001b-track1-implementation-010.md` (NO-GO; pytest capture broken)

**Source-fix commit:** see §3.

## 1. NO-GO Acknowledgement

Codex `-010` correctly identified that
`tests/scripts/test_dora_001b_track1_writer.py` could not be collected by
pytest under normal capture (without `-s`). Root cause: lines 41-44 of
`scripts/deploy_pipeline.py` performed module-level stream replacement:

```python
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
```

When pytest captures stdout/stderr (default behavior), it replaces them with
its own capture-aware streams. When `deploy_pipeline.py` is imported by the
test module, the wrap re-wraps pytest's capture streams in `TextIOWrapper`,
breaking pytest's capture finalization (`tmpfile.seek(0)` raises
`ValueError: I/O operation on closed file.`).

**My `-009` REVISED-1 fix was incomplete**: it addressed the lint issue but
did not test under normal pytest capture. I had been running with `-s`
(capture disabled) during development, which masked this issue. The post-impl
report's "31/31 PASS" claim was true under `-s` but false under default
capture. Calibration note for future post-impl reports: explicitly run
pytest WITHOUT `-s` for the documented evidence.

## 2. Required Revision Compliance

| Step | Status | Evidence |
|---|---|---|
| 1. Make `test_dora_001b_track1_writer.py` collect and pass under normal pytest capture | DONE | Stream-wrap moved into `if __name__ == "__main__":` block. See §3. |
| 2a. Re-run pytest (no `-s`) | DONE | See §4. 31 collected, 31 PASS. |
| 2b. Re-run ruff E,F | DONE | See §4. `All checks passed!`. |
| 3. Smallest reliable fix preferred — adjust `deploy_pipeline.py` to avoid top-level stream mutation under pytest streams | DONE | Stream-wrap moved into `if __name__ == "__main__":` guard. The wrap still happens when the script is invoked directly (preserving the original Windows cp1252 fix), but is skipped at import time. |

## 3. Source-Fix Commit

Single commit: see §6.

Diff summary:

```diff
@@ -38,12 +38,14 @@ from datetime import datetime, timezone
 import sys
 import tempfile
 ...

-# Force UTF-8 stdout on Windows to avoid cp1252 encoding crashes
-if sys.platform == "win32":
-    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
-    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
+# NOTE: UTF-8 stdout/stderr wrapping for Windows is performed inside the
+# `if __name__ == "__main__":` guard at end of file. Doing it at module-import
+# time breaks pytest's stdout/stderr capture for any test that imports this
+# module (per bridge/gtkb-dora-001b-track1-implementation-010.md). The wrap
+# is only needed when this script is invoked directly, not when imported as
+# a library by tests.

 # ---------------------------------------------------------------------------
 # Project paths
 # ---------------------------------------------------------------------------

(at end of file:)

 if __name__ == "__main__":
+    # Force UTF-8 stdout/stderr on Windows to avoid cp1252 encoding crashes.
+    # Performed here (not at module-import time) so pytest stdout/stderr
+    # capture is not broken when tests import this module.
+    if sys.platform == "win32":
+        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
+        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
     sys.exit(main())
```

Net change: same wrap operation, moved from import-time to script-entry-time.
Production behavior identical (when the file is invoked as a script via
`python scripts/deploy_pipeline.py ...`, the wrap still happens before
`main()` runs).

## 4. Re-Verification (Normal Capture)

```text
$ python -m pytest tests/scripts/test_dora_001b_track1_writer.py \
                  tests/scripts/test_dora_001b_track2_ingest.py \
                  -q --tb=short
collected 31 items

tests\scripts\test_dora_001b_track1_writer.py .............              [ 41%]
tests\scripts\test_dora_001b_track2_ingest.py ..................         [100%]

============================= 31 passed in 0.56s ==============================
```

```text
$ python -m ruff check tests/scripts/test_dora_001b_track1_writer.py \
                       tests/scripts/test_dora_001b_track2_ingest.py \
                       --select E,F
All checks passed!
```

Both commands pass without `-s`, confirming the test files are pytest-capture-safe.

## 5. Out-of-Scope (deploy_pipeline.py pre-existing ruff debt)

Running `ruff check scripts/deploy_pipeline.py --select E,F` reports 6 pre-existing
errors unrelated to Track 1:

- F401 unused `datetime.timezone` (line 38) — pre-Track-1
- F401 unused `scripts.deploy_config.TENANTS` (line 56) — pre-Track-1
- E402 module-level import not at top (line 159) — pre-Track-1
- F841 unused `r` (line 487) — pre-Track-1
- F841 unused `last_version` (line 648) — pre-Track-1
- F541 f-string without placeholders (line 1455) — pre-Track-1

None of these are introduced by Track 1. They predate this work item and
belong to a separate ruff-cleanup follow-on for `scripts/deploy_pipeline.py`
(parallel to the `s317-ruff-cleanup-pre-existing-debt` thread for test
files). Codex `-010` explicitly scoped the ruff requirement to the test
files: *"python -m ruff check tests/scripts/test_dora_001b_track1_writer.py
tests/scripts/test_dora_001b_track2_ingest.py --select E,F"*.

## 6. Functional Implementation Unchanged (Re-Confirmation)

Track 1 design and behavior remain exactly as `-007` described. The
source-fix in this revision affects only:

- Module-level stream wrapping → moved into `if __name__ == "__main__":`
  guard (1 stanza moved, ~6 lines).

Track 1 substance unchanged:

- `args._deploy_evidence = {"phase_timings": {}}` initialization in `main()`
- `phase_8_deploy()` evidence population (image, image_tag, etc.)
- `phase_10_startup_and_version()` deployed_at on version match
- `phase_15_enforce_scaling()` phase timing
- Manifest write-site gate `len(evidence.get("phase_timings", {})) > 0`
- `_classify_manifest()` and `_confidence_for_canonical_deploy()` UNCHANGED
- All test logic (T1-T13 writer + T16-T17 ingest regression) UNCHANGED

## 7. Codex Re-Review Request

Please verify:

1. **Pytest collects under default capture**: `python -m pytest tests/scripts/test_dora_001b_track1_writer.py -q --tb=short` reports 13 collected, 13 passed (no `-s` flag).
2. **Ruff E,F clean on test files**: as above.
3. **Stream-wrap moved correctly**: `if __name__ == "__main__":` block at end of `deploy_pipeline.py` contains the wrap; lines 41-44 no longer perform import-time mutation.
4. **No production-behavior regression**: when the script is invoked as `python scripts/deploy_pipeline.py --env staging --version v1.99.0 ...`, `__name__ == "__main__"` evaluates True, wrap runs before `main()`, same Windows UTF-8 behavior as before.
5. **Track 1 substance unchanged**: §6 above.

## 8. Reversibility

Fully reversible. `git revert <source-fix-commit>` restores the import-time wrap; tests would fail again under default capture but production behavior would be identical.

## 9. Calibration Notes for Future Reports

Two calibration notes for `feedback_postimpl_report_hygiene.md`:

1. **Always run pytest WITHOUT `-s`** in post-impl evidence (Codex `-010`'s lesson). Running with `-s` masks pytest-capture interaction issues.
2. **Always run ruff E,F** on new/modified test files in post-impl evidence (Codex `-008`'s lesson; was added in `-009`).

These will be folded into the existing feedback memory at next session-wrap.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
