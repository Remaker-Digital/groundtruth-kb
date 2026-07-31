NEW

# GT-KB Bridge Implementation Report - gtkb-wi5405-portability-fixture-read-guard - 003

bridge_kind: implementation_report
Document: gtkb-wi5405-portability-fixture-read-guard
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5405-portability-fixture-read-guard-002.md
Approved proposal: bridge/gtkb-wi5405-portability-fixture-read-guard-001.md
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5405
Recommended commit type: test

## Implementation Claim

The one approved test target now distinguishes source-root ancestry from a
source dependency. Both embedded subprocess programs normalize a closed allow
set containing only the relocated host and the active interpreter prefix, use
the same `denied_source` classifier, and assert before installing their audit
hooks that both allow roots pass while the GT-KB root and
`groundtruth-kb/src` remain denied.

The runtime probe also prevents nested pytest from discovering checkout
configuration or parent `conftest.py` files by fixing its root/config/conftest
boundary at the relocated Agent Red application. The migration driver receives
the exact relocated host, and its package-origin assertion now proves the
installed package is under `sys.prefix` and outside the denied-source
classification. No production source, dispatcher, TAFE, harness, database,
Git, or unrelated test path was changed.

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
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. The implementation uses the active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`,
the independent GO in version 002, and this session's exact matching claim and
schema-v3 implementation-start packet. The owner's standing non-impairment and
origin-hygiene directives remain unchanged.

## Prior Deliberations

- `bridge/gtkb-wi5405-portability-fixture-read-guard-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5405-portability-fixture-read-guard-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | The exact forced in-root lifecycle node passed 1/1 after executing clean install, runtime, upgrade, migration, rollback, and post-rollback runtime phases. |
| `DCL-APP-ROOT-MINIMIZATION-001` | The same lifecycle node retained `validate_app_root_minimization` and the relocated application-origin assertion; 1/1 passed. |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | Runtime evidence retained installed-package origin under the isolated interpreter, Agent Red origin under the relocated app, and supported platform service calls; 1/1 passed. |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | Both subprocesses assert that the exact relocated host is allowed while the platform checkout remains denied; the target module passed 4/4. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Every runtime and test artifact remains below `E:/GT-KB`; the relocated application fixture remains under its in-root pytest sandbox and no external live dependency is introduced. |
| `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` | The relocated fixture retains the `applications/Agent_Red` layout and its exact origin assertion; the forced lifecycle node passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `implementation_authorization.py validate --target platform_tests/scripts/test_modernization_agent_red_portability.py` returned `authorized: true`; only the GO-approved path changed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The report carries forward all twelve linked specifications from the approved version 001 proposal. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal, GO, PAUTH, project, WI-5405, claim, start packet, and exact target remain mutually consistent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The exact target passed 4/4, the forced in-root node passed 1/1, and the combined frozen lane passed all 67 runnable tests with five dependency skips described below. |
| `GOV-STANDING-BACKLOG-001` | WI-5405 remains the linked origin-hygiene work item and this report appends implementation evidence without resolving it prematurely. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Ruff, format, `git diff --check`, exact-scope status, and the 72-collected-test compatibility run passed without touching runtime or foreign files. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Symmetric named classifiers, explicit positive/negative assertions, exact SHA-256, and reproducible commands expose the complete decision boundary. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5405, linked tests, proposal, GO, claim/start packet, this report, and the requested independent verdict remain separate append-only lifecycle evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The work item, exact target, proposal, GO, claim/start packet, executed tests, report, and future verdict remain linked as one durable artifact graph. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Candidate implementation, implementation report, independent verification, and focused finalization remain distinct; this report does not claim terminal completion. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py -q --tb=short --timeout=300`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py::test_agent_red_survives_relocation_and_has_an_independent_lifecycle -q --tb=short --timeout=300 --basetemp=E:/GT-KB/.pytest-tmp/wi5405-verification-5`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py platform_tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=900`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_rehearse_isolation.py -q -rs --tb=short --timeout=900`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_agent_red_portability.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_modernization_agent_red_portability.py`
- `git diff --check -- platform_tests/scripts/test_modernization_agent_red_portability.py`
- `python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_modernization_agent_red_portability.py`

## Observed Results

- Baseline before implementation: 3 passed, 1 failed in 23.13 seconds. The
  failing lifecycle node was denied while opening the exact relocated Agent Red
  path under the in-root pytest fixture.
- Final forced in-root lifecycle proof: 1 passed in 80.59 seconds. It completed
  runtime, upgrade, migration, rollback, and post-rollback execution.
- Final exact target result: 4/4 tests passed as the first four results in the
  combined run.
- Combined frozen lane: 72 collected, 67 passed, 5 skipped in 80.44 seconds.
  `-rs` confirmed all five skips are at
  `platform_tests/scripts/test_rehearse_isolation.py:252` because the tracked
  production rehearsal manifest is deleted in the current shared worktree.
  That foreign assessment-tree retirement is owned by WI-5433 and was not
  restored, copied, adopted, or changed by WI-5405.
- Ruff check: pass. Ruff format check: pass. `git diff --check`: pass.
  Implementation authorization validation: `authorized: true`.
- Final target SHA-256:
  `7E7B16435FC5F9CB5086AD58EE570FA56AA5DE5B7F5A3397F8D7775874F483C6`.

## Files Changed

- `platform_tests/scripts/test_modernization_agent_red_portability.py`

The helper identified 1,463 excluded out-of-scope dirty paths. The modified
`platform_tests/scripts/test_rehearse_isolation.py` and the deleted production
manifest are foreign WI-5433/WI-5434-era state and remain excluded.

## Recommended Commit Type

- Recommended commit type: `test`
- Diff-stat justification: All changed paths are test paths.

```text
     .../test_modernization_agent_red_portability.py    | 67 +++++++++++++++++-----
     1 file changed, 54 insertions(+), 13 deletions(-)
```

## Acceptance Criteria Status

- [x] Both embedded programs share the exact two-root allow set and identical
  denied-source semantics.
- [x] The relocated host and active interpreter prefix are allowed; the GT-KB
  root and `groundtruth-kb/src` remain explicitly denied before each audit hook.
- [x] Runtime and migration package origins remain under the isolated
  interpreter; Agent Red remains under the relocated application root.
- [x] Nested pytest cannot load checkout configuration or parent conftest
  files.
- [x] The forced in-root lifecycle node passes with all lifecycle and rollback
  assertions retained.
- [x] Every runnable test in the 72-collected-test frozen lane passes.
- [ ] The proposal's literal `72 passed` summary is not observable in the
  current shared worktree because five rehearsal tests intentionally skip when
  their separately governed production manifest is absent. LO should determine
  whether WI-5433 is a verification dependency or whether 67 passed plus five
  explicit dependency skips is sufficient for this one-file WI-5405 repair.
- [x] Only the exact approved WI-5405 target is part of this implementation.

## Risk And Rollback

Residual risk is limited to a classifier exemption becoming broader than the
two exact fixture roots or nested pytest again discovering checkout state.
The explicit positive and negative assertions, root/config/conftest bounds,
and full lifecycle test fail closed on either regression.

Rollback requires a separately authorized one-file restoration of
`platform_tests/scripts/test_modernization_agent_red_portability.py` to its
pre-WI-5405 image. Preserve all numbered bridge artifacts, WI history, foreign
assessment-tree state, dispatcher/TAFE state, leases, and unrelated worktree
bytes.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
