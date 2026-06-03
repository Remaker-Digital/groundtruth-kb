NEW

# Implementation Report — Per-Session Pytest Basetemp Isolation (WI-3469)

bridge_kind: implementation_report
Document: gtkb-pytest-basetemp-session-isolation
Version: 003
Responds to: bridge/gtkb-pytest-basetemp-session-isolation-002.md (GO)
Author: Prime Builder (Claude, harness B; durable PB per harness-registry.json; session-stated PB via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: fix

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 45299969-65c1-495e-b4a7-1cecaa373ae1
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder]); /loop dynamic-mode iteration 6

Implements: WI-3469
Project Authorization: PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-3469
target_paths: ["conftest.py", "platform_tests/scripts/test_pytest_basetemp_isolation.py"]

## Summary

The GO `-002` (Codex, 2026-06-01) authorized WI-3469: a root `conftest.py` `pytest_configure` hook that roots pytest's basetemp at a per-process-unique leaf under the in-root `.pytest-tmp/` parent when no explicit `--basetemp` was given, eliminating parallel-session ACL contamination. This report records the completed implementation, the executed tests, the code-quality gates, and one verification-discovered robustness improvement.

Both new files are within the two GO-approved target paths. No `pyproject.toml`, subtree conftest, ad-hoc `--basetemp` invocation, or runtime temp content was modified.

**Bridge-INDEX recovery note:** like the sibling dashboard thread, this GO'd thread had been pruned from the ~1471-line `bridge/INDEX.md` before implementation, stranding a valid GO from session `86d7f8a9`. This session re-promoted the entry (`GO: -002`, `NEW: -001`) to the top of the live INDEX before minting the implementation-start packet, then prepended this report's `NEW: -003` line. Append-only preserved.

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-pytest-basetemp-session-isolation
```

Observed: `latest_status: GO`; `packet_hash: sha256:a62090011bf289975af5df145a054e7508e0738d209541d19791fc2a45c7736f`; PAUTH `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001` active, `work_item_id: WI-3469`, `requirement_sufficiency: sufficient`.

## IP-1 — Root `conftest.py` (per-session basetemp isolation)

A new configuration-only `conftest.py` at the project root:

- `pytest_configure(config)` — when `config.option.basetemp` is falsy (no explicit `--basetemp`), sets it to a per-process-unique leaf and returns; **no-op** when an explicit basetemp was supplied, preserving every existing ad-hoc `--basetemp` invocation.
- `_session_basetemp_leaf(project_root)` — returns `<project_root>/.pytest-tmp/session-<pid>-<token>`, namespaced by `os.getpid()` (disjoins parallel sessions, which are separate OS processes) plus `os.urandom(3).hex()` (guards against PID reuse across sequential runs).

The conftest defines no fixtures, markers, or collection hooks, so it cannot change which tests run or how they assert. It imports only `os` and `pathlib` (no application code), consistent with the shielding pattern at `platform_tests/scripts/conftest.py`.

### Verification-discovered robustness improvement (eager leaf creation)

The proposal's IP-1 described creating the **parent** (`leaf.parent.mkdir(parents=True, exist_ok=True)`) and then assigning the leaf. During live verification I observed that this is unsafe when the in-root `.pytest-tmp/` parent already exists but is **ACL-contaminated** by a prior crashed/concurrent run: `parent.mkdir(exist_ok=True)` no-ops on the existing (locked) directory, so the hook commits basetemp to a leaf under a poisoned parent, and the `PermissionError` then surfaces **later** during pytest fixture setup — a hard suite failure rather than a graceful fallback.

The implemented hook therefore creates the **leaf** eagerly (`leaf.mkdir(parents=True, exist_ok=True)` — `parents=True` still creates the in-root parent when absent). If the parent is unwritable this raises at `pytest_configure` time, is caught by the surrounding `except OSError`, and the hook falls back to pytest's default basetemp. This is strictly better than the proposal's parent-only creation (graceful fallback vs. deferred hard failure) and preserves the GO's observable contract (no-op when explicit; in-root per-session leaf otherwise). The `except OSError` defensive wrap is itself required because a root conftest that raised in `pytest_configure` would break the entire suite.

This robustness change was **demonstrated live**: the platform test `platform_tests/scripts/test_active_session_heartbeat.py::test_heartbeat_session_start_creates_lock` ERRORED with `PermissionError: [WinError 5] Access is denied: 'E:\GT-KB\.pytest-tmp\session-...'` under the parent-only version, and PASSES under the eager-leaf version (graceful fallback to OS temp when `.pytest-tmp/` is poisoned).

## IP-2 — Regression Tests (`platform_tests/scripts/test_pytest_basetemp_isolation.py`)

8 tests, loading the root conftest via `importlib` and exercising the hook with lightweight config doubles (no nested pytest processes):

- `test_root_conftest_exists` — the root conftest is present.
- `test_session_leaf_name_encodes_pid_under_inroot_parent` — pure path: leaf is `<root>/.pytest-tmp/session-<pid>-<token>`.
- `test_hook_sets_and_creates_basetemp_when_unset` — success path on a **clean** tmp_path-rooted leaf (deterministic regardless of the real `.pytest-tmp/` ACL state); asserts basetemp set to the leaf and the leaf eagerly created.
- `test_hook_is_noop_when_basetemp_already_set` — explicit basetemp preserved unchanged.
- `test_two_sessions_get_distinct_nonnesting_leaves` — two calls yield distinct, non-nesting sibling leaves under the same in-root parent.
- `test_distinct_pids_yield_distinct_leaves` — monkeypatched distinct PIDs yield distinct non-nesting leaves.
- `test_computed_parent_resolves_inside_project_root` — the leaf resolves inside the project root (root-boundary).
- `test_hook_falls_back_gracefully_when_parent_unwritable` — a simulated ACL-contaminated parent (monkeypatched `Path.mkdir` raising `PermissionError`) leaves basetemp unset, no exception (the robustness path above).

## Specification Links

Carried forward from `-001`; all governing specifications cited concretely.

- `WI-3469` — the originating defect (`origin=defect`): reclaim `.pytest-tmp/` from ACL contamination by parallel-session python processes.
- `GOV-RELIABILITY-FAST-LANE-001` — governs small single-concern defect fixes with no new behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the basetemp parent is the in-root `.pytest-tmp/`; no out-of-root path is written (test asserts the computed parent resolves inside the project root).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; `bridge/INDEX.md` canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification is cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specifications and executed (spec-to-test mapping below).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the fix is preserved as durable artifacts (proposal, report) traceable to WI-3469.

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-2548` (S381 owner decision) — authorizes WI-3469 for implementation through normal bridge review; operationalized as `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001`.
- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` — the S377 broad-pytest verification waiver caused by 13 parallel-contamination failures; the direct motivation for this structural fix.
- Bridge thread `gtkb-cross-harness-trigger-import-repair-001` — structural exemplar for a single-concern reliability defect fix under a project authorization.

## Owner Decisions / Input

No owner decision required before VERIFIED. The dedicated `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001` (owner decision `DELIB-2548`, S381) authorizes the bounded scope with allowed mutation classes `["source", "test_addition", "hook_upgrade"]`, which cover the new root `conftest.py` (source + hook_upgrade) and the new regression test (test_addition). No formal-artifact-approval packet is required (no GOV/SPEC/PB/ADR/DCL artifact created, no protected narrative file touched). Codex confirmed "Owner Action Required" is not raised in `-002`.

## Spec-To-Test Mapping

Executed spec-derived verification per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec / governing surface | Verification | Test / Evidence | Observed |
|---|---|---|---|
| GOV-RELIABILITY-FAST-LANE-001 (defect removal; no-op when explicit) | hook sets in-root per-session leaf when unset; no-op when `--basetemp` given | `test_hook_sets_and_creates_basetemp_when_unset`, `test_hook_is_noop_when_basetemp_already_set` | PASS |
| WI-3469 (parallel-session contamination removed) | two sessions get distinct, non-nesting leaves (token + PID) | `test_two_sessions_get_distinct_nonnesting_leaves`, `test_distinct_pids_yield_distinct_leaves` | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root) | computed parent resolves inside `E:\GT-KB` | `test_computed_parent_resolves_inside_project_root`, `test_session_leaf_name_encodes_pid_under_inroot_parent` | PASS |
| WI-3469 (graceful degradation on poisoned parent) | unwritable parent → fall back, no hard failure | `test_hook_falls_back_gracefully_when_parent_unwritable`; live `test_heartbeat...` now PASS (was ERROR) | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries executed commands + results | this section | satisfied |
| GOV-FILE-BRIDGE-AUTHORITY-001 | bridge-reviewed; INDEX canonical | INDEX re-promotion + this report | satisfied |

## Executed Verification Commands + Observed Results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_pytest_basetemp_isolation.py -q --tb=short -p no:cacheprovider
# 8 passed in 0.10s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check conftest.py platform_tests/scripts/test_pytest_basetemp_isolation.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check conftest.py platform_tests/scripts/test_pytest_basetemp_isolation.py
# 2 files already formatted

# Mechanism proof (isolated scratch project with a copy of the hook, clean parent):
#   tmp_path landed at <scratch>/.pytest-tmp/session-70088-b043ca/test_...0  (leaf created)
# Graceful-fallback proof (real in-root .pytest-tmp/ ACL-poisoned by concurrent runs):
#   platform_tests/scripts/test_active_session_heartbeat.py -> 8 passed (was ERROR pre-hardening)
```

Both code-quality gates (lint AND format) were run separately per `.claude/rules/file-bridge-protocol.md` § Pre-File Code-Quality Gates.

## Applicability + Clause Preflights

To be re-run by Loyal Opposition against `-003`. At proposal time (`-002`) the applicability preflight passed with no missing required specs and the clause preflight reported 0 blocking gaps; this report carries forward the same spec set plus the executed test evidence.

## Observations (Not in Scope; for the reviewer's record)

1. **Pre-existing poisoned temp parents.** The in-root `.pytest-tmp/` (and several `.pytest_tmp_lo*` siblings) are currently ACL-contaminated by prior concurrent Codex/Claude runs this session — `ls`, `mkdir`, and `Get-Acl` all return Access Denied, and removal needs an elevated context. Per the proposal's Out-Of-Scope, cleaning previously-accumulated `.pytest-tmp/` content is not part of this defect fix. The hardened hook degrades around them (fallback to OS temp), so they do not block the suite; per-session in-root isolation activates once `.pytest-tmp/` is writable.
2. **Shared-parent residual risk.** The GO'd design namespaces per-session **leaves** under a shared `.pytest-tmp/` parent. If the parent itself is poisoned, isolation degrades to the OS-temp fallback rather than activating. A stronger design (per-session parent, or a writability self-heal that relocates the parent) would remove this residual; it is beyond WI-3469's single-concern scope and is offered as a candidate follow-on, not implemented here.
3. **INDEX pruning strands GOs.** This is the second stranded GO from session `86d7f8a9` (2026-06-01) recovered this iteration (the first was the dashboard launcher fix, now VERIFIED). The ~1471-line `bridge/INDEX.md` is pruning still-actionable GOs before implementation — a hygiene defect worth a backlog item (INDEX maintenance should not drop entries whose latest status is an un-implemented GO).

## Acceptance Criteria Status

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] Root `conftest.py` sets a per-PID in-root leaf when no explicit `--basetemp` — test covered.
- [x] No-op when explicit `--basetemp` supplied — test covered.
- [x] Two simulated sessions receive distinct non-nesting leaves — test covered.
- [x] Computed parent resolves inside `E:\GT-KB` — test covered.
- [x] No change to `pyproject.toml`, subtree conftests, or `.gitignore`.
- [x] `ruff check` and `ruff format --check` pass on both files.
- [x] This report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED (pending this report's review).

## Files Changed

- `conftest.py` (new, project root) — `pytest_configure` per-session basetemp hook + `_session_basetemp_leaf` helper; eager leaf creation with graceful `OSError` fallback.
- `platform_tests/scripts/test_pytest_basetemp_isolation.py` (new) — 8 regression tests.
- `bridge/INDEX.md` — re-promoted the pruned thread entry; prepended `NEW: -003`.

## Bridge INDEX Update Evidence

The `gtkb-pytest-basetemp-session-isolation` entry was re-promoted to the top of `bridge/INDEX.md` with its true prior state (`GO: -002`, `NEW: -001`), then `NEW: bridge/gtkb-pytest-basetemp-session-isolation-003.md` prepended. Append-only preserved; `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs the parallel-session temp-directory contamination defect with no new capability surface; net diff is two new files (the configuration-only conftest hook plus its regression tests).

## Next Steps for Loyal Opposition

Verify this report against GO `-002`. Re-run the applicability + clause preflights against `-003`, the isolation test file, and both ruff gates. Note the documented eager-leaf robustness improvement over the proposal's parent-only creation (graceful fallback vs. deferred hard failure) and confirm it stays within the GO's contract.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
