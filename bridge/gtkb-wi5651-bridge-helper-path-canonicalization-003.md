REVISED
::init gtkb lo
::open build

# WI-5651 (Fast-Lane, REVISED) — Canonicalize skill-rename stale-path probes in tracked bridge helpers

bridge_kind: prime_proposal
Document: gtkb-wi5651-bridge-helper-path-canonicalization
Version: 003
Responds to: bridge/gtkb-wi5651-bridge-helper-path-canonicalization-002.md
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

## Response to NO-GO (version 002)

- **F1 (P1) — scope integrity resolved by narrowing.** This revision scopes the change to **tracked source/template/test only** (the four `target_paths` above), all of which are `source`/`test_addition` mutations covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. The previous version's claims that install-local `.claude/skills/*` active copies would be refreshed and the temporary shim deleted *in the same change* are **removed from this proposal's committed scope and acceptance criteria**. Per owner decision (2026-07-23), the install-local active-copy refresh and shim deletion are performed as **install-local cleanup after this tracked fix is VERIFIED** — `.claude/` is git-ignored install-local by design and is not part of this committed bridge surface, so no live path outside `target_paths` is mutated by this proposal's implementation.
- **F2 (P3) — placeholder removed.** The auto-seeded `### Helper-suggested candidates` / `_No prior deliberations: <fill in reason>._` scaffold line is removed; the Prior Deliberations section below carries only reviewed, real entries.
- **Preserved:** the passing mechanical preflights and the regression-test direction from version 001 are retained; only the scope and acceptance were corrected.

## Summary

The canonical bridge skills were renamed to the `gtkb-` prefix in `.claude/skills/` (`bridge-propose` → `gtkb-bridge-propose`, `bridge` → `gtkb-bridge`, `verify` → `gtkb-verify`), but several **tracked** helpers still probe the pre-rename `.claude/skills/bridge-propose/...` and `.claude/skills/bridge/...` paths. Because those directories no longer exist at the canonical location, the helpers fail at runtime ("Governed bridge writer helper not found" / `FileNotFoundError`) while their dry-runs pass, masking a path regression as a content problem.

Confirmed tracked stale probes:

1. `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` — `_load_bridge_writer` (lines ~618-625) probes only unprefixed `bridge-propose` candidates. Root cause of the broken `gt bridge file-implementation-proposal`.
2. `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py` — loads `proposal_helper` from `bridge-propose`, `report_helper` from `bridge`, and `verify_helper` from `verify` (lines ~385-395), all pre-rename.
3. `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` — `BRIDGE_PROPOSE_HELPER` (~line 29) assigns the unprefixed `bridge-propose` path.

**Fix (single-concern, path canonicalization, tracked only):** at each probe, prefer the canonical `gtkb-` prefixed path and retain the unprefixed path as a backward-compatibility fallback (so scaffolded/unrenamed projects still resolve). Add a regression test asserting the tracked helpers reference/resolve the canonical `gtkb-` location and fails on the pre-fix code.

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

1. **Origin defect/regression** — WI-5651 origin is `regression`. ✓
2. **No new public API/CLI/behavior beyond removing the defect** — only path resolution changes; no new surface. ✓
3. **No new/revised requirement or specification.** ✓
4. **Small, single-concern** — path canonicalization across 3 tracked source/template files + 1 test; net change well under 150 lines. ✓

WI-5651 is a member of `PROJECT-GTKB-RELIABILITY-FIXES` and is covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (allowed mutation classes `source`, `test_addition`, `hook_upgrade`); all four target paths are `source` or `test` mutations within that authorization.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — the fast-lane governance path; eligibility justified above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge artifact; this REVISED is the next append-only numbered file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing spec; no phantom citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Test Plan derives an executable regression test; no VERIFIED without executed evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — governs the standing PAUTH covering this WI via project membership.
- `GOV-STANDING-BACKLOG-001` — WI-5651 is the governed backlog authority for this work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the changed helpers are shared cross-harness surfaces; the fix changes only path resolution, no hook contract or payload shape.

## Requirement Sufficiency

Existing requirements sufficient. This is a defect fix restoring the intended helper lookup to the canonical path. No new or revised requirement or specification is required before implementation.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision establishing the reliability fast-lane used by this proposal.
- `gtkb-skill-rollout` playbook — the rename-map + adapter-regeneration + stale-dir-cleanup procedure this fix aligns with; the residual stale probes are the "sweep for other stale unprefixed references" step it calls for.
- WI-5650 (VERIFIED this session, `gtkb-wi5650-pb-startup-relay-selfheal-budget-004`) — during whose report filing this defect was hit in the report helper, requiring the temporary shim that the (separate, install-local) cleanup retires.

## Test Plan (spec-derived)

| Specification | Derived test | Assertion |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / `GOV-RELIABILITY-FAST-LANE-001` | `test_governed_bridge_helper_paths_prefer_canonical_gtkb_prefix` (new, in `platform_tests/skills/test_bridge_impl_report_helper.py`) | `proposal_filing._load_bridge_writer` loads the write helper without raising; the tracked `proposal_filing.py`, `modernization/workflow.py`, and `templates/skills/bridge/helpers/impl_report_bridge.py` reference the canonical `gtkb-` prefixed skill path. Fails on the pre-fix code (which references only the unprefixed path). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | existing `platform_tests/skills/test_bridge_impl_report_helper.py` suite (with its stale `HELPER_PATH` corrected to the canonical `gtkb-bridge` path) | Full suite passes; no cross-harness or helper-contract regression. |

Commands to execute at implementation: `python -m pytest platform_tests/skills/test_bridge_impl_report_helper.py platform_tests/scripts/test_gtkb_bridge_writer.py -q`, `ruff check <changed>`, `ruff format --check <changed>`.

## Acceptance Criteria

1. Each tracked probe (`proposal_filing._load_bridge_writer`, `modernization/workflow.py` proposal/report/verify helpers, `templates/skills/bridge/helpers/impl_report_bridge.py` `BRIDGE_PROPOSE_HELPER`) prefers the canonical `gtkb-` path and keeps the unprefixed path as a backward-compatibility fallback; no live path is hard-broken.
2. A regression test pins canonical `gtkb-` resolution across the tracked helpers and fails on the pre-fix code.
3. The existing `test_bridge_impl_report_helper.py` suite (with the corrected `HELPER_PATH`) plus `ruff check` and `ruff format --check` pass.
4. Scope is tracked-only; install-local `.claude/` active-copy refresh and shim deletion are explicitly out of this committed scope and handled as install-local cleanup after VERIFY (owner decision 2026-07-23).

## Risk and Rollback

Low risk: path-resolution-only change on already-broken tracked lookups; the canonical path is confirmed present. Rollback is a `git revert` of the single commit (source + template + test).

## Owner Decisions / Input

Per GOV-RELIABILITY-FAST-LANE-001, a fast-lane fix does not require per-fix owner approval; project membership under the standing PAUTH supplies authorization. Owner directives of record: **2026-07-23, "Proceed with WI-5651 implementation, then delete the shim when you are done,"** and the **2026-07-23 scope decision** to revise tracked-only and perform the install-local active-copy refresh + shim deletion as install-local cleanup after this tracked fix VERIFIES. No blocking owner decision is requested by this proposal.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
