GO

# Loyal Opposition Review - Claude SessionStart Hook Parity

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed proposal: `bridge/gtkb-claude-session-start-parity-001.md`
Skill used: `harness-parity-review`
Verdict: GO

## Claim

The proposal is approved for implementation. The investigated defect is real:
Claude's configured SessionStart command emits a flat `additionalContext`
envelope, while the canonical startup service has a separate
`--emit-startup-service-payload` path that emits the SessionStart
`hookSpecificOutput` envelope. The proposed Claude-side dispatcher, timeout
alignment, and harness-parity import repair are scoped and testable.

## Applicability Preflight

- packet_hash: `sha256:e2a87501c7d2878622665c580fda09e55355672a1a922e793405cb17f39c8d08`
- bridge_document_name: `gtkb-claude-session-start-parity`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-session-start-parity-001.md`
- operative_file: `bridge/gtkb-claude-session-start-parity-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Evidence

- `.claude/settings.json` currently invokes
  `python "$CLAUDE_PROJECT_DIR/scripts/session_self_initialization.py" --emit-report --fast-hook --harness-name claude`
  with `timeout: 15`.
- Running that command produced top-level JSON key `additionalContext`, no
  `hookSpecificOutput`, and included
  `No module named 'scripts.check_harness_parity'`.
- `scripts/session_self_initialization.py:5366` through `:5367` is the flat
  `_emit_hook_context()` path: `{"additionalContext": text}`.
- Running `python scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook --harness-name claude`
  produced top-level `hookSpecificOutput`, `hookEventName: SessionStart`, and
  context containing `Programmatic Startup Payload`; it still reproduced the
  harness-parity import error, so Change 3 remains necessary.
- `scripts/session_self_initialization.py:5608` through `:5618` is the canonical
  startup-service payload path with `hookSpecificOutput`.
- `.codex/gtkb-hooks/session_start_dispatch.py` already provides the validated
  dispatcher pattern: persistent harness id resolution, freshness-contract
  validation, diagnostic file writes, and fail-soft fallback context.

## Harness Parity Review Summary

- Overall status: PASS.
- Checked role/harness: Claude as `prime-builder`.
- Missing role-critical capabilities: none in live checker output.
- Degraded fallbacks: none in live checker output.
- Stale adapters: none in live checker output.
- Undeclared extras: none in live checker output.
- Verification:
  - `python scripts/check_harness_parity.py --harness claude --role prime-builder --json` -> PASS, `PASS: 20`.
  - `python scripts/check_harness_parity.py --all --markdown` -> PASS, `PASS: 50`.

## Gate Checks

- Specification-linkage gate: PASS. The proposal cites startup governance,
  token-budget, bridge authority, mandatory spec-linkage, verified-testing,
  root-boundary/isolation, and artifact-governance authorities.
- Test-plan gate: PASS. The proposed tests cover SessionStart envelope shape,
  governance disclosure content, token-budget content, Codex envelope parity,
  root-contained diagnostics, timeout alignment, harness-parity import repair,
  and dispatcher fallback behavior.
- Scope-control gate: PASS. The proposal is scoped to Claude SessionStart,
  timeout alignment, and the canonical service harness-parity field. It does
  not approve Stop/UserPromptSubmit changes, shared dispatcher refactoring,
  deployment, credential action, or external mutation.

## Implementation Conditions

- Do not modify the Claude Stop hook under this `GO`; the proposal explicitly
  leaves Stop-hook envelope review for a later bridge thread if needed.
- Preserve fail-soft behavior: dispatcher failure must still emit a valid
  SessionStart envelope containing degraded startup context.
- The post-implementation report must include executed tests for the new
  dispatcher, timeout alignment, root-contained diagnostic files, fallback
  behavior, and the repaired harness-parity startup field.
- The implementation report must prove
  `python scripts/check_harness_parity.py --all --markdown` remains `PASS`.

## Owner Decision Needed

None. Prime Builder may implement the scoped SessionStart parity fix.

File bridge scan: 1 entry processed.
