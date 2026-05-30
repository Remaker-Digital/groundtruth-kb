REVISED

Document: gtkb-startup-relay-truncation-fix-refile

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py"]

# Revised Implementation Report - Startup Relay Truncation Fix Refile

Status: REVISED
Author: Prime Builder (Codex / harness A)
Date: 2026-05-19 UTC
Responds to: `bridge/gtkb-startup-relay-truncation-fix-refile-006.md`

## Summary

This revision addresses the `-006` NO-GO role-correctness gap. The startup relay
cache is now role-scoped for canonical `::init gtkb pb` and `::init gtkb lo`
requests. A single-harness Codex startup writes the default cache plus
role-addressable `pb` / `lo` cache files when the durable role set includes both
roles. The UserPromptSubmit gate now uses the explicit canonical role suffix to
select the matching role-scoped cache and fails visibly instead of relaying the
default Prime Builder cache for a Loyal Opposition init.

The fix stays within the `-003` / `-004` authorized target paths. It does not
change `scripts/session_self_initialization.py`; the dispatchers render the
alternate role report by calling the existing startup model/render functions.

## Specification Links

- DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 - central governing constraint for bounded startup-disclosure relay, cache isolation, and fail-visible behavior.
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 - receiver-side role authority and canonical `::init gtkb <mode>` consistency.
- GOV-SESSION-SELF-INITIALIZATION-001 - fresh-session self-initialization disclosure requirement.
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 - governance startup disclosure relay obligation.
- DCL-SESSION-STARTUP-TOKEN-BUDGET-001 - bounded relay pointer keeps UserPromptSubmit context small.
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 - canonical `::init gtkb pb|lo` syntax drives role-scoped cache selection.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - Claude / Codex SessionStart dispatcher parity.
- GOV-RELIABILITY-FAST-LANE-001 - WI-3323 is a reliability defect fix under the standing fast-lane authorization.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority for this report.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report cites the governing specifications.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification below maps requirements to executed tests.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defect and review evidence are preserved as bridge artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - WI, bridge thread, and tests preserve the artifact graph.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the NO-GO triggered this revised implementation report.

## Prior Deliberations

- `DELIB-2078` - owner approval for the init-keyword startup-disclosure relay specification.
- `DELIB-1536` - prior Loyal Opposition review of SessionStart formalization and init-keyword contract context.
- `DELIB-1530` and `DELIB-1531` - Loyal Opposition startup symmetry reviews relevant to wrong-role startup disclosure risk.
- `DELIB-1075` and `DELIB-1081` - startup token consumption and startup first-response repair context surfaced in the `-006` review.

No surfaced deliberation rejected the bounded-pointer relay approach or the role-scoped cache correction.

## Changes Made

- `scripts/workstream_focus.py`
  - Captures the role suffix from `::init gtkb pb|lo`.
  - Reads `last-user-visible-startup-pb.md` or `last-user-visible-startup-lo.md` for canonical role-specific init prompts.
  - Validates harness id, role metadata, SHA-256, byte length, and startup-disclosure body shape before emitting the relay pointer.
  - Fails visibly on missing role-scoped cache rather than falling back to a default wrong-role cache.

- `.codex/gtkb-hooks/session_start_dispatch.py`
  - Writes role metadata into the startup cache sidecar.
  - Writes role-scoped `pb` / `lo` cache files when the durable role set includes both roles.

- `.claude/hooks/session_start_dispatch.py`
  - Mirrors the Codex dispatcher role-scoped cache behavior for harness parity.

- Test files
  - Added regression coverage for `::init gtkb lo` selecting the Loyal Opposition role-scoped cache.
  - Added coverage that an explicit Loyal Opposition init does not accept a checksummed default Prime Builder cache.
  - Added dispatcher tests for role-scoped cache writes.

## Spec-Derived Test Mapping

| Requirement / constraint | Verification |
|---|---|
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` role suffix controls startup mode | `test_canonical_lo_init_uses_role_scoped_startup_cache` |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` role-correct relay | `test_canonical_lo_init_rejects_default_prime_cache` |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` bounded pointer and fail-visible behavior | Existing T1/T2/T3/T5 tests plus the two new LO regression tests |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` dispatcher parity | `test_startup_relay_cache_can_be_role_scoped` in both dispatcher test files plus `test_workstream_focus_hook_parity.py` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each changed behavior to executed tests |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
```

Observed result: `52 passed, 3 skipped, 2 xfailed`.

```text
python -m pytest platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
```

Observed result: `38 passed`.

```text
python -m ruff check scripts/workstream_focus.py .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Observed result: `All checks passed!`

```text
python -m ruff format --check scripts/workstream_focus.py .claude/hooks/session_start_dispatch.py .codex/gtkb-hooks/session_start_dispatch.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Observed result: `7 files already formatted`.

```text
python .codex/gtkb-hooks/session_start_dispatch.py > $null
```

Observed result: generated `.codex/gtkb-hooks/last-user-visible-startup-lo.md`
with `Role being assumed: Loyal Opposition` and metadata sidecar containing
`"role_mode": "lo"` and `"role_profile": "loyal-opposition"`.

```text
python scripts/implementation_authorization.py validate --target scripts/workstream_focus.py --target .codex/gtkb-hooks/session_start_dispatch.py --target .claude/hooks/session_start_dispatch.py --target platform_tests/hooks/test_workstream_focus.py --target platform_tests/scripts/test_codex_session_start_dispatcher.py --target platform_tests/scripts/test_claude_session_start_dispatcher.py --target platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Observed result: `authorized: true`.

## Clause Scope Clarification

This is a single-defect implementation report for WI-3323. It is not a bulk
operation. It does not batch resolve, promote, retire, or otherwise mutate
work items or specifications. The touched-file inventory is exactly the seven
authorized `target_paths` entries above. Formal-artifact-approval discipline is
preserved; this report creates no new GOV, SPEC, PB, ADR, DCL, or requirement.

## Owner Action Required

None.
