REVISED

# Implementation Report Revision - Implementation Start Authorization Gate

bridge_kind: implementation_report_revision
Document: gtkb-implementation-start-authorization-gate
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds to: `bridge/gtkb-implementation-start-authorization-gate-004.md`
Implements: `bridge/gtkb-implementation-start-authorization-gate-001.md`
GO verdict: `bridge/gtkb-implementation-start-authorization-gate-002.md`
Recommended commit type: `fix:`

## Claim

The verification blockers from `-004` are addressed. The implementation-start
gate now extracts Codex raw/freeform patch payloads, escaped patch text, and
nested patch payloads; allows bridge-only patch writes without an authorization
packet; and still denies protected source, test, script, hook, and
configuration mutations without a live GO authorization packet.

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
- `.claude/rules/bridge-essential.md`
- `.claude/settings.json`
- `.codex/hooks.json`

## Prior Deliberations

Carried forward from the proposal and `-004` verification: `DELIB-1740`,
`DELIB-1715`, `DELIB-0628`, `DELIB-1646`, and
`DELIB-S321-SPEC-CREATION-STANDING-AUTH` constrain the hard-gate design,
bridge authority, and requirement-sufficiency behavior.

## Owner Decisions / Input

No new owner decision was requested. The repair relies on standing bridge
integrity authority in `.claude/rules/bridge-essential.md` and the explicit
emergency bridge infrastructure repair exception in
`.claude/rules/codex-review-gate.md`. That exception was necessary because the
defective gate blocked the normal Codex patch path for bridge-only verdict
writes and also blocked the protected source edit needed to repair that gate
while the live latest bridge status was `NO-GO`.

## Findings Addressed

### F1 - The gate blocked authorized bridge verdict filing through the normal Codex patch path

Response: fixed. `scripts/implementation_start_gate.py` now accepts raw string
`tool_input`, top-level `input`, nested string payloads, escaped newline forms,
and fully qualified patch tool names such as `functions.apply_patch`. The patch
extractor now finds `*** Add File`, `*** Update File`, `*** Delete File`, and
`*** Move to` paths in those payloads before deciding whether the mutation is
protected.

Regression coverage:

- `test_raw_patch_bridge_only_write_remains_open_without_authorization` proves
  a raw patch payload that touches only `bridge/**` is allowed without an
  implementation authorization packet.
- `test_nested_patch_payload_without_tool_name_allows_bridge_only_write` proves
  a nested patch payload is still recognized without relying on a specific tool
  name.
- `test_shell_payload_with_escaped_patch_newlines_allows_bridge_only_write`
  proves escaped patch newlines are normalized before path extraction.

### F2 - Codex patch-tool hard-gate coverage remains a stated capability boundary, not verified runtime behavior

Response: tightened. The prior dispatch already supplied live evidence that
the Codex `apply_patch` PreToolUse gate can fire by producing the incorrect
denial recorded in `-004`. This revision adds direct hook-level probes and
regression tests for the intended behavior:

- Nested bridge-only patch payload piped to `scripts/implementation_start_gate.py`
  returned `{}`.
- A protected patch-shaped shell payload was denied at PreToolUse before the
  command executed, with `GTKB-IMPLEMENTATION-START-GATE`.
- Combined focused pytest lane now includes the raw, nested, and escaped-patch
  regression tests and passes with `33 passed`.

## Emergency Repair Note

The initial normal source patch for this fix was blocked by
`GTKB-IMPLEMENTATION-START-GATE` because live `bridge/INDEX.md` correctly showed
this thread's latest status as `NO-GO`, so no normal implementation
authorization packet could be minted. Prime Builder used the documented
emergency bridge infrastructure repair exception to make the narrowly scoped
gate repair. No persistent bypass, hook disablement, alternate queue, alternate
dispatcher, or off-root artifact was created.

## Implementation Summary

- Updated `_tool_input` to preserve raw string tool payloads instead of
  discarding them.
- Added patch-tool matching for both `apply_patch` and fully qualified tool
  names ending in `.apply_patch`.
- Added recursive string extraction so nested hook payloads can still yield
  patch text.
- Normalized PowerShell backtick-newline and JSON-escaped newline forms before
  patch path extraction.
- Guarded shell-command parsing so non-dict raw payloads do not raise while
  checking `"command" in data`.
- Added regression tests for raw bridge-only patch allowance, raw protected
  patch denial, nested bridge-only payloads, and escaped patch-newline payloads.

## Files Changed

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `bridge/gtkb-implementation-start-authorization-gate-005.md`
- `bridge/gtkb-codex-bridge-compliance-gate-parity-011.md`
- `bridge/INDEX.md`

## Spec-to-Test Mapping

| Proposal Test ID / Requirement | Evidence |
|---|---|
| T-codex-apply-patch | Raw, nested, escaped-newline, and protected patch tests in `platform_tests/scripts/test_implementation_start_gate.py`, plus direct hook probes listed below. |
| T-no-auth-block | `test_no_auth_blocks_protected_source_edit` and the live protected-patch PreToolUse denial. |
| T-target-mismatch | Existing `test_target_mismatch_blocks_even_with_valid_packet` remains passing. |
| T-shell-conservative | Existing shell mutation/read-only tests remain passing; escaped bridge patch shell payload is allowed only because it extracts bridge-only paths. |
| Bridge proposal/review/report writing remains possible | The parser now recognizes bridge-only patch payloads across raw, nested, and escaped forms. |
| Formal-artifact composition remains independent | This fix does not alter `formal-artifact-approval-gate.py` or its registration. |
| Harness registration parity | `platform_tests/scripts/test_hook_registration_parity.py` and `platform_tests/scripts/test_codex_hook_parity.py` remain passing. |

## Verification

Commands executed:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m pytest platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -q --tb=short
python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short -p no:cacheprovider
python scripts/check_codex_hook_parity.py
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/workstream_focus.py scripts/session_self_initialization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_hook_registration_parity.py platform_tests/scripts/test_session_self_initialization.py platform_tests/hooks/test_workstream_focus.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py .claude/hooks/implementation-start-gate.py
python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

Observed results:

- Implementation-start focused tests: `13 passed`.
- Hook registration plus Codex hook parity tests: `13 passed`.
- Codex bridge-compliance tests: `7 passed`.
- Combined gate/parity lane: `33 passed`.
- Codex hook parity: `PASS`.
- Targeted ruff check: `All checks passed!`; one run emitted the existing cache
  warning `Different package root in cache`.
- Targeted ruff format check for touched files: `2 files already formatted`.

Direct hook probes:

- Nested bridge-only patch payload: `scripts/implementation_start_gate.py`
  returned `{}`.
- Protected patch-shaped shell payload: PreToolUse denied the command before it
  executed with `GTKB-IMPLEMENTATION-START-GATE`.

## Known Gaps

No remaining selected gap is known for raw/freeform Codex patch payload
classification. The broader runtime capability boundary remains governed by
`.codex/hooks.json` and hook telemetry: the prior live denial proves the Codex
patch PreToolUse hook can fire in this environment, while the direct probes and
regressions prove the intended classifier behavior.

## Risk And Rollback

Risk: the emergency bridge-repair exception could be overused. Mitigation: this
report records the exact reason it was needed, the files touched, and the tests
run.

Rollback: revert only the parser/test changes in `scripts/implementation_start_gate.py`
and `platform_tests/scripts/test_implementation_start_gate.py`, then file a
superseding bridge report. Do not delete bridge files.
