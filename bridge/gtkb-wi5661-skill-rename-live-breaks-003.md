NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c685e1d2-4271-4679-8ceb-70491ed1d6a9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Document: gtkb-wi5661-skill-rename-live-breaks
Version: 003
bridge_kind: implementation_report
Responds to: bridge/gtkb-wi5661-skill-rename-live-breaks-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661
target_paths: ["scripts/gtkb_bridge_writer.py", ".claude/hooks/bridge-axis-2-surface.py", "scripts/per_thread_finalization_repair.py"]

# WI-5661 — Post-Implementation Report (partial scope: findings 1, 2, 4)

## Summary

Implemented 3 of the 6 GO'd skill-rename live-break fixes (findings 1, 2, 4) from
`gtkb-wi5661-skill-rename-live-breaks-001.md` (GO at `-002`, Loyal Opposition / Antigravity-C).
Findings 3, 5, 6 are deferred with documented rationale (§ Deferred Findings); each is blocked by
an external factor — a work-subject gate, a concurrent session's uncommitted BOM, and an
out-of-scope test-fixture coupling respectively — not by the fix itself. The URGENT finding 1
(provider VERIFIED finalizer) is included and verified.

**LO routing note:** route this verification to Codex-A or Antigravity-C, NOT provider harnesses
D/F/H — their VERIFIED finalizer is the exact break finding 1 repairs and is not yet committed, so a
provider-harness VERIFIED finalization would fail closed.

## Scope Delta From GO'd Proposal

The GO'd proposal declared 6 source `target_paths`. This report covers 3:

- **Implemented:** finding 1 (`scripts/gtkb_bridge_writer.py`), finding 2
  (`.claude/hooks/bridge-axis-2-surface.py`), finding 4 (`scripts/per_thread_finalization_repair.py`).
- **Deferred to follow-up slices:** findings 3, 5, 6.

## Specification Links (carried forward from -001)

- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane governance path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge finalization/surface authority (the breaks degrade it).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal/report spec linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` coverage.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — config/hooks tracked-mirror model.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification.

## Implemented Changes

### Finding 1 — `scripts/gtkb_bridge_writer.py` (provider VERIFIED finalizer) — URGENT

`_finalize_verified_provider_verdict` hardcoded `.claude/skills/verify/helpers/write_verdict.py`
(bare `verify`, non-existent post-WI-5651-rename), so the provider finalizer failed closed
(`raise BridgePublicationError`). Fixed with a prefer-gtkb / fallback-legacy resolver:

    helper = project_root / ".claude" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py"
    if not helper.is_file():
        _legacy = project_root / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
        if _legacy.is_file():
            helper = _legacy

### Finding 2 — `.claude/hooks/bridge-axis-2-surface.py` (axis-2 surfacing)

`_load_scan_bridge_helper` hardcoded `.claude/skills/bridge/helpers/scan_bridge.py` (bare `bridge`);
FileNotFoundError every prompt. Fixed with the same prefer-`gtkb-bridge` / fallback-legacy pattern.
Runtime-only: `.claude/` is git-ignored; the durable tracked mirror is finding 3 (deferred).

### Finding 4 — `scripts/per_thread_finalization_repair.py` (module-broken-on-import)

`VERIFY_HELPERS` pointed at bare `.claude/skills/verify/helpers`; the top-level
`from write_verdict import ...` failed on import. Fixed with prefer-`gtkb-verify` / fallback-legacy
directory resolution.

## Deferred Findings

- **Finding 3** (`config/hooks/gtkb-bridge-axis-2-surface.py`): the `GTKB-WORK-SUBJECT` gate blocks the
  edit, misclassifying this platform bridge-hook mirror as "application product artifacts." The file is
  also currently **untracked** — it is the concurrent file-move-rename session's new file. Deferred
  pending (a) a work-subject-gate classification fix and (b) that session committing the mirror. The
  live break is mitigated in the runtime copy by finding 2.
- **Finding 5** (`scripts/harness_parity_phase2.py`): `ruff format --check` FAILS on this file due to a
  concurrent session's UTF-8 **BOM** on line 1 (part of an unrelated capability-registry rename, not
  WI-5661). Per the sibling `-repair` NO-GO (Codex, P2), a changed Python path must show clean ruff
  evidence. Deferred until the concurrent session commits/attributes its hunk.
- **Finding 6** (`scripts/verify_antigravity_dispatch.py`): the source fix (anchor paths → `gtkb-verify`)
  requires updating 2 fixtures in `platform_tests/scripts/test_verify_antigravity_dispatch.py` (bare
  `verify` → `gtkb-verify`), but that test file is **outside the GO'd `target_paths`**. My finding-6 edit
  was **reverted** to keep the file's tests green; deferred to a slice whose target_paths include the test.

## Spec-to-Test Mapping

| Finding / Spec | Test / Command | Result |
|---|---|---|
| Finding 1 / `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest test_gtkb_bridge_writer.py`; assert `.claude/skills/gtkb-verify/helpers/write_verdict.py` resolves | PASS |
| Finding 2 / `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest test_bridge_axis_2_surface.py`; assert `.claude/skills/gtkb-bridge/helpers/scan_bridge.py` resolves | PASS |
| Finding 4 / `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest test_per_thread_finalization_repair.py`; `import per_thread_finalization_repair` succeeds | PASS |
| Code quality / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` + `ruff format --check` on the 3 changed files | PASS |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_bridge_writer.py scripts/per_thread_finalization_repair.py .claude/hooks/bridge-axis-2-surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <same 3 files>
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_bridge_axis_2_surface.py platform_tests/scripts/test_per_thread_finalization_repair.py -q
```

## Observed Results

- `ruff check`: All checks passed. `ruff format --check`: 3 files already formatted.
- `pytest` (findings 1, 2, 4 test files): all PASS.
- Per-finding assertions: `gtkb-verify` / `gtkb-bridge` paths resolve; `per_thread_finalization_repair`
  imports cleanly.

## Commit Finalization Plan (hunk-patch required)

- `scripts/gtkb_bridge_writer.py` carries an **unrelated concurrent routing-flip**
  (`ENVELOPE_RESPONDER_BY_STATUS` reversed, ~lines 62-73) from the file-move-rename session — NOT WI-5661.
  VERIFIED finalization MUST **hunk-patch ONLY the finding-1 hunk** (~lines 627-633), leaving the
  routing-flip uncommitted.
- `scripts/per_thread_finalization_repair.py`: clean — direct include.
- Finding 2 (`.claude/hooks/...`): git-ignored, runtime-only, NOT committed.

## Recommended Commit Type

Recommended commit type: `fix:` — repairs broken path resolution in live code; no new capability surface.

## Owner Decisions / Input

- Owner AUQ (session `c685e1d2-4271-4679-8ceb-70491ed1d6a9`, 2026-07-24): authorized filing this partial
  report — "File 1,2,4,6 now; defer 3 & 5" (finding 6 subsequently forced to defer on the out-of-scope
  test-fixture coupling), then "File v003 now; you route to A/C."
- Governing owner decision: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizing
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.

## Prior Deliberations

- `DELIB-202667106` / `DELIB-202667105` — canonical skill-rename rollout (the rename these references lag).
- `DELIB-202667193` — owner directed live breaks first with per-slice GO/VERIFIED gates.
- Sibling thread `gtkb-wi5661-skill-rename-live-break-repair` (Codex, NO-GO `-002`): Codex deferred its
  duplicate to THIS thread (P1) and set the clean-ruff / attribute-dirty-hunks bar (P2) this report honors.

## Root-Boundary / In-Root Placement

All changed paths are within `E:\GT-KB`.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
