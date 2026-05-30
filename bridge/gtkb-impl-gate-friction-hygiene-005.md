NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# GT-KB Bridge Implementation Report - gtkb-impl-gate-friction-hygiene - 005

bridge_kind: implementation_report
Document: gtkb-impl-gate-friction-hygiene
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-impl-gate-friction-hygiene-004.md
Approved proposal: bridge/gtkb-impl-gate-friction-hygiene-003.md
Date: 2026-05-20 UTC

## Implementation Claim

Implemented the approved narrowed WI-3310 friction-hygiene scope for `scripts/implementation_start_gate.py`:

- IP-1: added explicit target regression fixtures for `>NUL`, `2>NUL`, `>$null`, `2>$null`, `&>/dev/null`, and same-family real-file redirects.
- IP-2: changed the blocking reason format to include the governing clause id, a `Reason:` line naming the matched protected-prefix or target classification, and a `Suggested fix:` line pointing to the implementation authorization command.
- IP-3: added `--diagnostic` CLI mode. It reads the same stdin payload and runs the same `gate_decision()` path, but prints diagnostic JSON instead of a hook `permissionDecision` envelope.

The older `gtkb-implementation-gate-friction-hygiene` thread and its latest `-018` NO-GO were not edited or closed by this work.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate enforces protected implementation mutation authorization.
- `GOV-ARTIFACT-APPROVAL-001` - protected-mutation evidence requirement; the gate is one mechanical enforcement surface.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface; `--diagnostic` is deterministic self-check output.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping and executed-results requirement.
- `GOV-STANDING-BACKLOG-001` - WI-3310 tracked.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle trigger discipline.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization covering WI-3310.

## Owner Decisions / Input

No new owner decision was required. This implementation carries forward the active `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` authorization for WI-3310 and the GO verdict at `bridge/gtkb-impl-gate-friction-hygiene-004.md`.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 project authorization covering WI-3310.
- `bridge/gtkb-impl-gate-friction-hygiene-003.md` - approved revised proposal.
- `bridge/gtkb-impl-gate-friction-hygiene-004.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-implementation-gate-friction-hygiene-018.md` - older WI-3310 thread's still-open NO-GO. This implementation does not resolve, narrow, waive, or close that separate obligation.

## Specification-Derived Verification Plan

| Spec / behavior | Executed verification evidence |
| --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `GOV-ARTIFACT-APPROVAL-001` | `test_block_reason_includes_clause_and_suggestion`, `test_real_file_redirect_still_blocked`, and the full target suite passed. |
| Null-sink allowlist forms from IP-1 | `test_null_sink_nul_forms_allowed`, `test_null_sink_dollar_null_allowed`, and `test_null_sink_amp_dev_null_allowed` passed as part of the full target suite. |
| `SPEC-AUQ-POLICY-ENGINE-001` deterministic self-check behavior | `test_diagnostic_mode_no_emit` and `test_diagnostic_matches_enforce` passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full canonical target command passed: 112 collected tests, 112 passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report is filed as a new bridge version; prior bridge files were not edited. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implemented changes are under `E:\GT-KB` and within the GO target paths. |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-impl-gate-friction-hygiene`
- `python -m pytest platform_tests\scripts\test_implementation_start_gate.py -q --tb=short`
- `python -m ruff check scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_start_gate.py`
- `python -m ruff format --check scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_start_gate.py`
- `python -m ruff format scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_start_gate.py`
- `git diff --check -- scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_start_gate.py`
- `git diff -- scripts\implementation_start_gate.py`
- `git diff -- platform_tests\scripts\test_implementation_start_gate.py`

## Observed Results

- Implementation authorization packet created for latest `GO`, packet hash `sha256:b1e3f0950ef050878db8dd34e8e0938a63e110e2d9fcadfa253c98323ec4ad1e`.
- Before formatting, the target pytest command passed: 112 passed, 1 warning in 12.87s.
- Ruff check passed.
- Ruff format check initially reported both touched files would be reformatted; `python -m ruff format` reformatted those authorized files.
- After formatting, the target pytest command passed again: 112 passed, 1 warning in 12.96s.
- After formatting, Ruff check passed and Ruff format check reported `2 files already formatted`.
- `git diff --check` for the two authorized target files returned no whitespace errors.
- The only pytest warning observed was an unrelated `chromadb` deprecation warning about `asyncio.iscoroutinefunction`.

## Files Changed

Thread-authorized implementation files changed:

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

Live bridge filing changes from this report:

- `bridge/gtkb-impl-gate-friction-hygiene-005.md`
- `bridge/INDEX.md`

Note: `platform_tests/scripts/test_implementation_start_gate.py` already had local dirty hunks before this thread began, including FD-duplication and sqlite safe-read regression fixtures. Those pre-existing hunks were preserved; this report's claim is limited to the IP-1/IP-2/IP-3 changes listed above and the verification of the full target file after formatting.

The globally dirty worktree contains unrelated pending changes from other bridge slices; they are not part of this implementation claim.

## Acceptance Criteria Status

- [x] IP-1 landed with named null-sink and real-file redirect fixtures.
- [x] IP-2 landed with clause id, protected target classification, and suggested authorization fix in the block reason.
- [x] IP-3 landed with `--diagnostic` mode.
- [x] `platform_tests/scripts/test_implementation_start_gate.py` passes: 112 passed.
- [x] Ruff check and format check pass for the touched files.
- [x] Old `gtkb-implementation-gate-friction-hygiene` thread files and INDEX status were not edited by this implementation.

## Risk And Rollback

Risk: diagnostic JSON becomes another output contract. Mitigation: tests pin that diagnostic mode uses the same enforce-mode decision and avoids hook `permissionDecision` output.

Risk: the clearer block reason may affect string-match consumers. Existing tests that only require the authorization-packet phrase still pass, and new tests pin the more structured output.

Rollback: revert the changes in the two authorized target files. No database or durable state was changed.

## Loyal Opposition Asks

1. Verify the IP-1/IP-2/IP-3 implementation against the approved narrowed GO scope.
2. Confirm the diagnostic mode does not emit a hook block envelope.
3. Confirm the older `gtkb-implementation-gate-friction-hygiene` NO-GO remains independent and untouched.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
