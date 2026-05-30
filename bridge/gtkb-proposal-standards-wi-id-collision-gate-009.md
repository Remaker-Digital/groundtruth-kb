NEW

# GT-KB Bridge Implementation Report - Proposal-Standards WI-ID Collision Gate - 009

bridge_kind: implementation_report
Document: gtkb-proposal-standards-wi-id-collision-gate
Version: 009 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-proposal-standards-wi-id-collision-gate-008.md
Approved proposal: bridge/gtkb-proposal-standards-wi-id-collision-gate-007.md
Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE3
Implementation authorization packet: sha256:ae19a1cf205e2a7ffdcf26397956032403f77c1982723e2a9a639d568b00c976
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex Desktop default reasoning

## Implementation Claim

Implemented the approved Slice 3 WI-ID collision gate.

The new engine `scripts/bridge_proposal_wi_id_collision_check.py` scans bridge proposal content for `GTKB-[A-Z]+-NNN` and `WI-NNNN` IDs outside fenced code blocks, parses the declared `Work Item:` metadata, checks cited IDs against MemBase `current_work_items`, and reports collisions when an existing cited WI differs from the declared WI. The CLI emits Markdown by default, JSON with `--json`, exits 0 by default, and exits non-zero only with `--strict` when collisions are present.

The Claude hook `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` is registered on the existing `.claude/settings.json` `PreToolUse` `Write|Edit` matcher. It scans `content` for `Write`, `new_string` for `Edit`, acts only on `bridge/<slug>-NNN.md`, emits an advisory `additionalContext` warning when collisions are found, and does not emit a block/deny decision. It fails open with a diagnostic if MemBase is unavailable.

The Codex Bash surface is covered by `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`, invoked by `.codex/gtkb-hooks/wi-id-collision-gate.cmd` and registered in `.codex/hooks.json` under a `Bash` matcher. The adapter extracts common bridge-write shapes, including heredoc writes, synthesizes a Claude-shaped `Write` payload, and delegates to the canonical Claude hook. Codex `apply_patch` coverage remains explicitly out of scope per the approved `-007` proposal.

The two hook config files already had unrelated dirty diffs before this slice. This implementation preserved those existing edits and only claims the new WI-ID collision registrations: `.claude/settings.json:25` and `.codex/hooks.json:102`.

When filed, the bridge helper inserted `NEW: bridge/gtkb-proposal-standards-wi-id-collision-gate-009.md` at the top of the live `bridge/INDEX.md` entry for this document. Prior versions remain preserved in the version chain.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the hook protects bridge proposal integrity before review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal-internal WI references are checked against the declared work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specs to executed tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files are inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the engine reads `current_work_items` as the standing-backlog authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Claude and Codex Bash hook surfaces are both covered; `apply_patch` remains a deferred follow-on.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this governed enforcement artifact is captured by bridge proposal/report flow.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, bridge thread, engine, hooks, config registrations, and tests form a traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the hook fires during the bridge proposal write/edit lifecycle event.

## Owner Decisions / Input

No new owner decision is required. This implementation remains inside the active project authorization and the approved GO scope.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - owner authorization for `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS`, including Slice 3.
- `DELIB-0990`, `DELIB-0991`, and `DELIB-0993` - proposal-standards family context requiring mechanical checks.
- `DELIB-1738` - prior hook-review precedent requiring pending hook content and Edit payload handling to be specified/tested.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-007.md` - approved revised implementation proposal.
- `bridge/gtkb-proposal-standards-wi-id-collision-gate-008.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-STANDING-BACKLOG-001` | `test_collision_detected_on_alien_wi`, `test_no_collision_when_only_declared_wi`, and `test_multiple_collisions_listed` verify MemBase-backed WI collision behavior. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `test_output_json_schema` and the engine tests verify the declared work item is compared with cited work-item IDs. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_hook_fires_on_bridge_proposal_write`, `test_hook_noop_on_non_bridge_path`, `test_hook_fires_on_bridge_proposal_edit`, and `test_hook_no_collision_on_edit` verify the bridge-only Write/Edit hook behavior. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_hook_advisory_does_not_block_on_collision` verifies the hook surfaces lifecycle-time warnings without blocking writes. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_hook_fail_open_on_membase_error`, `test_hook_fail_open_on_membase_error_edit`, `test_codex_adapter_detects_collision_on_bash_write`, and `test_codex_adapter_noop_on_non_bridge_command` verify fail-open and Codex Bash behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_ignore_ids_in_fenced_code_blocks` and `test_edit_without_declared_work_item_reports_no_false_collision` verify low-noise artifact handling. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The focused proposal-standards suite executes 17 tests and reports 17 passing tests. |

## Commands Run

```text
python scripts\implementation_authorization.py validate --target scripts/bridge_proposal_wi_id_collision_check.py --target .claude/hooks/bridge-proposal-wi-id-collision-gate.py --target .claude/settings.json --target .codex/hooks.json --target .codex/gtkb-hooks/wi-id-collision-gate.cmd --target .codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py --target platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py
```

Observed result:

```text
"authorized": true
"targets": [
  "scripts/bridge_proposal_wi_id_collision_check.py",
  ".claude/hooks/bridge-proposal-wi-id-collision-gate.py",
  ".claude/settings.json",
  ".codex/hooks.json",
  ".codex/gtkb-hooks/wi-id-collision-gate.cmd",
  ".codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py",
  "platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py"
]
```

```text
python -m pytest platform_tests\scripts\test_bridge_proposal_wi_id_collision_check.py -v --tb=short
```

Observed result:

```text
collected 17 items
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_collision_detected_on_alien_wi PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_no_collision_when_only_declared_wi PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_multiple_collisions_listed PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_strict_mode_exits_nonzero_on_collision PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_default_exit_zero_on_collision PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_output_json_schema PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_ignore_ids_in_fenced_code_blocks PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_fires_on_bridge_proposal_write PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_noop_on_non_bridge_path PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_advisory_does_not_block_on_collision PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_fail_open_on_membase_error PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_fires_on_bridge_proposal_edit PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_no_collision_on_edit PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_hook_fail_open_on_membase_error_edit PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_edit_without_declared_work_item_reports_no_false_collision PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_codex_adapter_detects_collision_on_bash_write PASSED
platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py::test_codex_adapter_noop_on_non_bridge_command PASSED
17 passed
```

```text
python -m ruff check scripts\bridge_proposal_wi_id_collision_check.py .claude\hooks\bridge-proposal-wi-id-collision-gate.py .codex\gtkb-hooks\wi-id-collision-gate-bash-adapter.py platform_tests\scripts\test_bridge_proposal_wi_id_collision_check.py
```

Observed result:

```text
All checks passed!
```

Ruff also emitted an existing cache-root warning: `Different package root in cache: expected E:\GT-KB\.claude\hooks, got`. This did not indicate a lint failure.

```text
python -m ruff format --check scripts\bridge_proposal_wi_id_collision_check.py .claude\hooks\bridge-proposal-wi-id-collision-gate.py .codex\gtkb-hooks\wi-id-collision-gate-bash-adapter.py platform_tests\scripts\test_bridge_proposal_wi_id_collision_check.py
```

Observed result:

```text
4 files already formatted
```

```text
python -c "import json,pathlib; [json.loads(pathlib.Path(p).read_text()) for p in ('.claude/settings.json','.codex/hooks.json')]"
```

Observed result: exit code 0, no output.

```text
git diff --check -- scripts\bridge_proposal_wi_id_collision_check.py .claude\hooks\bridge-proposal-wi-id-collision-gate.py .claude\settings.json .codex\hooks.json .codex\gtkb-hooks\wi-id-collision-gate.cmd .codex\gtkb-hooks\wi-id-collision-gate-bash-adapter.py platform_tests\scripts\test_bridge_proposal_wi_id_collision_check.py
```

Observed result: exit code 0, no whitespace errors. Git emitted existing Windows line-ending notices for `.claude/settings.json` and `.codex/hooks.json`.

## Files Changed

- `scripts/bridge_proposal_wi_id_collision_check.py` - new shared collision-check engine and CLI.
- `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` - new advisory Claude `Write|Edit` hook.
- `.claude/settings.json` - added only the new Claude hook registration at `.claude/settings.json:25`; pre-existing unrelated dirty diffs were preserved and not claimed.
- `.codex/hooks.json` - added only the new Codex Bash registration at `.codex/hooks.json:102`; pre-existing unrelated dirty diffs were preserved and not claimed.
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd` - new Codex wrapper.
- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py` - new Codex Bash adapter.
- `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py` - new focused regression suite.

## Evidence Anchors

- `scripts/bridge_proposal_wi_id_collision_check.py:27` defines the approved ID pattern.
- `scripts/bridge_proposal_wi_id_collision_check.py:118` implements `check_content()`.
- `scripts/bridge_proposal_wi_id_collision_check.py:148` renders the Collision Check Markdown table.
- `.claude/hooks/bridge-proposal-wi-id-collision-gate.py:21` limits hook scope to `bridge/<slug>-NNN.md`.
- `.claude/hooks/bridge-proposal-wi-id-collision-gate.py:83` implements the hook main path.
- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py:81` extracts common Bash bridge-write shapes.
- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py:100` synthesizes a Claude-shaped `Write` payload.
- `.claude/settings.json:25` registers the Claude hook.
- `.codex/hooks.json:102` registers the Codex Bash wrapper.
- `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py:88` through `:261` cover engine, hook, and adapter behavior.

## Acceptance Criteria Status

- [x] IP-1 landed: shared engine CLI, default advisory exit behavior, `--strict`, JSON output, Markdown output, fenced-code exclusion, and reusable `check_content()`.
- [x] IP-2a landed: Claude `Write|Edit` hook and `.claude/settings.json` registration.
- [x] IP-2b landed: Codex Bash adapter, `.cmd` wrapper, and `.codex/hooks.json` Bash registration.
- [x] IP-3 landed: 17 tests cover engine, Claude hook Write/Edit, Codex Bash adapter, fail-open behavior, and non-blocking advisory output.
- [x] JSON validity check passed for `.claude/settings.json` and `.codex/hooks.json`.
- [x] Focused pytest, Ruff check, Ruff format check, authorization validation, and `git diff --check` pass for the approved slice.
- [x] Codex `apply_patch` coverage remains out of scope and deferred as the GO authorized.

## Risk And Rollback

Residual risk: the Bash adapter supports common write shapes and inherits the same extraction limits as the bridge-compliance Bash adapter pattern. Unrecognized write shapes fail open rather than blocking work.

Rollback: remove the engine, Claude hook, Codex adapter, Codex wrapper, and focused test file, then remove only the new hook registration entries from `.claude/settings.json` and `.codex/hooks.json`. Bridge audit files remain append-only.

## Recommended Commit Type

`feat` - adds a new proposal-standards enforcement capability across the Claude Write/Edit and Codex Bash surfaces.

## Loyal Opposition Asks

1. Verify the implementation against the approved `-007` scope and confirm it does not claim Codex `apply_patch` coverage.
2. Confirm the hook emits advisory additional context and no deny/block decision on collisions.
3. Confirm the existing unrelated dirty config diffs are not part of this slice's implementation claim.
