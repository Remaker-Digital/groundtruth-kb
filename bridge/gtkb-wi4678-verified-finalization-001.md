NEW

# WI-4678 verified implementation finalization

bridge_kind: prime_proposal
Document: gtkb-wi4678-verified-finalization
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-19T12:45:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: keep-working-20260619T124500Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: autonomous Prime Builder keep-working automation; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4678

target_paths: ["groundtruth-kb/pyproject.toml", "groundtruth-kb/uv.lock", "platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py", "bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-002.md", "bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-003.md", "bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md", "bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md", "bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-006.md", "groundtruth.db"]

implementation_scope: verified-finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4678 is implementation-verified at `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-006.md`, but the corresponding source, lockfile, regression test, and numbered bridge chain files remain uncommitted in the live worktree. The current active implementation-start packet belongs to unrelated Agent Red readiness work, and the original WI-4678 packet is terminal because the bridge thread is already `VERIFIED`.

This proposal asks Loyal Opposition to authorize the narrow finalization step that remains after verification: preserve the already-verified WI-4678 artifact set in a path-limited local commit, then resolve WI-4678 in MemBase with completion evidence pointing to the verified bridge chain and commit. It does not request new pytest-timeout implementation work, dependency changes beyond the verified diff, or any mutation outside the listed target paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - finalization still changes repository and MemBase state, so it must proceed through a reviewed bridge proposal instead of bypassing the implementation-start gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active May29 Hygiene authorization covers unimplemented work items in this project but does not replace bridge `GO` or target-path scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing requirements before requesting finalization authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries `Project Authorization`, `Project`, and `Work Item` metadata for WI-4678.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - WI-4678 has already received LO verification; finalization must preserve that evidence and re-check the focused test surface before commit.
- `GOV-STANDING-BACKLOG-001` - resolving WI-4678 is a governed backlog mutation and needs explicit bridge authority and completion evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain inside `E:\GT-KB` and the change preserves root platform pytest behavior without routing evidence to Agent Red.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the post-verification finalization gap is captured as a durable bridge action rather than a chat-only workaround.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - finalization preserves source, tests, lockfile, bridge evidence, and backlog closure as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the verified bridge verdict is the lifecycle trigger for committing the verified artifact set and resolving the work item.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner authorization for autonomous implementation flow on unimplemented May29 Hygiene work items.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-001.md` - approved implementation proposal for the pytest-timeout dependency repair.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-002.md` - Loyal Opposition GO authorizing implementation.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md` - Loyal Opposition NO-GO requiring managed dependency, lockfile, venv install, and structural regression test completion.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md` - revised implementation report documenting the completed dependency, lockfile, venv install, and regression test.
- `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-006.md` - Loyal Opposition VERIFIED verdict for WI-4678.

## Owner Decisions / Input

No new owner decision is required. This finalization stays within active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, backed by `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`, and does not create or modify formal GOV/SPEC/ADR/DCL records.

## Requirement Sufficiency

Existing requirements sufficient. The verified WI-4678 bridge chain plus the standing bridge, project authorization, backlog, root-boundary, and artifact-lifecycle requirements listed above define the remaining finalization work. No new or revised requirement is needed before this finalization.

## Proposed Finalization Scope

If this proposal receives `GO`, Prime Builder will:

1. Acquire a work-intent claim and implementation-start packet for this finalization thread.
2. Re-run the focused verification commands that LO already accepted for WI-4678.
3. Stage only the listed WI-4678 paths, preserving unrelated dirty/staged work and excluding all unrelated source or bridge artifacts.
4. Create a local `fix:` commit for the verified WI-4678 artifact set.
5. Resolve WI-4678 in MemBase with completion evidence referencing the VERIFIED bridge verdict and local commit.
6. File a post-finalization implementation report through this bridge thread for Loyal Opposition verification.

## Spec-Derived Verification Plan

Expected commands before the post-finalization report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py -q --tb=short --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py --collect-only -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py
git diff --check -- groundtruth-kb/pyproject.toml groundtruth-kb/uv.lock platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-002.md bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-003.md bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-004.md bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-005.md bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-006.md
gt backlog show WI-4678 --json
```

Verification mapping:

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused pytest, collect-only, Ruff, and diff checks must pass without clearing pytest addopts.
- `GOV-STANDING-BACKLOG-001` - MemBase readback must show WI-4678 resolved only after the local commit exists and completion evidence cites the verified bridge verdict.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `gt bridge show gtkb-wi4678-verified-finalization --json` must show this thread's post-finalization report as the latest numbered bridge entry before requesting verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-start authorization must validate the active May29 Hygiene PAUTH, WI-4678 metadata, and the listed target paths.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all committed artifacts and MemBase evidence must stay under `E:\GT-KB`.

## Risk / Rollback

Primary risk is bundling unrelated dirty work from the current broad worktree. Mitigation: use path-limited staging and commit only the listed WI-4678 files, then verify the commit diff. Secondary risk is resolving WI-4678 before commit evidence exists. Mitigation: perform MemBase resolution only after the local commit is created and cite the commit plus `bridge/gtkb-wi4678-pytest-timeout-addopts-dependency-006.md`.

Rollback is a local revert of the finalization commit plus a follow-up governed MemBase correction if the backlog resolution was already applied. The original verified bridge chain remains append-only.

## Recommended Commit Type

fix: the final local commit should preserve the verified fix for a broken default pytest command surface and its regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
