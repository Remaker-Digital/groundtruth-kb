NEW

# gtkb-wi5419-in-root-root-resolution-fixture (Slice 1) - Isolate negative root-resolution fixtures in-root

bridge_kind: prime_proposal
Document: gtkb-wi5419-in-root-root-resolution-fixture
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5419

target_paths: ["groundtruth-kb/tests/test_bridge_paths.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair two environment-sensitive negative tests in
`groundtruth-kb/tests/test_bridge_paths.py` without changing production root
resolution. Add a test-local helper that monkeypatches the existing private
`_has_marker` predicate so only markers at or below the named synthetic fixture
root are visible. Apply it to the empty-directory and markerless-Git-repository
tests before invoking the unchanged public `resolve_project_root()` API.

With pytest's intended in-root basetemp forced, the two nodes currently fail
`2/2` because their parent walk reaches the real host
`E:/GT-KB/groundtruth.toml`. A default run currently reports `14 passed` only
when the root conftest falls back to an external temp location, making that
green result environment-dependent and contrary to the root-boundary contract.
The repair keeps every fixture byte in-root, preserves the real parent walk and
Git probe, and never modifies the host marker.

## Specification Links

- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - its root-containment rule
  requires all GT-KB test artifacts and live dependencies beneath `E:/GT-KB`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires the test to preserve the
  GT-KB host/application boundary and avoid external fixture roots.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before the
  protected test changes and independent VERIFIED before completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the
  fixture repair and verification commands to trace to governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit
  PAUTH, project, work-item, target-path, and slice linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent
  execution under the in-root basetemp that exposes the pre-change defect.
- `GOV-STANDING-BACKLOG-001` - governs WI-5419 as the durable hygiene defect.
- `GOV-WORK-TREE-HYGIENE-001` - requires a bounded one-file repair without
  absorbing neighboring dirty paths.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires production root
  validation, parent walking, Git behavior, and basetemp policy to remain
  unchanged.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic
  current evidence under the intended fixture topology.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - require traceable proposal,
  implementation, verification, and completion artifacts.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` establishes the binding
  all-project-files-in-root constraint carried by
  `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`.
- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` is the provenance cited
  by the root conftest for per-session in-root basetemp isolation. This proposal
  preserves that policy and repairs tests that accidentally depended on its
  external fallback.

## Owner Decisions / Input

No new owner decision is required. The owner authorized the modernization
program, required discovered defects to become hygiene items with tests, and
authorized non-mechanical implementation work under the project gates. Active
authority is
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE`.
Implementation remains gated on independent GO plus matching work-intent and
implementation-start authority.

## Requirement Sufficiency

Existing requirements sufficient. The root-containment GOV, isolation ADR,
non-impairment requirement, and existing production resolver contract fully
determine the test-only correction. No production interface, root-resolution
rule, or basetemp policy change is required.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5419 forced in-root reproduction and the root conftest's WI-3469 policy",
  "canonical_authority": "GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 plus ADR-ISOLATION-APPLICATION-PLACEMENT-001",
  "primary_route": "the existing public groundtruth_kb.bridge.paths.resolve_project_root API",
  "before_behavior": "negative fixtures below E:/GT-KB inherit the real host marker as an ancestor and fail to raise; an external pytest fallback masks the defect",
  "after_behavior": "the same production resolver runs while a process-local test seam limits marker visibility to the synthetic fixture boundary",
  "self_descriptive_naming": "a test helper named _confine_marker_lookup_to_fixture describes the only substituted behavior",
  "obsolete_guidance_disposition": "no guidance changes; stale test prose claiming synthetic fixtures are isolated becomes true",
  "history_preservation": "WI-5419 records both the accidental external-green result and deterministic forced-in-root failures",
  "baseline": "14 tests pass under an external fallback, but the two affected nodes fail under an explicit in-root basetemp",
  "expected_result": "all 14 bridge-path tests pass with the basetemp explicitly rooted under E:/GT-KB/.pytest-tmp",
  "rollback": "remove the helper and its two call sites in one governed test-only transaction",
  "hard_invariants": [
    "production bridge.paths source remains byte-for-byte unchanged",
    "resolve_project_root remains the exercised public API",
    "the markerless Git test still invokes a real in-root Git repository",
    "the host groundtruth.toml is never modified, renamed, or deleted",
    "all temporary fixture and basetemp paths remain beneath E:/GT-KB",
    "the canonical in-root basetemp policy remains enabled"
  ],
  "fail_closed_conditions": [
    "any production source changes",
    "a test depends on an external filesystem path",
    "the root marker is mutated",
    "the parent walk or Git probe is bypassed instead of marker visibility being confined",
    "either affected node fails under forced in-root basetemp"
  ],
  "essential_context_preservation": "strict-marker validation, environment override precedence, Git common-dir discovery, parent walking, worktree handling, and state-directory containment tests remain intact"
}
```

## Spec-Derived Verification Plan

1. Root containment, isolation, and non-impairment:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_paths.py -q --tb=short --basetemp=E:/GT-KB/.pytest-tmp/wi5419-verification
```

Expected: `14 passed`. The explicit in-root basetemp is required evidence; a
default run that falls back externally is insufficient.

2. Focused pre-change failure/post-change pass:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_paths.py::test_resolve_project_root_raises_when_no_marker_found groundtruth-kb/tests/test_bridge_paths.py::test_resolve_project_root_rejects_git_repo_without_groundtruth_toml -q --tb=short --basetemp=E:/GT-KB/.pytest-tmp/wi5419-focused-verification
```

Expected after implementation: `2 passed`; current baseline is `2 failed`
because neither node raises.

3. Production-source non-mutation and static scope:

```text
git diff --exit-code -- groundtruth-kb/src/groundtruth_kb/bridge/paths.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/tests/test_bridge_paths.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/tests/test_bridge_paths.py
git diff --check -- groundtruth-kb/tests/test_bridge_paths.py
```

The bridge-path production command must report no WI-5419 diff. Ruff, format,
and whitespace checks must pass. Independent review must distinguish unrelated
pre-existing prose dirt in `bridge/paths.py` from this one-file test scope.

4. Bridge and artifact lifecycle:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5419-in-root-root-resolution-fixture --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5419-in-root-root-resolution-fixture
```

Expected: no missing required/advisory specifications and zero blocking clause
gaps, followed by independent Loyal Opposition verification of the exact test
hunk and command evidence.

## Risk / Rollback

The monkeypatch touches a private predicate during two tests, so careless state
leakage could affect neighbors. `pytest.MonkeyPatch` restores it after each
test, and the full 14-test lane proves isolation. Rollback removes only the
test-local helper and two calls; production files and runtime state are not part
of either direction.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5419-in-root-root-resolution-fixture`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - this is a one-file fixture-isolation repair with no production change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
