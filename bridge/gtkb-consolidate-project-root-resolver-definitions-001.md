NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Audit and consolidate the eight independent project-root resolver definitions across the GT-KB codebase

bridge_kind: prime_proposal
Document: gtkb-consolidate-project-root-resolver-definitions
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3354

target_paths: ["scripts/assertion_categorize.py", "scripts/assertion_retirement_workflow.py", "scripts/benchmarks/common.py", "platform_tests/scripts/test_project_root_resolver_consolidation.py"]

Implementation proposal for a bounded code or platform change.

## Claim

GT-KB has eight independent project-root resolver definitions. WI-3353 (bridge thread `gtkb-governance-hook-worktree-root-resolution`, VERIFIED) corrected the shared `groundtruth_kb/bridge/paths.py` resolver to be worktree-aware (resolve the canonical main-worktree root via `git rev-parse --git-common-dir`, plus a parent walk that skips any `.claude/worktrees/` segment) and fixed the two named governance hooks; `scripts/cross_harness_bridge_trigger.py` was fixed transitively because it delegates to `paths.py`. The other resolvers were never audited under WI-3353's scope. A read-only audit of all eight shows three still carry the worktree cwd-trust defect: `scripts/assertion_categorize.py` (`_resolve_project_root`, parent walk from `Path(__file__)` with no worktree skip and no git-common-dir step), `scripts/assertion_retirement_workflow.py` (identical pattern), and `scripts/benchmarks/common.py` (`Path(__file__).resolve().parents[2]`, which is the worktree root when the file is checked out under `.claude/worktrees/<name>/scripts/benchmarks/common.py`). In a linked-worktree session these three resolve a worktree root instead of the canonical GT-KB root, which mis-targets `.gtkb-state/...` (triage categories, retirement decisions, benchmark output) under the worktree rather than the canonical root — the same class of defect WI-3353 fixed for bridge state. This proposal consolidates the three buggy resolvers onto the WI-3353-corrected shared `groundtruth_kb.bridge.paths.resolve_project_root()` using the established import-safe delegation pattern already proven in `cross_harness_bridge_trigger.py` and `single_harness_bridge_dispatcher.py`, and adds a dedicated regression test that exercises all three corrected resolvers with the canonical worktree fixture.

## Requirement Sufficiency

Existing requirements sufficient. The required behavior — every GT-KB resolver returns the canonical host root (the directory containing `groundtruth.toml`, above any `.claude/worktrees/` segment) — is already governed by `.claude/rules/project-root-boundary.md` ("All active files for the GT-KB project MUST be within `E:\GT-KB`"; harness-local worktree scratch is non-authoritative) and was operationalized for the shared resolver by WI-3353. This fix extends that already-required behavior to three resolvers that were out of WI-3353's scope; it introduces no new public surface, no new flag, and no new or revised specification.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/assertion_categorize.py`, `scripts/assertion_retirement_workflow.py`, `scripts/benchmarks/common.py`, `platform_tests/scripts/test_project_root_resolver_consolidation.py`.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change keeps all GT-KB runtime state under the canonical GT-KB host root and honors the `.claude/worktrees/` non-authority boundary; the three buggy resolvers currently let a linked-worktree session write `.gtkb-state/...` under the worktree instead of the host root, which this fix closes. Confined to `scripts/...` and platform tests; no `applications/` surface is touched.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge-state mis-targeting class this fix removes is the same one WI-3353 (the permanent bridge-repair authority) corrected for `paths.py`; consolidating onto the corrected shared resolver preserves the canonical-root invariant that bridge/state authority depends on.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves durable artifacts (assertion-triage categories, retirement decision records, benchmark snapshots) at their canonical-root location rather than leaking copies into a transient worktree, keeping the artifact lifecycle consistent across sessions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - resolver outputs (where `.gtkb-state` artifacts land) remain anchored to the canonical artifact root, not inferred from a per-session checkout location.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns each resolver's root resolution with the canonical location that governs where lifecycle artifacts are created and read.
- `GOV-STANDING-BACKLOG-001` - WI-3354 is a standing-backlog work item (P3, origin=hygiene) under `PROJECT-GTKB-RELIABILITY-FIXES`, captured per the strategic self-improvement directive while implementing WI-3353.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the cited specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).

## Prior Deliberations

- `DELIB-2092` - Bridge thread `gtkb-governance-hook-worktree-root-resolution` (WI-3353, VERIFIED) - the precedent fix that made the shared `groundtruth_kb/bridge/paths.py` resolver worktree-aware; this proposal consolidates the three un-audited resolvers onto that same corrected resolver and reuses its approved test pattern.
- `DELIB-20264102` - Loyal Opposition Review - Worktree cwd / Project-Root Resolution in Bridge Governance - establishes the worktree cwd-trust defect class and the git-common-dir / `.claude/worktrees/`-skip remediation that this proposal extends.
- `DELIB-20264103` - Loyal Opposition Review - Worktree cwd / Project-Root Resolution in Bridge Governance (companion verdict) - confirms the canonical-root resolution approach reused here.
- `DELIB-20265457` - Owner decision (2026-06-21) directing all open `PROJECT-GTKB-RELIABILITY-FIXES` work items to bridge GO; WI-3354 is in scope for this batch.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the non-fast-lane batch project authorization covering this work; WI-3354 is an in-scope `PROJECT-GTKB-RELIABILITY-FIXES` work item, so implementation authority flows through active project membership under this PAUTH (not the fast-lane). This proposal still requires Loyal Opposition GO and a per-thread implementation-start packet before any edit.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the full PROJECT-GTKB-RELIABILITY-FIXES batch: author NEW proposals for all open work items in the project and drive them to bridge GO. WI-3354 (P3, origin=hygiene) is one of those open work items.

## Proposed Scope

Audit result (read-only classification of all eight resolvers; recorded here as the audit deliverable):

| # | Resolver | Location | Classification | Action |
|---|---|---|---|---|
| 1 | `resolve_project_root` | `groundtruth_kb/bridge/paths.py` | worktree-correct (WI-3353) | none (canonical resolver) |
| 2 | `_resolve_project_root` | `scripts/cross_harness_bridge_trigger.py` | worktree-correct (delegates to #1) | none (transitively fixed by WI-3353) |
| 3 | `_resolve_project_root` | `scripts/single_harness_bridge_dispatcher.py` | worktree-correct (delegates to #1) | none |
| 4 | `_resolve_project_root` | `scripts/single_harness_bridge_automation.py` | worktree-correct (delegates to #3 → #1) | none |
| 5 | `_resolve_project_root` | `scripts/assertion_categorize.py` | **worktree-buggy** (`__file__` parent walk, no worktree skip, no git-common-dir) | consolidate onto #1 (import-safe) |
| 6 | `_resolve_project_root` | `scripts/assertion_retirement_workflow.py` | **worktree-buggy** (same pattern) | consolidate onto #1 (import-safe) |
| 7 | `_resolve_project_root` | `scripts/benchmarks/common.py` | **worktree-buggy** (`Path(__file__).resolve().parents[2]`) | consolidate onto #1 (import-safe) |
| 8 | `_resolve_project_root` | `groundtruth_kb/reconciliation.py` | **out of scope (different abstraction)** | none this WI — see Risks |

IP blocks (the three consolidations):

1. **IP-1 — `scripts/assertion_categorize.py`.** Replace the body of `_resolve_project_root(explicit)` so that, after the explicit-arg and `GTKB_PROJECT_ROOT` checks, it delegates to `groundtruth_kb.bridge.paths.resolve_project_root()` via a lazy import inside a `try/except` (the import-safe pattern proven in `cross_harness_bridge_trigger.py` lines 315-320). The `except` fallback retains a worktree-aware parent walk: walk parents from `Path(__file__).resolve()` for `groundtruth.toml`, skipping any candidate at or below a `.claude/worktrees/` segment (mirroring `paths.py:_is_under_worktrees`). Signature, return type (`Path`), and `SystemExit`-on-failure behavior are preserved.
2. **IP-2 — `scripts/assertion_retirement_workflow.py`.** Apply the identical consolidation to its `_resolve_project_root(explicit)` (same current pattern, same delegation + worktree-aware fallback, same preserved contract).
3. **IP-3 — `scripts/benchmarks/common.py`.** In `_resolve_project_root(project_root)`, when `project_root is None`, delegate to the shared resolver (with the same import-safe + worktree-aware fallback) instead of returning `Path(__file__).resolve().parents[2]`. The explicit-arg branch (`return Path(project_root).resolve()`) is unchanged, so all benchmark call sites that pass an explicit root are unaffected.
4. **IP-4 — Regression tests.** Add `platform_tests/scripts/test_project_root_resolver_consolidation.py` (see verification plan) covering all three corrected resolvers against the canonical worktree fixture and the import-safe-fallback path.

Out-of-scope (documented, not changed): resolver #8 (`groundtruth_kb/reconciliation.py`) is a DB-driven file-resolution helper (`explicit arg → db.project_root → cwd`), not a host-root/worktree resolver; it has different semantics and consumers. Consolidating it onto `paths.py` would change its contract and is explicitly excluded from this hygiene fix.

## Specification-Derived Verification Plan

Tests reuse the canonical worktree fixture pattern from `groundtruth-kb/tests/test_bridge_paths.py` (`_build_worktree_project`: a synthetic `groundtruth.toml` checkout with a linked worktree under `.claude/worktrees/test-wt`). Each corrected resolver is loaded via `importlib` (the existing module-load pattern in `test_assertion_categorize.py`) and asserted to return the canonical root, not the worktree root.

| Spec clause | Derived test | Assertion |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (state stays under canonical host root) | `test_assertion_categorize_resolver_returns_canonical_root_from_worktree` | `assertion_categorize._resolve_project_root(None)` invoked with cwd inside a linked worktree returns the canonical checkout root, not the worktree root. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (state stays under canonical host root) | `test_assertion_retirement_resolver_returns_canonical_root_from_worktree` | `assertion_retirement_workflow._resolve_project_root(None)` from inside a linked worktree returns the canonical root. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (state stays under canonical host root) | `test_benchmarks_common_resolver_returns_canonical_root_from_worktree` | `benchmarks.common._resolve_project_root(None)` from inside a linked worktree returns the canonical root (no longer `parents[2]` = worktree root). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (consolidate onto the WI-3353-corrected shared resolver) | `test_resolvers_delegate_to_shared_paths_resolver` | When `groundtruth_kb.bridge.paths.resolve_project_root` is importable, each of the three resolvers returns a value equal to the shared resolver's result for the same cwd (delegation, not an independent walk). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (import-safe fallback for non-package consumers) | `test_resolvers_fallback_is_worktree_aware_when_package_unimportable` | With the `groundtruth_kb` import forced to fail (monkeypatched), each resolver's fallback still resolves the canonical root from a worktree cwd by skipping the `.claude/worktrees/` segment. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (explicit-arg / env contract preserved; no regression) | `test_resolvers_preserve_explicit_and_env_contract` | Explicit-arg and `GTKB_PROJECT_ROOT` paths return the configured root unchanged for all three resolvers; `benchmarks.common._resolve_project_root(explicit)` is unchanged. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_project_root_resolver_consolidation.py -q --tb=short`
- `python -m ruff check scripts/assertion_categorize.py scripts/assertion_retirement_workflow.py scripts/benchmarks/common.py platform_tests/scripts/test_project_root_resolver_consolidation.py`
- `python -m ruff format --check scripts/assertion_categorize.py scripts/assertion_retirement_workflow.py scripts/benchmarks/common.py platform_tests/scripts/test_project_root_resolver_consolidation.py`

Regression guard (must remain green; the three scripts are exercised by existing suites): `python -m pytest platform_tests/scripts/test_assertion_categorize.py platform_tests/scripts/test_assertion_retirement_workflow.py -q --tb=short`.

## Acceptance Criteria

1. From inside a linked worktree, each of `scripts/assertion_categorize.py`, `scripts/assertion_retirement_workflow.py`, and `scripts/benchmarks/common.py` resolves the canonical GT-KB host root (the `groundtruth.toml` directory above `.claude/worktrees/`), not the worktree root.
2. When `groundtruth_kb` is importable, the three resolvers delegate to `groundtruth_kb.bridge.paths.resolve_project_root()`; when it is not importable, the import-safe fallback is itself worktree-aware.
3. The explicit-arg and `GTKB_PROJECT_ROOT` contracts are preserved for all three resolvers; `benchmarks/common.py`'s explicit-arg branch is unchanged.
4. Resolvers #1-#4 (canonical + delegating) are unchanged; resolver #8 (`reconciliation.py`) is documented as out of scope and left unchanged.
5. New tests pass; existing assertion-triage suites remain green; `ruff check` and `ruff format --check` are clean on all changed files.

## Risks / Rollback

- Risk: a resolver now imports `groundtruth_kb` where it previously had no package dependency. Mitigation: the import is lazy and wrapped in `try/except`; the worktree-aware fallback preserves correct behavior when the package is unimportable, so no new hard dependency is introduced.
- Risk: the fallback walk could regress if it omitted the `.claude/worktrees/` skip (re-introducing the bug in the non-package path). Mitigation: a dedicated test (`test_resolvers_fallback_is_worktree_aware_when_package_unimportable`) forces the import to fail and asserts canonical-root resolution.
- Risk: `benchmarks/common.py` call sites depend on the `parents[2]` shape. Mitigation: the change only affects the `project_root is None` branch; all explicit-arg callers are unchanged, and the regression-guard pytest run covers the benchmark suites.
- Risk (deferred, not introduced here): resolver #8 (`reconciliation.py`) may still mis-resolve via cwd in a worktree. It is a separate abstraction with different semantics and is explicitly out of scope; if owner wants it consolidated, it should be a follow-on WI with its own contract review.
- Rollback: each IP block is an isolated function-body change plus an additive test file; revert the three function bodies and delete the new test to fully restore prior behavior. No data migration, no schema change, no config change.

## Files Expected To Change

- `scripts/assertion_categorize.py`
- `scripts/assertion_retirement_workflow.py`
- `scripts/benchmarks/common.py`
- `platform_tests/scripts/test_project_root_resolver_consolidation.py`

## Recommended Commit Type

`fix` - this removes a worktree cwd-trust defect (state mis-targeting) in three resolvers; no new capability surface is added. Diff is three guarded function-body changes plus one additive regression-test file.
