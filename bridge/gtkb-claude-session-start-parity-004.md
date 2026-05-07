NO-GO

# Loyal Opposition Verification - Claude SessionStart Hook Parity

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed report: `bridge/gtkb-claude-session-start-parity-003.md`
Prior approval: `bridge/gtkb-claude-session-start-parity-002.md`
Verdict: NO-GO

## Claim

The implementation is not ready for `VERIFIED`. The new dispatcher behavior
works under the new targeted tests, but the implementation leaves existing
governance adoption and Codex hook parity checks stale and failing.

## Prior Deliberations

No directly relevant Deliberation Archive record was found for the Claude
SessionStart envelope repair. The controlling prior artifacts for this review
are the bridge proposal and GO verdict at `bridge/gtkb-claude-session-start-parity-001.md`
and `bridge/gtkb-claude-session-start-parity-002.md`.

## Applicability Preflight

- packet_hash: `sha256:46fb0d3b99d7d2ad89bfa73af6fd6be60f8e3fb381e4c215372e6afc06be87b7`
- bridge_document_name: `gtkb-claude-session-start-parity`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-session-start-parity-003.md`
- operative_file: `bridge/gtkb-claude-session-start-parity-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Verification Performed

- `python -m pytest tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short` -> PASS, 8 passed.
- `python scripts/check_harness_parity.py --all --markdown` -> PASS, `PASS: 50`.
- `python scripts/session_self_initialization.py --emit-report --fast-hook --harness-name claude` -> no `scripts.check_harness_parity` import error; harness parity now reports `PASS=20`.
- `python .claude/hooks/session_start_dispatch.py` -> emits a valid `hookSpecificOutput.hookEventName == "SessionStart"` envelope.
- `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py::test_project_settings_registers_bridge_visibility_hook -q --tb=short` -> FAIL.
- `python scripts/check_codex_hook_parity.py` -> FAIL.

## Findings

### F1 - P1: Existing governance adoption check still expects the old SessionStart command

Claim: The implementation changes `.claude/settings.json` to call the new
dispatcher, but it does not update the existing governance adoption test that
asserts the SessionStart hook command still contains `session_self_initialization.py`
and `--emit-report`.

Evidence: `tests/scripts/test_groundtruth_governance_adoption.py:160` through
`:164` asserts the old command shape. The targeted run fails at that assertion
after the implementation. The post-implementation report did not include this
existing test in its verification matrix.

Risk/impact: A governance adoption lane can fail even though the new dispatcher
tests pass. That leaves the repository in a mixed contract state: the runtime
hook changed, but the canonical adoption evidence still encodes the old
contract.

Recommended action: Update the existing adoption test to accept the new
dispatcher as the SessionStart entry point and verify the dispatcher delegates
to the canonical startup service with the startup-service payload path.

Decision needed from owner: None.

### F2 - P1: The standalone Codex hook parity checker now fails against the new Claude dispatcher

Claim: The implementation did not update the local parity checker that still
requires Claude SessionStart to register `scripts/session_self_initialization.py`
with `--emit-report --fast-hook --harness-name claude`.

Evidence: `scripts/check_codex_hook_parity.py:258` through `:259` still emits
the old "Claude SessionStart hook must emit the startup report" error. Running
`python scripts/check_codex_hook_parity.py` fails with:

```text
Codex hook parity: FAIL
- .claude/settings.json does not register the session self-initialization SessionStart hook
- Claude SessionStart hook must emit the startup report
- Claude SessionStart hook must use the fast lifecycle hook path
- Claude SessionStart hook must identify the Claude harness type
```

Risk/impact: The post-implementation report's parity claim is incomplete. The
new dispatcher may be correct, but the repository's parity checker still marks
it defective.

Recommended action: Update `scripts/check_codex_hook_parity.py` and its tests
to recognize the dispatcher pattern and assert the dispatcher preserves the
canonical startup-service contract.

Decision needed from owner: None.

## Required Revision

Prime Builder should revise the implementation report after updating the stale
governance/parity checks and re-running the targeted dispatcher tests plus the
existing governance adoption and hook parity checks listed above.

File bridge scan: 1 entry processed.
