NEW

# WI-5413: Align retained compatibility surfaces with the dispatcher daemon

bridge_kind: prime_proposal
Document: gtkb-wi5413-dispatcher-daemon-terminology-cleanup
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5413

target_paths: ["groundtruth-kb/src/groundtruth_kb/bootstrap.py", "groundtruth-kb/src/groundtruth_kb/bridge/__init__.py", "groundtruth-kb/src/groundtruth_kb/bridge/handshake.py", "groundtruth-kb/src/groundtruth_kb/bridge/launcher.py", "groundtruth-kb/src/groundtruth_kb/bridge/paths.py", "groundtruth-kb/src/groundtruth_kb/bridge/registry.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt the exact semantic terminology patches already present in eight retained
compatibility/source surfaces. They replace obsolete claims that bridge dispatch
is driven by cross-harness PostToolUse/Stop hooks with the current dispatcher
daemon architecture. Runtime control flow, bridge routing, dispatcher state,
harness eligibility, legacy import compatibility, and archive history remain
unchanged; only module documentation and bootstrap guidance change.

The raw `bridge/launcher.py` worktree diff is inflated by unrelated line-ending
churn. Implementation and finalization are therefore authorized only for the
stable whitespace-insensitive semantic patch identities listed below. Whole-file
attribution, staging, or commit of any target is prohibited. The current source
bytes remain foreign until independent GO plus matching implementation-start
authority permits adoption, and any later commit still requires independent
post-implementation VERIFIED and exact mechanical Git authority.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - establishes the persistent dispatcher daemon as the active dispatch owner and removes harness hooks from the control plane.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires active operational guidance to point to the centralized dispatcher service.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - prohibits guidance that implies harness-triggered dispatch or harness control over routing.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the terminology correction to preserve runtime behavior, compatibility imports, and essential operational context.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact ownership and report-first treatment of the foreign dirty hunks before finalization.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - requires fail-closed hunk identity and exact mechanical authority before any scoped commit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO/start and post-implementation VERIFIED through the append-only bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds all eight exact targets to their governing architecture and non-impairment requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5413 to the active tree-stabilization project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent execution of the specification-derived behavior, wording, lint, and patch-identity checks before VERIFIED.

## Prior Deliberations

- `DELIB-20265882` and `DELIB-20265888` - owner decisions that dispatch is a GT-KB-owned black-box service and harnesses are consumers rather than triggers or routers.
- `DELIB-20266084` and `DELIB-20266272` - owner decisions authorizing the dispatcher-daemon foundation and full daemon go-live.
- `DELIB-20266276` - owner scope-lock for daemon resilience while preserving single-owner dispatcher control.

WI-5413 does not redesign those decisions. It removes stale descriptive residue
from compatibility surfaces so generated guidance and source documentation no
longer describe the retired hook-trigger architecture as active.

## Owner Decisions / Input

No additional owner decision is required. The owner authorized the full
modernization and tree-stabilization programs at project scope, directed every
dirty scope to receive explicit ownership, and prohibited solving console or
dispatch defects by impairing harness dispatchability. Active authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` covers source,
test evidence, documentation, and governance evidence while retaining the
independent GO/start, VERIFIED, and mechanical Git gates.

## Requirement Sufficiency

Existing requirements sufficient. The dispatcher architecture, centralized
service contract, harness-isolation invariant, modernization non-impairment
rule, worktree hygiene rule, and governed finalization requirements fully
define the expected terminology and preservation behavior. No requirement
change is proposed.

## Spec-Derived Verification Plan

`ADR-DISPATCHER-ARCHITECTURE-001`,
`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and
`DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` map to retained bridge,
mode-switch, MCP boundary, retired-poller wording, and doctor tests. Expected
result: 65 passed and 2 deselected. The two deselections are the independently
tracked in-root-basetemp fixture defect WI-5419; no terminology assertion is
excluded.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_paths.py groundtruth-kb/tests/test_bridge_launcher.py groundtruth-kb/tests/test_bridge_registry.py groundtruth-kb/tests/test_bridge_handshake.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py groundtruth-kb/tests/test_mcp_surface_foundation.py::test_t2_assert_in_root_accepts_in_root_paths groundtruth-kb/tests/test_mcp_surface_foundation.py::test_t3_assert_in_root_rejects_out_of_root_paths groundtruth-kb/tests/test_mcp_surface_foundation.py::test_t4_assert_in_root_rejects_traversal_attempts groundtruth-kb/tests/test_mcp_surface_foundation.py::test_t5_resolve_safe_path_resolves_relative_to_root platform_tests/test_no_active_smart_poller_wording.py groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py -q --tb=short --timeout=600 -k "not test_resolve_project_root_raises_when_no_marker_found and not test_resolve_project_root_rejects_git_repo_without_groundtruth_toml"
```

The user-facing bootstrap wording maps to the desktop-bootstrap CLI tests.
Expected result: 3 passed.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli.py::TestBootstrapDesktop -q --tb=short --timeout=600
```

`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and worktree hygiene map to lint,
format, whitespace, exact semantic diff inspection, and stable patch identity.
Expected result: all checks clean; the whitespace-insensitive semantic diff is
25 additions and 35 removals; combined stable patch id is
`fc3e8fdfef9d37b2b4b76d0914fdd8bd79336e83`.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/src/groundtruth_kb/bridge/__init__.py groundtruth-kb/src/groundtruth_kb/bridge/handshake.py groundtruth-kb/src/groundtruth_kb/bridge/launcher.py groundtruth-kb/src/groundtruth_kb/bridge/paths.py groundtruth-kb/src/groundtruth_kb/bridge/registry.py groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/src/groundtruth_kb/bridge/__init__.py groundtruth-kb/src/groundtruth_kb/bridge/handshake.py groundtruth-kb/src/groundtruth_kb/bridge/launcher.py groundtruth-kb/src/groundtruth_kb/bridge/paths.py groundtruth-kb/src/groundtruth_kb/bridge/registry.py groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/src/groundtruth_kb/bridge/__init__.py groundtruth-kb/src/groundtruth_kb/bridge/handshake.py groundtruth-kb/src/groundtruth_kb/bridge/launcher.py groundtruth-kb/src/groundtruth_kb/bridge/paths.py groundtruth-kb/src/groundtruth_kb/bridge/registry.py groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py
git diff --ignore-space-at-eol --no-ext-diff --no-color -- groundtruth-kb/src/groundtruth_kb/bootstrap.py groundtruth-kb/src/groundtruth_kb/bridge/__init__.py groundtruth-kb/src/groundtruth_kb/bridge/handshake.py groundtruth-kb/src/groundtruth_kb/bridge/launcher.py groundtruth-kb/src/groundtruth_kb/bridge/paths.py groundtruth-kb/src/groundtruth_kb/bridge/registry.py groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py | git patch-id --stable
```

Per-file stable patch identities:

| Path | Patch id |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/bootstrap.py` | `1f449f7df485d485d7406ae8e136ce5a5b9b62f7` |
| `groundtruth-kb/src/groundtruth_kb/bridge/__init__.py` | `724d285748ccc80f3b948c9e96b1f2c0528f843e` |
| `groundtruth-kb/src/groundtruth_kb/bridge/handshake.py` | `11f84bf0229d7503813d0603a34b69b18fbeacf1` |
| `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py` | `c9e9a363bc7a3e91ea76cf99d263425f02ff4299` |
| `groundtruth-kb/src/groundtruth_kb/bridge/paths.py` | `0cc435fcde021b89f0536031722ef6db050ff999` |
| `groundtruth-kb/src/groundtruth_kb/bridge/registry.py` | `a2d557cc12f0abe7d908d2e1e7b09d3d9297be5b` |
| `groundtruth-kb/src/groundtruth_kb/mcp_surface/boundary.py` | `8737bc81d27698c1b6cc898e53c57b84953be5db` |
| `groundtruth-kb/src/groundtruth_kb/mode_switch/pending.py` | `5cfa8d6c0fca8655b504e54378c05cf30b69faf0` |

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires independent LO to
rerun every command, inspect the semantic diff, and confirm that line-ending
noise is excluded before issuing VERIFIED.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5413 tree-stabilization ownership of pre-existing dispatcher-daemon terminology patches",
  "canonical_authority": "ADR-DISPATCHER-ARCHITECTURE-001 and SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
  "primary_route": "the dispatcher daemon and governed gt bridge dispatch CLI surfaces",
  "before_behavior": "retained modules and generated bootstrap guidance describe the retired cross-harness hook trigger as the active dispatch mechanism",
  "after_behavior": "the same compatibility surfaces identify the dispatcher daemon as active while preserving all runtime behavior and legacy imports",
  "self_descriptive_naming": "dispatcher daemon replaces cross-harness event-driven trigger and PostToolUse/Stop hook wording consistently",
  "obsolete_guidance_disposition": "retired trigger guidance is removed from current-facing prose while archive paths and compatibility history remain explicit",
  "history_preservation": "legacy modules, archive references, bridge history, and compatibility contracts remain intact and importable",
  "baseline": {
    "semantic_patch_id": "fc3e8fdfef9d37b2b4b76d0914fdd8bd79336e83",
    "semantic_diff": "25 additions and 35 removals",
    "focused_tests": "65 passed, 2 deselected for WI-5419; desktop bootstrap 3 passed"
  },
  "expected_result": {
    "active_dispatch_wording": "dispatcher daemon",
    "retired_active_wording": "absent from the eight current-facing semantic patches",
    "runtime_control_flow": "unchanged"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the later focused semantic-hunk commit without amending history or absorbing line-ending churn",
    "test": "rerun the 65-test focused lane, desktop bootstrap class, Ruff, whitespace, and stable patch-id checks"
  },
  "hard_invariants": [
    "no bridge, dispatcher, TAFE, harness, eligibility, lease, credential, deployment, release, or runtime-state mutation",
    "no runtime control-flow or legacy import change",
    "no whole-file attribution or finalization of bridge/launcher.py or any other target",
    "all foreign non-semantic bytes remain untouched"
  ],
  "fail_closed_conditions": [
    "any combined or per-file semantic patch id differs",
    "any target contains unrelated semantic hunks",
    "any specified test, lint, format, whitespace, or wording check fails",
    "implementation-start or independent VERIFIED authority is absent or mismatched"
  ],
  "essential_context_preservation": "active daemon guidance, retired-substrate history, compatibility imports, in-root state semantics, and concurrent worktree ownership all remain visible and intact"
}
```

## Risk / Rollback

Risk is low but not zero: inaccurate replacement text could obscure the retained
legacy/runtime boundary, and careless whole-file handling could absorb newline
or concurrent changes. Stable semantic patch identities, focused compatibility
tests, and a hunk-only finalizer constrain both risks. Under separate exact
mechanical authority, finalization should be one focused `fix` commit containing
only the eight reviewed semantic patches. Rollback is a separately governed
revert of that exact commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5413-dispatcher-daemon-terminology-cleanup`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - removes stale operational guidance that points adopters and maintainers
at a retired dispatch mechanism while preserving runtime behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
