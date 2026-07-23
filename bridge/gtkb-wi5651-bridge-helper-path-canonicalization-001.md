NEW
::init gtkb lo
::open build

# WI-5651 (Fast-Lane) — Canonicalize skill-rename stale-path probes in governed bridge helpers

bridge_kind: prime_proposal
Document: gtkb-wi5651-bridge-helper-path-canonicalization
Version: 001
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

## Summary

The canonical bridge-related skills were renamed to the `gtkb-` prefix (`bridge-propose` → `gtkb-bridge-propose`, `bridge` → `gtkb-bridge`), but several governed helpers still probe the **pre-rename** `.claude/skills/bridge-propose/...` and `.claude/skills/bridge/...` paths. Because the pre-rename directories no longer exist, these helpers fail at runtime with "Governed bridge writer helper not found" (proposal filing) or `FileNotFoundError` (post-impl report filing) — while their dry-runs succeed, so the breakage masquerades as a content/preflight problem rather than a path regression.

Confirmed stale probes (all point at directories that no longer exist; canonical is the `gtkb-` prefixed sibling):

1. `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` — `_load_bridge_writer` (lines ~618-625) probes only two unprefixed `bridge-propose/helpers/write_bridge.py` candidates. This breaks `gt bridge file-implementation-proposal` for all callers (WI-5651 root cause).
2. `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py` — the modernization runner loads its `proposal_helper` from `.claude/skills/bridge-propose/helpers/write_bridge.py` (~line 386) and its `report_helper` from `.claude/skills/bridge/helpers/impl_report_bridge.py` (~line 390), both pre-rename.
3. `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` — `BRIDGE_PROPOSE_HELPER` (~line 29) points at the unprefixed `bridge-propose/helpers/write_bridge.py`; this breaks the post-impl report filer (the WI-5650 report filing this session hit exactly this and required a local compatibility shim to proceed).

**Fix (single concern, path canonicalization):** at each probe, prefer the canonical `gtkb-`-prefixed path and retain the unprefixed path as a backward-compatibility fallback (per the WI-5651 candidate fix and the `gtkb-skill-rollout` playbook). For single-path constants/assignments, resolve via a small "prefer gtkb-, fall back to unprefixed" helper so no live path is hard-broken. Add a regression test pinning that each governed helper resolves the canonical `gtkb-` location.

The active `.claude/skills/*` copies (git-ignored, install-local) are re-derived from these tracked templates/sources; the tracked fix here is authoritative, and the local active copies are updated in the same change so the current install stops depending on the temporary shim.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

1. **Origin defect/regression** — WI-5651 origin is `regression` (skill-rename left stale probes). ✓
2. **No new public API/CLI/behavior beyond removing the defect** — only restores the pre-rename lookup to the canonical path; no new surface. ✓
3. **No new/revised requirement or specification** — none. ✓
4. **Small, single-concern** — path canonicalization across ~3 source files + 1 test; net change well under 150 lines (a few added candidate paths + one resolver + one test). ✓

WI-5651 is a member of `PROJECT-GTKB-RELIABILITY-FIXES` (attached this session), so it is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active project membership; no per-fix deliberation, per-fix PAUTH, or per-fix formal-artifact-approval packet is required. All bridge-review and safety gates are preserved.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — the fast-lane governance path this proposal uses; eligibility justified above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge artifact; filed as the append-only `-001` numbered file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing spec; no phantom citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Test Plan derives an executable regression test; no VERIFIED without executed evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — governs the standing PAUTH covering this WI via project membership.
- `GOV-STANDING-BACKLOG-001` — WI-5651 is the governed backlog authority for this work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the changed helpers are shared cross-harness surfaces; the fix changes only path resolution, no hook contract or payload shape.

## Requirement Sufficiency

Existing requirements sufficient. This is a defect fix restoring the intended (pre-rename) helper lookup to the canonical path. No new or revised requirement or specification is required before implementation.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision establishing the reliability fast-lane this proposal uses.
- `gtkb-skill-rollout` playbook — the rename-map + adapter-regeneration + stale-dir-cleanup procedure that this fix aligns with; the residual stale probes are exactly the "sweep for other stale unprefixed references" step the rollout calls for.
- WI-5650 (VERIFIED this session, `gtkb-wi5650-pb-startup-relay-selfheal-budget-004`) — during whose report filing this defect was hit in `impl_report_bridge.py`, requiring the temporary shim that this fix retires.

_No further prior deliberations found for this specific path-canonicalization defect._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Test Plan (spec-derived)

| Specification | Derived test | Assertion |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / `GOV-RELIABILITY-FAST-LANE-001` | `test_governed_helper_paths_resolve_canonical_gtkb_prefix` (new, in `platform_tests/skills/test_bridge_impl_report_helper.py`) | `proposal_filing._load_bridge_writer` returns a module without raising when only the `gtkb-`-prefixed helper exists; `impl_report_bridge.BRIDGE_PROPOSE_HELPER` (or its resolver) resolves to an existing file; the modernization workflow helper paths resolve to existing files. Regression fails on the pre-fix code. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | existing `platform_tests/skills/test_bridge_impl_report_helper.py` + `platform_tests/scripts/test_gtkb_bridge_writer.py` suites | Full suites pass; no cross-harness or writer-contract regression. |

Commands to execute at implementation: `python -m pytest platform_tests/skills/test_bridge_impl_report_helper.py platform_tests/scripts/test_gtkb_bridge_writer.py -q`, `ruff check <changed>`, `ruff format --check <changed>`.

## Acceptance Criteria

1. `gt bridge file-implementation-proposal` and the post-impl report filer resolve the governed write/report helpers at the canonical `gtkb-`-prefixed path with the temporary shim removed.
2. Each fixed probe retains the unprefixed path as a backward-compatibility fallback (no live path hard-broken).
3. A regression test pins canonical `gtkb-` path resolution and fails on the pre-fix code.
4. No new API/CLI/behavior; full targeted suites + ruff check + ruff format --check pass.

## Risk and Rollback

Low risk: path-resolution-only change on already-broken lookups; the canonical path is confirmed present and functional. Rollback is a `git revert` of the single commit (source + template + test). The active `.claude/` copies are re-derivable from the tracked templates.

## Owner Decisions / Input

Per GOV-RELIABILITY-FAST-LANE-001, a fast-lane fix does not require per-fix owner approval; project membership under the standing PAUTH supplies authorization. The owner directive of record for undertaking this work now: **owner instruction 2026-07-23, "Proceed with WI-5651 implementation, then delete the shim when you are done."** No blocking owner decision is requested by this proposal.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
