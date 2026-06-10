NEW

# Implementation Proposal - Implementation Start Gate Repository Finalization Deadlock Fix

bridge_kind: prime_proposal
Document: gtkb-implementation-start-gate-repository-finalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Recommended commit type: fix:
target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Claim

Fix a deadlock in the implementation-start gate where fully verified bridge work cannot be committed or pushed because `git commit` and `git push` are classified as protected implementation-start mutations that require a live latest-`GO` authorization packet.

The correction is narrow: allow simple repository finalization commands through this PreToolUse gate when they are standalone git commands, while continuing to block chained commands that include protected file writes or other shell mutation after the git command. This keeps the implementation-start boundary focused on starting or performing protected source, configuration, test, script, and hook mutations, not on finalizing already-staged and already-verified work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` remains authoritative for implementation lifecycle state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing requirements before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include spec-derived test evidence before `VERIFIED`.
- `.claude/rules/codex-review-gate.md` - implementation requires bridge approval before protected source, configuration, test, script, and hook work; repository finalization must not bypass review, but it also must not deadlock after review is complete.
- `.claude/rules/file-bridge-protocol.md` - implementation reports carry recommended commit type and are verified before closure; the final commit and push are repository transport steps after the bridge lifecycle evidence exists.
- `bridge/gtkb-implementation-start-authorization-gate-010.md` - verified implementation-start gate behavior and current acceptance criteria requiring post-`VERIFIED` protection against new implementation work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB work remains under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the bridge proposal, verification, and finalization steps remain durable artifacts in the governed lifecycle.

## Requirement Sufficiency

Existing requirements sufficient. The verified gate requirements already distinguish implementation-start protection from bridge lifecycle closure. No new GOV/ADR/DCL/SPEC is required to correct a false-positive deadlock in the gate's shell-command classifier.

## Owner Decisions / Input

- Current owner directive: "Please clean up the dirty worktree and commit, then push to GitHub."
- Blocking observation: the implementation-start gate blocks `git commit` after relevant bridge threads have reached `VERIFIED`, because the live packet validator requires latest `GO`.
- This proposal does not request approval for deployment, production release, history rewrite, formal artifact mutation, or any alternate bridge runtime.

## Prior Deliberations

- `bridge/gtkb-implementation-start-authorization-gate-010.md` verified the gate and records the current intent: block new protected implementation after terminal `VERIFIED` unless a new GO'd proposal authorizes new work.
- `bridge/gtkb-projects-skill-001-007.md`, `bridge/gtkb-formal-artifact-approval-hook-false-positive-fix-001-007.md`, and related verified bridge records show the current worktree has already completed bridge verification for the relevant implementation threads.
- Prior bridge architecture discussions treat direct git commits as a known enforcement path, but the active implementation-start hook is a PreToolUse implementation-start guard, not the only commit-time governance layer.

## Problem Statement

`git commit -m "..."` is currently matched by `MUTATING_COMMAND_RE`. The command text contains no protected file path, so `changed_paths()` returns `mutating=True` with no paths. `gate_decision()` substitutes `<unknown-mutating-target>` and calls `validate_targets()`, which then rejects the current packet because the latest bridge status is now `VERIFIED`, not `GO`.

That behavior blocks the normal governed sequence:

1. implementation proposal receives `GO`;
2. Prime implements and files an implementation report;
3. Loyal Opposition verifies and writes `VERIFIED`;
4. Prime commits and pushes the verified staged work.

The gate should still block new protected source, configuration, test, script, and hook mutation after `VERIFIED`; it should not block simple repository transport commands that do not themselves write protected files.

## Proposed Implementation

1. Add a small classifier for standalone git finalization commands:
   - allow `git commit ...` and `git push ...` when the command is a simple git invocation;
   - reject the safe classification if shell chaining or control markers are present, such as `;`, `&&`, `||`, `|`, command substitution, or backtick execution.
2. Call this classifier from `_is_safe_command()` before the existing safe-prefix list.
3. Add tests proving:
   - simple `git commit -m "..."` is allowed without an implementation authorization packet;
   - simple `git push origin develop` is allowed without an implementation authorization packet;
   - chained `git commit ...; Set-Content scripts/sample.py ...` is still blocked.

## Specification-Derived Verification Plan

| Test ID | Requirement | Verification |
|---|---|---|
| T-finalize-commit | `.claude/rules/file-bridge-protocol.md` post-verification commit transport | `test_git_commit_finalization_command_is_allowed_without_authorization` |
| T-finalize-push | owner-requested GitHub transport after verified work | `test_git_push_finalization_command_is_allowed_without_authorization` |
| T-chain-block | implementation-start gate must still block protected shell mutation | `test_chained_git_commit_with_protected_write_still_blocks` |
| T-existing-gate | `GOV-FILE-BRIDGE-AUTHORITY-001` and gate regressions | Run the existing implementation-start gate test file. |

Expected commands:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

## Acceptance Criteria

- `git commit -m "..."` no longer fails this PreToolUse gate solely because the current implementation authorization packet's bridge thread is `VERIFIED`.
- `git push origin develop` no longer fails this PreToolUse gate solely because the current implementation authorization packet's bridge thread is `VERIFIED`.
- Chained or compound shell commands that include protected mutations after a git finalization command still require authorization and still block without it.
- Existing tests for no-auth protected writes, target mismatch, latest-status drift, bridge writes, and read-only commands still pass.
- No formal artifact approval behavior is changed.

## Risk / Rollback

Risk: allowing git finalization in this PreToolUse hook could be misread as allowing unreviewed implementation to be committed. Mitigation: only standalone git finalization commands are allowed; actual protected writes remain gated at write/start time, and repository-level pre-commit/CI gates remain separate enforcement layers.

Rollback: remove the standalone git finalization classifier and tests, returning to the current behavior where commit and push are treated as protected unknown-target shell mutations.

## Out of Scope

- Changing `.githooks/pre-commit` behavior.
- Changing formal artifact approval.
- Allowing chained shell commands after git finalization.
- Deployment, tag creation, release, merge, rebase, reset, or history rewrite.
- Broad rewrite of staged-path authorization for all git subcommands.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
