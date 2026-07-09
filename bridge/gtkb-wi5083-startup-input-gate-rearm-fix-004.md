NEW

# gtkb-wi5083-startup-input-gate-rearm-fix — Post-Implementation Report (WI-5083)

bridge_kind: implementation_report
Document: gtkb-wi5083-startup-input-gate-rearm-fix
Version: 004
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC
Responds to: bridge/gtkb-wi5083-startup-input-gate-rearm-fix-003.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: cb6f9937-1f03-4d62-80de-69d8bb00e292
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatched Prime Builder worker (GTKB_BRIDGE_POLLER_RUN_ID=2026-07-09T15-24-35Z-prime-builder-B-07e1ab); resolved_role=prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5083

target_paths: ["scripts/session_start_dispatch_core.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py", "platform_tests/scripts/test_session_continuation_sources_parity.py", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented WI-5083 per the GO'd proposal (-001) and its confirmatory manual re-review GO (-003), applying the exact old→new block replacements and full new-test files from the verified review-ready package `WI-5083-startup-gate-rearm-review-package.md`. Both fixes are in place across all eight authorized `target_paths`:

- **Fix (a) — root cause:** `session_start_dispatch_core.py` now reads the SessionStart hook stdin `source` (fail-soft) and threads it to the startup service via `--session-start-source`; `session_self_initialization.py` gates the arm through a new `_maybe_arm_startup_interaction_guard` wrapper that skips arming on a mid-session continuation (`resume`/`compact`) and records `armed_source` on each arm.
- **Fix (b) — belt-and-suspenders:** the tracked readers (`workstream_focus.py::_startup_response_pending` and the Codex `session_wrapup_trigger_dispatch.py::_startup_input_gate_active`) now treat a continuation-armed gate as inactive/stale rather than blocking, preserving the legitimate fresh-start await.

All changes are additive and fail-soft: an absent/unread `source` degrades to `"startup"` (pre-WI-5083 behavior), the arm is only ever skipped (never newly-blocking) for continuations, and Fix (b) only ever relaxes a block. The legitimate fresh-start await still blocks (regression-tested).

The line numbers in the package were from the authoring worktree; each old-block was matched against the current canonical tree by exact text. Two canonical-tree adaptations were required and are noted below (they do not change behavior).

## Specification Links

Carried forward from the GO'd proposal (-001) and re-validated in the confirmatory GO (-003):

- `GOV-RELIABILITY-FAST-LANE-001` — reliability fast-lane; WI-5083's project home and governing authority for a bounded, spec-linked defect fix.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — the startup relay owns the genuinely-first prompt of a fresh session; the gate must not spuriously own mid-session prompts.
- `GOV-SESSION-SELF-INITIALIZATION-001` — fresh-session self-initialization; the arm belongs to a genuinely-fresh SessionStart, not a continuation.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — init-keyword disclosure-relay contract the gate serves; the relay window is kept intact for a fresh start.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — SessionStart hot-path budget; the new source reader is stdlib-light and fail-soft.
- `ADR-CROSS-HARNESS-PARITY-001` — cross-harness parity for the Codex-side reader change and the reconcile-on-merge of the untracked Claude reader.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail / GO-NO-GO discipline governing this report and its verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing specs cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/WI linkage metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests executed; mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-5083 tracked in MemBase work_items, member of PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) — every changed path is fully in-root under `E:\GT-KB` (`scripts/`, `platform_tests/`, `.codex/gtkb-hooks/`); no artifact is created, read as a live dependency, or resolved to an Agent Red / application surface. The single "Agent Red" reference in this report is a verbatim quotation of a pre-existing failing test's expected string, not a live application-placement dependency. CLAUSE-IN-ROOT satisfied (matches the -003 GO clause preflight).

## Spec-to-Test Mapping (executed)

Interpreter: project venv (`groundtruth-kb/.venv/Scripts/python.exe`). All tests PASS.

| Linked spec(s) | Behavior | Test(s) | Result |
|---|---|---|---|
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` + `GOV-RELIABILITY-FAST-LANE-001` (Fix a: arm only on a genuinely-fresh start) | continuation source does not re-arm an active gate; fresh/absent source arms and records `armed_source` | `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py` (5 cases) | PASS |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` + `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (Fix b: continuation-armed does not block; fresh-start await still blocks) | `test_continuation_armed_gate_does_not_block_tool_use`, `test_fresh_armed_gate_still_blocks_within_window` | `platform_tests/hooks/test_workstream_focus.py` (2 appended cases) | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (fail-soft source reader) | `_read_session_start_source` extracts source; returns None on tty/empty/bad-json/absent | `platform_tests/scripts/test_session_start_dispatch_core.py` (4 appended cases) | PASS |
| `ADR-CROSS-HARNESS-PARITY-001` (the continuation-sources constant duplicated across three hot-path modules) | asserts the three copies stay equal (mirrors the `_SESSION_ROLE_MARKER_NAME` parity contract) | `platform_tests/scripts/test_session_continuation_sources_parity.py` (1 case) | PASS |

## Verification Evidence (commands + results)

- **Targeted regression** — `python -m pytest` the four targets above `-q --tb=short`:
  `93 passed, 3 skipped` (the 3 skips are pre-existing in `test_workstream_focus.py`, unrelated to WI-5083).
- **Wider guard** — `python -m pytest platform_tests/scripts/test_session_self_initialization.py test_claude_session_start_dispatcher.py test_codex_session_start_dispatcher.py`:
  `120 passed, 2 failed`. The 2 failures (`test_startup_model_contains_role_governance_and_kpi_inventory` — `accessibility_axe` status `partial` vs `ready`; `test_dashboard_and_report_are_written_with_time_series_kpi` — dashboard title `GT-KB Operations Dashboard` vs `Agent Red GT-KB Dashboard`) are **pre-existing baseline drift, not WI-5083 regressions** — see the Pre-Existing Unrelated Failures section below for the `git stash` baseline proof.
- **Code quality (BOTH separate gates, all 8 changed .py):** `python -m ruff check` → `All checks passed!`; `python -m ruff format --check` → `8 files already formatted`.
- **Cross-harness parity** — `python scripts/check_codex_hook_parity.py`: FAIL, but with **zero drift attributable to WI-5083** — identical failures on the pre-change baseline (see Pre-Existing Unrelated Failures). The change adds no new parity error, including no `_resolution_table_parity_errors`.

## Files Changed (my 8 authorized target_paths)

Clean diff vs HEAD (no line-ending churn — one file, `test_session_start_dispatch_core.py`, was LF at HEAD but the editor flipped it to CRLF; it was byte-normalized back to LF so its diff is the +38 real additions only):

- `scripts/session_start_dispatch_core.py` (+42): `_read_session_start_source` reader + `--session-start-source` threading. Canonical adaptation: command literal's first element is `prefer_pythonw_executable(sys.executable)` (not `sys.executable`).
- `scripts/session_self_initialization.py` (+63/-1): `_SESSION_CONTINUATION_SOURCES`, `_is_session_continuation_source`, `armed_source` on the arm, `_maybe_arm_startup_interaction_guard` wrapper, `--session-start-source` CLI arg, gated arm call.
- `scripts/workstream_focus.py` (+43): `_SESSION_CONTINUATION_SOURCES` + `_armed_source_is_session_continuation` (co-located with the startup-relay constants) and the continuation-armed staleness branch in `_startup_response_pending`.
- `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` (+11): parity constant + continuation guard in `_startup_input_gate_active`.
- `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py` (NEW, 5 tests).
- `platform_tests/scripts/test_session_continuation_sources_parity.py` (NEW, 1 test).
- `platform_tests/scripts/test_session_start_dispatch_core.py` (+38): `import io`, `import json`, + 4 source-reader tests.
- `platform_tests/hooks/test_workstream_focus.py` (+86): 2 Fix-b tests.

## Reconcile-Only Untracked Reader (not applied; documented follow-up)

`.claude/hooks/session-topic-envelope-router.py` is the Claude twin of the Codex `_startup_input_gate_active` reader. It is git-untracked (`.claude/` is gitignored) and is deliberately **not** in `target_paths`, so the implementation-start gate correctly refused an edit to it (out-of-authorized-scope). This is defense-in-depth only — Fix (a) prevents the continuation arm at the source, so the fix is complete and correct without it. The one-line guard to apply at reconcile (per package §6) is:

```
# WI-5083 belt-and-suspenders: a continuation-armed gate is never a genuine
# fresh-start relay window.
if str(state.get("armed_source") or "").strip().lower() in {"resume", "compact"}:
    return False
```

(inserted before the final `return` of that reader's `_startup_input_gate_active`).

## Pre-Existing Unrelated Failures (baseline stash proof)

To distinguish regressions from pre-existing drift in this shared fleet worktree, the exact WI-5083 diff was stashed (`git stash push -- <my 6 tracked files>`) and the failing checks re-run against the baseline:

- The 2 wider-suite tests (`test_startup_model_contains_role_governance_and_kpi_inventory`, `test_dashboard_and_report_are_written_with_time_series_kpi`) **failed identically** with the WI-5083 diff removed.
- The Codex hook parity check **failed with the identical 8 errors** (all about `.codex/config.toml` `[features].hooks` and `.codex/hooks.json` registrations — files this change never touches; confirmed via `git status`).

`git stash pop` then cleanly restored the WI-5083 diff. Conclusion: neither the 2 wider-suite failures nor the parity failures are caused by WI-5083; they are pre-existing baseline conditions and out of scope for this reliability-fast-lane fix.

## Requirement Sufficiency

Existing requirements sufficient. Defect fix under `GOV-RELIABILITY-FAST-LANE-001` against the existing startup-relay contract; no new requirement needed. Candidate follow-on (reviewer's call, non-blocking): a `DCL-STARTUP-GATE-FRESH-START-ONLY-001` capturing "the startup-input gate arms only on a genuinely-fresh SessionStart source."

## Owner Decisions / Input

This work depends on owner approval; authorizing evidence (carried forward from proposal -001):

- **Project-scope owner authorization:** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (reliability fast-lane standing authorization, `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`), covering WI-5083 by active project membership. The implementation-start authorization packet validated this against the live latest-GO (-003).
- **Owner task directive (2026-07-09):** run WI-5083 through the full governed bridge cycle across canonical + a Loyal Opposition counterpart. `detected_via: owner_directive`.
- **AUQ (prior worktree sessions, `detected_via: ask_user_question`):** authorized producing the verified review-ready package that is the source of the exact old→new blocks.

No new owner decision is required to verify this report.

## Prior Deliberations

- `gtkb-codex-wrapup-startup-gate-guard-sot-001` (…004) — origin of `_startup_input_gate_active` + the SoT lifecycle-guard path.
- `gtkb-loyal-opposition-startup-symmetry-001` (…010) — guard blocked-reason wording; the guard-path value finding WI-5083 preserves.
- `gtkb-startup-relay-pretooluse-read-exemption-001` (…005) — the Read/Grep/Glob exemption (why reads are exempt while shell tools are blocked).
- `gtkb-session-start-formalization-001` (…012) — the SessionStart arming machinery this fix gates.
- `gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004` — shared `session_start_dispatch_core` extraction; the parity contract respected here.

## Recommended Commit Type

Recommended commit type: fix

`fix:` — repairs broken behavior (mid-session gate re-arm blocking authorized tools) with no new capability surface. The net-new lines are almost entirely regression tests for the repaired behavior; per the Conventional Commits type discipline a test-heavy defect fix remains `fix:` (not `test:`) because its purpose is the behavior repair.

## Risk / Rollback

Blast radius: the SessionStart hot path. All changes additive and fail-soft; the only new persisted field is `armed_source` in `session-lifecycle-guard.json`, which older readers ignore. Rollback: revert the eight target_paths files. No data migration.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
