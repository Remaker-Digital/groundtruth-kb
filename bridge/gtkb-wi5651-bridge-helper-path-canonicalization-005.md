NEW
::init gtkb lo
::open build

# WI-5651 (Fast-Lane) — Implementation Report: Canonicalize skill-rename stale-path probes in tracked bridge helpers

bridge_kind: implementation_report
Document: gtkb-wi5651-bridge-helper-path-canonicalization
Version: 005
Responds to: bridge/gtkb-wi5651-bridge-helper-path-canonicalization-004.md
Date: 2026-07-23 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 09e8949e-b3d4-42a0-b175-adf28dc87b17
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (session envelope established for 09e8949e); explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5651

Recommended commit type: fix:

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]

## Implementation Commit

`d8926a8f fix(bridge-tooling): canonicalize skill-rename stale-path probes in tracked bridge helpers (WI-5651)` — 4 files changed, +76 / −5. Committed through the governed `python -m groundtruth_kb.git_lifecycle` path (pathspec-limited to the four `target_paths` only; the unrelated emergency-bootstrap taxonomy edit and all other concurrent working-tree changes were excluded). Pre-commit gates passed: narrative-artifact evidence (no protected paths in staged set), ruff format (4 staged files formatted), protected-commit authorization (3 protected paths cleared). This report requests VERIFIED against that commit.

## Summary of Implementation

Each tracked probe now prefers the canonical `gtkb-`-prefixed skill path and retains the unprefixed pre-rename path as a backward-compatibility fallback, so renamed installs resolve correctly while scaffolded/unrenamed projects still work:

1. `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` — `_load_bridge_writer` now prepends the two `gtkb-bridge-propose` candidates ahead of the unprefixed `bridge-propose` candidates.
2. `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py` — added `_resolve_platform_helper(platform_root, *relative_candidates)` (prefers the `gtkb-`-prefixed relative path, falls back to the unprefixed one) and routed `proposal_helper` (`gtkb-bridge-propose`), `report_helper` (`gtkb-bridge`), and `verify_helper` (`gtkb-verify`) through it.
3. `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` — replaced the hard-coded `BRIDGE_PROPOSE_HELPER = …` unprefixed assignment with `_resolve_bridge_propose_helper(root)` (prefer `gtkb-bridge-propose`, fall back to `bridge-propose`) and set `BRIDGE_PROPOSE_HELPER = _resolve_bridge_propose_helper(PROJECT_ROOT)`.
4. `platform_tests/skills/test_bridge_impl_report_helper.py` — corrected the stale `HELPER_PATH` to resolve the canonical `gtkb-bridge` helper via `_resolve_repo_helper(...)`, and added `test_governed_bridge_helper_paths_prefer_canonical_gtkb_prefix`.

## Specification Links (carried forward from -003 / -004)

- `GOV-RELIABILITY-FAST-LANE-001` — the fast-lane governance path; WI-5651 origin `regression`, small single-concern, no new requirement/surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is the next append-only numbered bridge file in the thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all governing specs carried forward; no phantom citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below with executed evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-5651 via project membership; mutation classes `source` + `test_addition`.
- `GOV-STANDING-BACKLOG-001` — WI-5651 is the governed backlog authority for this work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the changed helpers are shared cross-harness surfaces; the fix changes only path resolution, no hook contract or payload shape.

## Spec-to-Test Mapping

| Specification | Derived test | Assertion | Result |
|---|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / `GOV-RELIABILITY-FAST-LANE-001` | `test_governed_bridge_helper_paths_prefer_canonical_gtkb_prefix` (new, in `platform_tests/skills/test_bridge_impl_report_helper.py`) | `proposal_filing._load_bridge_writer(REPO_ROOT)` returns a module exposing `propose_bridge` without raising, and the three tracked helper sources (`proposal_filing.py`, `modernization/workflow.py`, `templates/skills/bridge/helpers/impl_report_bridge.py`) all reference the canonical `gtkb-bridge-propose` path. Proves canonical preference rather than mere either-path existence (per the -004 residual-risk note). | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | existing `platform_tests/skills/test_bridge_impl_report_helper.py` suite (with corrected `HELPER_PATH`) + `platform_tests/scripts/test_gtkb_bridge_writer.py` | Full suite passes; no cross-harness / helper-contract regression. | PASS (53 passed) |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_bridge_impl_report_helper.py platform_tests/scripts/test_gtkb_bridge_writer.py -q
groundtruth-kb/.venv/Scripts/ruff.exe check <4 target_paths>
groundtruth-kb/.venv/Scripts/ruff.exe format --check <4 target_paths>
```

## Observed Results

- pytest: `53 passed, 1 warning in 263.12s` (the pre-existing `asyncio_mode` config warning only).
- ruff check: `All checks passed!`
- ruff format --check: `4 files already formatted`.

## Acceptance Criteria Check

1. Each tracked probe prefers the canonical `gtkb-` path with the unprefixed path as fallback; no live path hard-broken. — **MET** (items 1–4 above; fallback retained).
2. A regression test pins canonical `gtkb-` resolution across the tracked helpers and fails on the pre-fix code. — **MET** (`test_governed_bridge_helper_paths_prefer_canonical_gtkb_prefix`; the pre-fix sources referenced only the unprefixed path, so the assertion on all three sources fails pre-fix).
3. The existing suite (with corrected `HELPER_PATH`) + `ruff check` + `ruff format --check` pass. — **MET** (53 passed; ruff clean).
4. Scope tracked-only; install-local `.claude/` active-copy refresh and shim deletion explicitly out of committed scope, handled as install-local cleanup after VERIFY. — **MET** (commit `d8926a8f` touched only the four tracked `target_paths`; no `.claude/` mutation).

## Risk and Rollback

Low risk: path-resolution-only change on already-broken tracked lookups; the canonical path is confirmed present, and the unprefixed fallback preserves scaffolded/unrenamed-project resolution. Rollback is a `git revert` of the single commit `d8926a8f`.

## Owner Decisions / Input

Per `GOV-RELIABILITY-FAST-LANE-001`, a fast-lane fix does not require per-fix owner approval; project membership under the standing PAUTH supplies authorization. Owner directives of record: **2026-07-23, "Proceed with WI-5651 implementation, then delete the shim when you are done,"** and the **2026-07-23 scope decision** to revise tracked-only and perform the install-local active-copy refresh + shim deletion as install-local cleanup after this tracked fix VERIFIES. No blocking owner decision is requested by this report.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
