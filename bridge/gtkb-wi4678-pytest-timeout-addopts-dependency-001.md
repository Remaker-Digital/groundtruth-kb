NEW

# gtkb-wi4678-pytest-timeout-addopts-dependency — restore pytest-timeout support for default addopts

bridge_kind: prime_proposal
Document: gtkb-wi4678-pytest-timeout-addopts-dependency
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-19T08:30:02Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019edee6-dc09-7903-8274-267d09d3bfd1
author_model: GPT-5
author_model_version: Codex desktop automation
author_model_configuration: autonomous Prime Builder keep-working run

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4678

target_paths: ["pyproject.toml", "groundtruth-kb/pyproject.toml", "groundtruth-kb/uv.lock", "platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py"]

implementation_scope: test-infrastructure
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`WI-4678` tracks a default test-environment defect found during live LO
verification of `WI-4672` and `WI-4677`: the repository root `pyproject.toml`
configures pytest with `--timeout=30`, but the in-root
`groundtruth-kb/.venv/Scripts/python.exe -m pytest ...` command surface rejects
that option because the managed GroundTruth-KB dev/test dependency surface does
not provide `pytest-timeout`.

This proposal keeps the existing default timeout policy intact and restores the
missing dependency contract by adding `pytest-timeout` to the GroundTruth-KB dev
extra, updating the lockfile, and adding a structural regression test that fails
if root pytest addopts require timeout support without the in-root dependency
surface declaring it. The implementation must not use per-command
`-o addopts=""` as the fix; that remains only historical evidence of the
symptom.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected pytest/dependency config changes
  require bridge coordination; this proposal is the PB request for LO review.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the active May29 Hygiene
  PAUTH authorizes proposals for unimplemented work items in this project.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  carries explicit governing requirement linkage before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the bridge file names
  `PROJECT-GTKB-MAY29-HYGIENE`, `WI-4678`, and the active PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must execute
  tests derived from each linked specification before a VERIFIED response.
- `GOV-STANDING-BACKLOG-001` — `WI-4678` is a standing backlog defect captured
  from live LO verification evidence and must move through governed status.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root pytest config must remain a
  GT-KB platform surface and must not broaden default discovery into hosted
  application tests while repairing the timeout dependency.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the recurring workaround has crossed
  from incidental observation into a governed backlog defect and bridge packet.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — implementation must preserve durable
  evidence through a testable dependency/config contract, not only a chat note.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the defect is already captured as
  `WI-4678`; this proposal moves the artifact through the bridge lifecycle.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` — owner authorization
  recorded by the project PAUTH for all unimplemented May29 Hygiene work items.
- `bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-003.md` — PB
  implementation evidence recorded that the exact proposed pytest command could
  not collect because the local venv rejected `--timeout=30`.
- `bridge/gtkb-wi4677-backlog-json-option-validation-003.md` — PB
  implementation evidence recorded the same default addopts failure before
  focused tests could run.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-005.md` — historical
  bridge evidence shows the same workaround pattern (`-o addopts=""`) has
  appeared before; this proposal turns that recurring workaround into a tracked
  dependency/config contract fix.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The active
authorization is
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, backed by
`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`, and the change is bounded
to test-infrastructure dependency/config parity for `WI-4678`.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`,
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` define the bridge, authorization,
proposal-linkage, verification, backlog, platform/application-isolation, and
artifact-lifecycle constraints needed for this fix. No DA/GOV/SPEC/PB/ADR/DCL
mutation is in scope.

Backlog visibility evidence for `GOV-STANDING-BACKLOG-001`: this is a single
work-item proposal, not a bulk backlog operation. The live inventory artifact
is `gt backlog show WI-4678 --json`, which shows `resolution_status: open`,
`stage: backlogged`, and `project_name: PROJECT-GTKB-MAY29-HYGIENE`; the review
packet is this bridge proposal. No `DECISION DEFERRED` marker is required
because implementation authorization already exists through the active PAUTH.

## Spec-Derived Verification Plan

Implementation must create or update tests that prove the contract rather than
merely bypassing it. Expected verification:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py -q --tb=short --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py --collect-only -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/test_pytest_timeout_dependency.py
```

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `gt bridge show
  gtkb-wi4678-pytest-timeout-addopts-dependency --json` and bridge
  applicability preflight must show this proposal/report is the live bridge
  authority for the protected target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `gt projects authorizations
  PROJECT-GTKB-MAY29-HYGIENE --json` must show the active May29 all-unimplemented
  PAUTH before implementation begins.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — bridge preflights must
  pass with no missing required specs and parseable `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report
  must map each linked spec to executed test evidence and must not request
  VERIFIED without those results.
- `GOV-STANDING-BACKLOG-001` — `gt backlog show WI-4678 --json` must remain
  linked to the bridge thread until resolution evidence is recorded.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — focused collect-only verification
  must retain root platform `testpaths` behavior and the Agent Red ignore while
  proving the timeout option is now recognized.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the implementation report must
  preserve bridge evidence, cite the backlog item, and avoid ad hoc local-only
  workaround state.

## Code Quality Baseline

| Requirement | Applicability | Planned evidence |
| --- | --- | --- |
| `CQ-SECRETS-001` | No credentials, tokens, or `.env` values are in scope. | `git diff --check` plus normal pre-commit credential scan on the eventual implementation commit. |
| `CQ-PATHS-001` | All target paths are inside `E:/GT-KB`; no live dependency on `E:/Claude-Playground`. | Bridge preflight and implementation report path evidence. |
| `CQ-COMPLEXITY-001` | The change should be a dependency/config parity fix plus a small structural test, not a new test runner. | Code review of the final diff; no new runtime abstraction expected. |
| `CQ-CONSTANTS-001` | Any package/version value must live in the dependency surface, not hard-coded in unrelated runtime code. | Structural test reads config/dependency declarations instead of duplicating hidden state. |
| `CQ-SECURITY-001` | Adding a dev/test package must not affect production runtime dependencies. | Diff review confirms the package is dev/test scoped; no production Docker/runtime file changes expected. |
| `CQ-DOCS-001` | No user-facing documentation change is required unless implementation discovers stale setup docs that cite the affected command. | Implementation report notes whether docs were changed or explicitly not needed. |
| `CQ-TESTS-001` | Add focused regression coverage for timeout-addopts/dependency parity and run collect-only on a previously blocked focused suite. | Commands listed in the verification plan. |
| `CQ-LOGGING-001` | No logging behavior is in scope. | N/A. |
| `CQ-VERIFICATION-001` | Use repo-native venv commands; do not rely on clearing addopts as verification. | Verification commands above run without `-o addopts=""`. |

## Risk / Rollback

Primary risk is dependency-surface drift: adding `pytest-timeout` in one place
but not the lock or the venv provisioning path would leave the symptom partly
reproducible. Secondary risk is accidentally solving the local problem by
removing the timeout policy, which would weaken the default test guard rather
than making it runnable. Rollback is a single implementation commit revert that
restores `pyproject.toml`, `groundtruth-kb/pyproject.toml`,
`groundtruth-kb/uv.lock`, and the focused test file to their prior state.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4678-pytest-timeout-addopts-dependency`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — this repairs a broken default pytest command surface and adds regression
coverage for the dependency/config contract.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
