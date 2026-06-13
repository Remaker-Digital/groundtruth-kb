NEW

# gtkb-wi-4475-platform-pytest-discovery-scope — Platform Pytest Discovery Scope

bridge_kind: prime_proposal
Document: gtkb-wi-4475-platform-pytest-discovery-scope
Version: 001
Author: Codex Prime Builder
Date: 2026-06-12 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4475

target_paths: ["pyproject.toml", "platform_tests/governance/test_platform_tests_rename.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Bare `python -m pytest` at the GT-KB repository root currently discovers both
`platform_tests` and `applications/Agent_Red/tests`. In the GT-KB platform venv,
collection then fails before any platform tests run because Agent Red's test
conftest imports `azure.cosmos`, which is not installed in the platform-only
environment.

This proposal narrows the root default pytest `testpaths` to the GT-KB platform
test tree and adds a regression assertion to the existing platform-test rename
invariant. Agent Red tests remain runnable through their explicit CI/test
paths; the change only prevents the platform default command from accidentally
collecting the application test suite.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires this implementation proposal to
  enter the bridge as a `NEW` entry and makes `bridge/INDEX.md` the canonical
  queue state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this
  proposal to cite the governing requirements for the implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires project,
  work-item, PAUTH, and target path metadata in the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires verification to
  derive from the cited requirements and target the implemented behavior.
- `GOV-STANDING-BACKLOG-001` — WI-4475 is the standing backlog item that makes
  this reliability fix durable across sessions.
- `GOV-RELIABILITY-FAST-LANE-001` — authorizes small defect/reliability fixes
  under the standing reliability project while retaining bridge review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — governs the separation between
  the GT-KB platform root and adopter applications under `applications/<name>/`;
  the default platform pytest command should not accidentally require adopter
  application dependencies.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — confirms the standing PAUTH
  does not bypass the required bridge proposal and verification flow.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision approving the
  standing reliability fast-lane and standing authorization used here.
- `DELIB-S377-SLICE7PRIME-PYTEST-CONTAMINATION-WAIVER` — prior pytest
  contamination waiver; this proposal removes one current contamination source
  instead of asking for another waiver.

## Owner Decisions / Input

No new owner decision is required. `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` authorize small reliability
fixes for active work items in `PROJECT-GTKB-RELIABILITY-FIXES`, while preserving
the bridge proposal/review/verification gates.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4475 identifies the failing platform
pytest surface; `GOV-RELIABILITY-FAST-LANE-001` and the standing PAUTH cover the
small test-configuration fix; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
keeps this work inside the bridge protocol.

## Spec-Derived Verification Plan

Verification will demonstrate both the failure class and the regression guard:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest --collect-only -q
```

Expected after implementation: root default collection no longer imports
`applications/Agent_Red/tests/conftest.py`; collection succeeds for the default
GT-KB platform test scope.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/governance/test_platform_tests_rename.py -q --tb=short
```

Expected: the platform-test rename invariants pass, including a new assertion
that root `testpaths` do not include `applications/Agent_Red/tests`. This maps
the isolation ADR to executable evidence by preventing the default platform
test command from crossing into the adopter test tree.

## Risk / Rollback

Risk: anyone relying on bare root `pytest` to run Agent Red tests must pass the
Agent Red paths explicitly. That matches current CI, which already passes
application paths explicitly and installs application dependencies separately.
Rollback is a single diff reverting `pyproject.toml` and the added invariant.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-wi-4475-platform-pytest-discovery-scope` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

fix: restores the GT-KB platform default pytest discovery path by preventing
application-test collection from the platform venv.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
