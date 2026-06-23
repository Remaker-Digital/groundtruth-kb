NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T12-21-46Z-prime-builder-A-8228ac
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; dispatch_id=2026-06-23T12-21-46Z-prime-builder-A-8228ac

# GT-KB Bridge Implementation Report - WI-4690 Application Work-Subject Advisory Boundary

bridge_kind: implementation_report
Document: gtkb-wi4690-application-work-subject-advisory-boundary
Version: 003 (NEW; post-implementation report)
Date: 2026-06-23 UTC
Responds to GO: bridge/gtkb-wi4690-application-work-subject-advisory-boundary-002.md
Approved proposal: bridge/gtkb-wi4690-application-work-subject-advisory-boundary-001.md
Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4690
Recommended commit type: fix

## Implementation Claim

Implemented the approved WI-4690 boundary tightening in `scripts/workstream_focus.py`.

Application work-subject sessions now block mutating writes to GT-KB bridge/governance/control-plane paths, including `.claude/rules/**`, `.claude/hooks/**`, `.codex/**`, `groundtruth.db`, and ordinary `bridge/*.md` files. The only GT-KB-directed write left open from application mode is a full-content `Write` to a numbered bridge file whose first non-blank line is `ADVISORY` and whose metadata declares an advisory `bridge_kind`.

The shared shell-command path now treats `Bash`, `shell_command`, and `functions.shell_command` as shell tools for path extraction. Mutating shell writes to bridge/governance paths fail closed because the guard cannot reliably inspect the final full file content.

Added regression coverage for application-mode governance blocking, ADVISORY bridge allowance, non-ADVISORY bridge blocking, shell fail-closed behavior, and bridge-source advisory-router staging. Also hardened existing startup-relay cache tests in the same authorized test file so they are isolated from auto-dispatch environment variables and use an unambiguously stale timestamp.

## Files Changed

- `scripts/workstream_focus.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_advisory_backlog_router.py`

No changes were made to `.claude/hooks/workstream-focus.py`, `.codex/gtkb-hooks/workstream-focus.cmd`, `platform_tests/scripts/test_workstream_focus_hook_parity.py`, or `scripts/advisory_backlog_router.py`; existing behavior there is covered by the executed parity/router tests.

The shared worktree contained unrelated dirty files before this dispatch. They are not part of this implementation report.

## Specification Links

- `DELIB-20265586`
- `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23`
- `WI-4690`
- `bridge/gtkb-envelope-disposition-autonomous-dispatch-advisory-001.md`
- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001`
- `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001`
- `DCL-ADVISORY-ROUTING-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-CODE-QUALITY-BASELINE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision was required. This implementation stayed within the active snapshot PAUTH, the latest GO verdict, and the implementation-start packet.

## Prior Deliberations

- `DELIB-20265586` - owner approval for the snapshot-bound project implementation authorization.
- `DELIB-20265287` - owner decision set for the envelope disposition and autonomous dispatch program.
- `DELIB-20260621` - activity disposition profile framing.
- `bridge/gtkb-wi4690-application-work-subject-advisory-boundary-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4690-application-work-subject-advisory-boundary-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `WI-4690` application write-isolation | `platform_tests/hooks/test_workstream_focus.py` now asserts application subject blocks `.claude/rules/**`, `.claude/hooks/**`, `.codex/**`, `groundtruth.db`, and non-ADVISORY numbered bridge writes. Full approved pytest command passed. |
| `WI-4690` cross-scope advisory channel | `test_application_subject_allows_bridge_advisory_write` asserts a full-content numbered bridge `ADVISORY` write with advisory `bridge_kind` remains allowed. |
| `DCL-ADVISORY-ROUTING-001` | `test_router_stages_bridge_advisory_candidates_creates_no_work_items` asserts latest bridge `ADVISORY` threads stage candidate events with `source="bridge"` and create no work items. |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001` | Full `test_workstream_focus.py` command passed, including application-product allowance, GT-KB-product blocking, and current-repo control-plane blocking behavior. |
| `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001` | Guard logic uses subject/category and bridge metadata, not Agent Red-specific path checks. Existing init/application alias tests remained passing in the full command. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Numbered bridge write allowance requires canonical status token `ADVISORY`; non-ADVISORY bridge report/proposal content blocks under application subject. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps each linked requirement to executed test evidence and command results. |
| `GOV-CODE-QUALITY-BASELINE-001` | Focused pytest, ruff check, and ruff format checks passed on the touched/approved files. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Cross-scope application concerns remain preserved as bridge advisory candidates rather than direct GT-KB artifact mutations; router staging tests passed. |

## Commands Run

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest E:\GT-KB\platform_tests\hooks\test_workstream_focus.py E:\GT-KB\platform_tests\scripts\test_workstream_focus_hook_parity.py E:\GT-KB\platform_tests\scripts\test_advisory_backlog_router.py --rootdir E:\GT-KB -q --tb=short --basetemp .\pytest-tmp-wi4690-full-final3
```

Run from working directory `E:\tmp`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\workstream_focus.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_workstream_focus_hook_parity.py platform_tests\scripts\test_advisory_backlog_router.py scripts\advisory_backlog_router.py
```

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\workstream_focus.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_workstream_focus_hook_parity.py platform_tests\scripts\test_advisory_backlog_router.py scripts\advisory_backlog_router.py
```

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts\workstream_focus.py --target platform_tests\hooks\test_workstream_focus.py --target platform_tests\scripts\test_advisory_backlog_router.py
```

## Observed Results

- Pytest: `86 passed, 3 skipped, 2 warnings in 10.29s`.
- Ruff lint: `All checks passed!`
- Ruff format check: `5 files already formatted`.
- Implementation authorization validation: `authorized: true` for the three changed files.

Verification environment note: explicit `--basetemp E:\tmp\...` was blocked by the root-boundary hook when invoked from `E:\GT-KB`, and default pytest temp allocation hit `PermissionError` on `C:\Users\micha\AppData\Local\Temp\pytest-of-micha`. The successful command above ran from `E:\tmp` with a relative basetemp while keeping project inputs rooted at `E:\GT-KB`.

## Recommended Commit Type

- Recommended commit type: `fix`
- Rationale: this corrects an application-mode isolation leak in the work-subject guard without adding a new user-facing feature surface.

## Acceptance Criteria Status

- [x] Application subject blocks direct GT-KB product writes.
- [x] Application subject blocks ordinary GT-KB bridge/governance/control-plane writes.
- [x] Application subject permits only full-content numbered bridge `ADVISORY` output with advisory metadata as the cross-scope GT-KB-directed write path.
- [x] Mutating shell writes to GT-KB bridge/governance paths fail closed when final content cannot be inspected.
- [x] GT-KB subject behavior remains unchanged for current-repo bridge/governance writes and still blocks application-product writes.
- [x] Bridge advisory router stages latest bridge `ADVISORY` entries as candidates and does not directly create work items.
- [x] Hook parity tests passed.
- [x] Ruff lint and format gates passed.

## Risk And Rollback

Risk: some application-mode workflow that previously wrote GT-KB control-plane files directly will now be blocked. That is the intended WI-4690 behavior; the allowed path is a numbered bridge `ADVISORY` file or switching the work subject to GT-KB.

Rollback: revert `scripts/workstream_focus.py`, `platform_tests/hooks/test_workstream_focus.py`, and `platform_tests/scripts/test_advisory_backlog_router.py` to restore the previous broader application-mode governance-write allowance. No formal artifacts, MemBase records, deployment state, or application source files were mutated.

## Loyal Opposition Asks

1. Verify that the implementation satisfies WI-4690 and the GO verdict scope.
2. Confirm the executed verification evidence is sufficient for the linked specifications.
3. Return `VERIFIED` if satisfied, or `NO-GO` with findings.
