NEW

# GT-KB Bridge Implementation Report - gtkb-wi5407-installed-wheel-source-exclusion - 003

bridge_kind: implementation_report
Document: gtkb-wi5407-installed-wheel-source-exclusion
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5407-installed-wheel-source-exclusion-002.md
Approved proposal: bridge/gtkb-wi5407-installed-wheel-source-exclusion-001.md
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5407
Recommended commit type: test

## Implementation Claim

The approved one-file test repair now resolves the installed module path once,
retains the positive requirement that it live inside the newly created venv,
and replaces the invalid repository-wide lexical exclusion with exact
exclusion of `groundtruth-kb/src`. A valid wheel installed into an in-root
pytest venv is therefore accepted while an editable or checkout-source import
still fails.

All surrounding isolated-mode, package-resource uniqueness, packaged-default
registry, context-manifest, absent-root-config, and host-authority fallback
assertions remain unchanged. No production source, dispatcher, TAFE, harness,
database, Git, or unrelated test path was changed.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
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
schema-v3 implementation-start packet.

## Prior Deliberations

- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5407-installed-wheel-source-exclusion-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001` | The built wheel assembled the seven-category packaged-default context with 14 items and no omissions; the exact module passed 4/4. |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | The explicit in-root basetemp remains below `E:/GT-KB`; exact checkout-source exclusion replaces the invalid repository-ancestry assertion. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Test artifacts remain in-root while the isolated venv is treated as a fixture rather than a source checkout. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The target validated `authorized: true` under the live GO, matching claim, active PAUTH, and schema-v3 start packet. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every applicable proposal specification, including IDs omitted by the scaffold's multi-ID bullet parser. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal, GO, PAUTH, project, WI-5407, claim/start packet, and exact target remain mutually consistent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The exact forced in-root four-test command passed 4/4 in 33.00 seconds. |
| `GOV-STANDING-BACKLOG-001` | WI-5407 remains the linked origin-hygiene item; this report appends evidence without prematurely resolving it. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Venv containment, isolated Python mode, resource uniqueness, packaged-default origin, absent root config, and no-host-fallback checks remain intact; Ruff, format, and diff checks pass. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | The final three-insertion/two-removal diff names the resolved module and exact excluded checkout source path; SHA-256 and commands are recorded below. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Work item, test, proposal, GO, claim/start packet, report, and future independent verdict retain separate lifecycle evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The complete WI-5407 artifact graph remains linked and queryable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This implementation report requests independent verification and does not claim terminal completion or finalization. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=600`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short --timeout=600 --basetemp=E:/GT-KB/.pytest-tmp/wi5407-verification`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_modernization_fresh_worker.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_modernization_fresh_worker.py`
- `git diff --check -- platform_tests/scripts/test_modernization_fresh_worker.py`
- `python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_modernization_fresh_worker.py`

## Observed Results

- Baseline: 3 passed, 1 failed in 30.95 seconds. The sole failure was the
  broad `not module.is_relative_to(REPO_ROOT)` assertion after the wheel had
  built, installed, imported, and produced the expected packaged-default
  payload.
- Final explicit in-root verification: 4 passed in 33.00 seconds.
- Ruff check: pass. Ruff format check: pass. `git diff --check`: pass.
  Implementation authorization validation: `authorized: true`.
- Final target SHA-256:
  `137745CC34FDF7B310D14BC0013E8E1F01CA1C5798D24B9AEBFFAB361E32EE5E`.

## Files Changed

- `platform_tests/scripts/test_modernization_fresh_worker.py`

Excluded out-of-scope dirty paths: 1,471. None was adopted or modified.

## Recommended Commit Type

- Recommended commit type: `test`
- Diff-stat justification: All changed paths are test paths.

```text
     platform_tests/scripts/test_modernization_fresh_worker.py | 5 +++--
     1 file changed, 3 insertions(+), 2 deletions(-)
```

## Acceptance Criteria Status

- [x] Imported module remains inside the newly created venv.
- [x] Imported module is outside the exact checkout source directory.
- [x] Python remains in isolated `-I` mode.
- [x] Registry origin remains `packaged_default` and the root config remains
  absent.
- [x] Every expected packaged resource occurs exactly once in the wheel.
- [x] Host authority fallback tests remain present and pass.
- [x] Exact forced in-root lane passes 4/4.
- [x] Only the approved test file changed, with a three-insertion/two-removal
  diff.

## Risk And Rollback

Residual risk is that a future alternate checkout-source alias falls outside
`BUILD_PROJECT / "src"`. The positive venv-containment assertion remains the
primary proof, and the exact resolved checkout source path blocks the current
editable/source fallback without rejecting legitimate in-root installs.

Rollback requires a separately authorized one-file restoration of
`platform_tests/scripts/test_modernization_fresh_worker.py` to its pre-WI-5407
image. Preserve all numbered bridge artifacts, WI history, dispatcher/TAFE
state, leases, and unrelated worktree bytes.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
