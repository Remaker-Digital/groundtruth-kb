NEW

# Implementation Report - Implementation Start Authorization Gate

bridge_kind: implementation_report
Document: gtkb-implementation-start-authorization-gate
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: `bridge/gtkb-implementation-start-authorization-gate-001.md`
GO verdict: `bridge/gtkb-implementation-start-authorization-gate-002.md`
Recommended commit type: `feat:`

## Claim

The implementation-start authorization gate is implemented for the selected scope. A shared authorization command creates a session-local packet from a live latest-`GO` bridge thread, and a shared hook denies protected source/config/test/script/hook mutations when the packet is missing, stale, expired, corrupt, or outside the approved `target_paths`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`

## Implementation Summary

- Added `scripts/implementation_authorization.py` to parse live `bridge/INDEX.md`, require latest `GO`, resolve the approved proposal and GO file, validate concrete spec links, validate concrete `target_paths`, require a spec-derived verification plan, enforce requirement-sufficiency behavior with a bootstrap exception for this gate's own pre-rule proposal, and write a hashed expiring packet.
- Added `scripts/implementation_start_gate.py` to classify Write/Edit/MultiEdit, Codex `apply_patch`, and shell/Bash mutation payloads; allow read-only commands and bridge/report writes; deny protected mutations without a valid scoped packet; and fail closed on unclassified mutating commands.
- Added Claude and Codex wrappers and registered the gate in `.claude/settings.json` and `.codex/hooks.json` for supported mutation surfaces.
- Updated bridge/counterpart-review rules and the system interface map so the mechanic is discoverable and auditable.
- Added tests for no-auth block, GO-auth allow, non-GO rejection, target mismatch, requirement-gap rejection, Codex `apply_patch` path extraction, shell mutation classification, bridge write allowance, and registration parity.

## Files Changed

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `.claude/hooks/implementation-start-gate.py`
- `.codex/gtkb-hooks/implementation-start-gate.cmd`
- `.claude/settings.json`
- `.codex/hooks.json`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `config/agent-control/system-interface-map.toml`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_hook_registration_parity.py`

## Spec-to-Test Mapping

| Proposal Test ID | Evidence |
|---|---|
| T-no-auth-block | `test_no_auth_blocks_protected_source_edit` |
| T-go-auth-allows | `test_go_authorization_packet_allows_in_scope_apply_patch` |
| T-non-go-block | `test_non_go_bridge_entry_cannot_create_authorization` |
| T-target-mismatch | `test_target_mismatch_blocks_even_with_valid_packet` |
| T-requirement-gap-block | `test_requirement_gap_blocks_authorization` |
| T-codex-apply-patch | `test_go_authorization_packet_allows_in_scope_apply_patch` and target mismatch test parse apply_patch paths. |
| T-shell-conservative | `test_shell_mutation_classification_blocks_protected_write` and `test_read_only_shell_command_is_allowed_without_authorization` |
| T-formal-artifact-composition | The gate documentation and implementation explicitly do not satisfy or disable formal-artifact approval; formal gate remains registered separately. |
| T-registration-parity | `platform_tests/scripts/test_hook_registration_parity.py` and `platform_tests/scripts/test_codex_hook_parity.py` |

## Verification

Commands executed:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py -q --tb=short
python scripts/implementation_authorization.py --project-root E:\GT-KB begin --bridge-id gtkb-implementation-start-authorization-gate --no-write
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py groundtruth-kb/tests/test_project_artifacts.py -q --tb=short
python scripts/check_codex_hook_parity.py
python -c "import json, pathlib; json.load(open('.claude/settings.json', encoding='utf-8')); json.load(open('.codex/hooks.json', encoding='utf-8')); print('json ok')"
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py .claude/hooks/implementation-start-gate.py
python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py .claude/hooks/implementation-start-gate.py
git diff --check
```

Observed results:

- `11 passed`
- Authorization dry run emitted a scoped packet for latest `GO`, including `requirement_sufficiency: bootstrap_pre_rule` for this one-time pre-rule bootstrap proposal.
- `21 passed`
- `13 passed`
- `18 passed, 1 warning`
- `Codex hook parity: PASS`
- `json ok`
- Targeted ruff check: `All checks passed!`
- Targeted ruff format check: `11 files already formatted`
- `git diff --check` passed; output contained only normal CRLF conversion warnings.

## Known Gaps

- The gate registers a Codex `PreToolUse` entry for `apply_patch` and includes tests for apply-patch payload parsing. Whether the Codex runtime actually invokes `PreToolUse` before `apply_patch` must be treated as a harness capability boundary until observed in live hook telemetry.
- Formal-artifact approval remains a separate hard gate and was not weakened or replaced by this packet.
- Broad `ruff check scripts platform_tests .claude/hooks groundtruth-kb/src/groundtruth_kb groundtruth-kb/tests` is not clean in this dirty worktree due to unrelated pre-existing findings across legacy hooks, scripts, MCP surface files, and unrelated tests. Targeted files for this bridge slice are clean.
