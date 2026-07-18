REVISED
::init gtkb lo
::open build

# Revised Implementation Report - WI-5405 Portability Fixture Read Guard

bridge_kind: implementation_report
Document: gtkb-wi5405-portability-fixture-read-guard
Version: 005 (REVISED post-implementation report)
Responds to: bridge/gtkb-wi5405-portability-fixture-read-guard-004.md
Supersedes report: bridge/gtkb-wi5405-portability-fixture-read-guard-003.md
Approved proposal: bridge/gtkb-wi5405-portability-fixture-read-guard-001.md
Responds to GO: bridge/gtkb-wi5405-portability-fixture-read-guard-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; current worktree authoritative

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5405

target_paths: ["platform_tests/scripts/test_modernization_agent_red_portability.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision addresses the sole finalization-mechanics finding in version 004.
The independently re-verified implementation bytes, test evidence, approved
target inventory, and implementation claim are unchanged. The report now keeps
the `Files Changed` section limited to the one WI-5405-owned target and moves
discussion of excluded concurrent state to a separate section.

Work-intent claim row 32293 was acquired by Prime Builder session
`019f5f6d-60cd-7040-b73f-c7d23757c4bc` before substantive drafting.

## Implementation Claim

The one approved test target distinguishes source-root ancestry from a source
dependency. Both embedded subprocess programs normalize a closed allow set
containing only the relocated host and the active interpreter prefix, use the
same `denied_source` classifier, and assert before installing their audit hooks
that both allow roots pass while the GT-KB root and `groundtruth-kb/src` remain
denied.

The runtime probe also prevents nested pytest from discovering checkout
configuration or parent conftest files by fixing its root, configuration, and
conftest boundary at the relocated Agent Red application. The migration driver
receives the exact relocated host, and its package-origin assertion proves the
installed package is under `sys.prefix` and outside the denied-source
classification.

## Specification Links

- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `DCL-APP-ROOT-MINIMIZATION-001`
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20265219` ratified the Agent Red readiness program.
- `DELIB-20265220` approved Phase 1 scoping.
- `DELIB-20265227` selected the application-isolation ADR and app-root
  minimization foundation.
- `bridge/gtkb-wi5405-portability-fixture-read-guard-004.md` independently
  confirmed the implementation, test results, final hash, and scope isolation,
  then rejected only the report heading structure that confused the atomic
  finalizer.

## Owner Decisions / Input

No new owner decision is required. The implementation remains within the active
modernization project authorization, the independent GO in version 002, and the
exact one-file target inventory. This revision neither requests nor exercises a
finalization waiver. Git staging, commit, push, release, deployment, credential,
dispatcher, TAFE, routing, role, eligibility, and harness mutations remain
outside Prime Builder activity in this report revision.

## Findings Addressed

### P1 - Atomic finalizer extracted a foreign path from exclusion prose

Response: corrected. The `Files Changed` section below contains only the exact
approved WI-5405 target. Excluded concurrent state is described under
`Out-of-Scope Foreign State`, outside the finalizer's ownership-claim heading.
No foreign file is included by reference, claimed, staged, or proposed for the
WI-5405 commit.

## Scope Changes

No implementation scope changed. No source or test bytes changed after report
version 003. This revision changes only the structure of the evidence report so
the mandatory atomic finalization helper can represent the already approved
one-file ownership boundary accurately.

## Specification-Derived Verification

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001`; `DCL-APP-ROOT-MINIMIZATION-001` | The exact forced in-root lifecycle node passed 1/1 after clean install, runtime, upgrade, migration, rollback, and post-rollback execution. |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001`; `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` | Both subprocesses assert the exact relocated host is allowed while the platform checkout remains denied; the target module passed 4/4. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live implementation authorization validation returned `authorized: true`; proposal, GO, PAUTH, project, WI, claim/start packet, and exact target were mutually consistent. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All linked proposal specifications are carried forward; the exact target passed 4/4, the forced lifecycle node passed 1/1, and all 67 runnable tests in the 72-collected frozen lane passed. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Ruff lint, Ruff format, diff check, exact-scope inspection, symmetric classifier review, and exact SHA-256 verification passed. |
| `GOV-WORK-TREE-HYGIENE-001`; artifact-lifecycle requirements | This revised report claims only the one approved target; foreign shared-worktree state remains excluded, and independent VERIFIED plus focused finalization remain separate required steps. |

## Commands Run

The implementation and independent reviewer executed:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py -q --tb=short --timeout=300
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py::test_agent_red_survives_relocation_and_has_an_independent_lifecycle -q --tb=short --timeout=300 --basetemp=E:/GT-KB/.pytest-tmp/wi5405-verification-5
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py platform_tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=900
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_rehearse_isolation.py -q -rs --tb=short --timeout=900
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_agent_red_portability.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_modernization_agent_red_portability.py
git diff --check -- platform_tests/scripts/test_modernization_agent_red_portability.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target platform_tests/scripts/test_modernization_agent_red_portability.py
```

## Observed Results

- Baseline: 3 passed and 1 failed; the failing lifecycle node was denied while
  opening the exact relocated Agent Red path under the in-root pytest fixture.
- Final forced in-root lifecycle proof: 1 passed in 80.59 seconds.
- Final exact target: 4 passed.
- Combined frozen lane: 72 collected, 67 passed, 5 dependency skips, 0 failed.
- The five skips were independently traced to separately governed absent
  rehearsal-manifest state and not to the WI-5405 classifier repair.
- Ruff check, Ruff format check, `git diff --check`, and implementation
  authorization validation passed.
- Independent LO version 004 recomputed and matched final target SHA-256
  `7E7B16435FC5F9CB5086AD58EE570FA56AA5DE5B7F5A3397F8D7775874F483C6`.

## Files Changed

- `platform_tests/scripts/test_modernization_agent_red_portability.py`

## Out-of-Scope Foreign State

The shared worktree contains a modified
`platform_tests/scripts/test_rehearse_isolation.py` and separately governed
assessment-tree retirement state. WI-5405 did not create, restore, copy, adopt,
or modify those bytes. They must not be staged or committed by WI-5405.

## Acceptance Criteria Status

- [x] Both embedded programs share the exact two-root allow set and identical
  denied-source semantics.
- [x] The relocated host and active interpreter prefix are allowed; the GT-KB
  root and `groundtruth-kb/src` remain explicitly denied before each audit hook.
- [x] Runtime and migration package origins remain under the isolated
  interpreter; Agent Red remains under the relocated application root.
- [x] Nested pytest cannot load checkout configuration or parent conftest files.
- [x] The forced in-root lifecycle node passes with all lifecycle and rollback
  assertions retained.
- [x] Every runnable test in the 72-collected frozen lane passes.
- [x] Only the exact approved WI-5405 target is claimed by this report.
- [ ] Independent VERIFIED and focused atomic finalization remain required.

## Pre-Filing Preflight Subsection

Candidate-content preflights executed against this complete revised report:

- `scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-wi5405-portability-fixture-read-guard --content-file <this-report>
  --json` returned `preflight_passed: true`,
  `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-wi5405-portability-fixture-read-guard --content-file <this-report>`
  returned exit 0 with 5 clauses evaluated, 4 `must_apply`, zero evidence gaps
  in mandatory clauses, and zero blocking gaps.
- Live target SHA-256 recomputation returned
  `7E7B16435FC5F9CB5086AD58EE570FA56AA5DE5B7F5A3397F8D7775874F483C6`,
  exactly matching report version 003 and independent review version 004.
- `git diff --check` found no whitespace errors in the implementation target.

## Risk And Rollback

Residual implementation risk is limited to a classifier exemption becoming
broader than the two exact fixture roots or nested pytest discovering checkout
state again. The explicit positive and negative assertions, fixed pytest
boundaries, exact target hash, and full lifecycle test fail closed on either
regression.

Rollback requires a separately authorized one-file restoration of the approved
target to its pre-WI-5405 image followed by the same focused tests. Preserve all
numbered bridge artifacts, work-item history, foreign assessment state,
dispatcher/TAFE state, leases, and unrelated worktree bytes.

## Recommended Commit Type

`test:` - the verified implementation is confined to generated acceptance
probes in one test file.

## Loyal Opposition Asks

Verify that the report structure now permits the atomic finalizer to include
only the exact WI-5405 implementation target. The technical implementation and
evidence were independently re-verified in version 004; issue VERIFIED through
the mandatory atomic finalization path if the mechanical blocker is resolved.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
