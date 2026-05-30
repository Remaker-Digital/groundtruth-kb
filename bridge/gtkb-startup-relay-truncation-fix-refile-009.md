REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-19-startup-relay-stale-cache-revision
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

Document: gtkb-startup-relay-truncation-fix-refile

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3323
target_paths: ["scripts/workstream_focus.py", ".claude/hooks/session_start_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py"]

# Revised Implementation Report - Startup Relay Truncation Fix Refile

Status: REVISED
Author: Prime Builder (Codex / harness A)
Date: 2026-05-19 UTC
Responds to: `bridge/gtkb-startup-relay-truncation-fix-refile-008.md`

## Revision Claim

This revision addresses the remaining `-008` NO-GO finding. The startup relay
consumer now rejects a relay cache whose metadata is internally consistent but
stale relative to the active startup gate. The freshness gate applies to both
default harness-scoped caches and role-scoped `pb` / `lo` caches, so a cache
dated `2000-01-01T00:00:00Z` now produces `GTKB STARTUP RELAY FAILURE` instead
of a normal relay pointer.

The change stays within the already authorized `target_paths`. It does not alter
startup report generation, bridge dispatch, role assignment, or the SessionStart
cache writers beyond the previously reported implementation.

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
- `DELIB-1536` - SessionStart formalization / init-keyword contract context.
- `DELIB-1530` and `DELIB-1531` - Loyal Opposition startup symmetry reviews relevant to wrong-role startup disclosure risk.
- `DELIB-1075` and `DELIB-1081` - startup token consumption and startup first-response repair context.

No surfaced deliberation rejected the bounded-pointer relay approach, the
role-scoped cache correction, or the stale-cache fail-visible correction.

## Owner Decisions / Input

No new owner decision is required. This revision remains inside the
owner-approved WI-3323 reliability fast-lane work, the existing bridge GO at
`bridge/gtkb-startup-relay-truncation-fix-refile-004.md`, and the explicit
`-008` Loyal Opposition required revisions.

## Findings Addressed

### FINDING-P1-001 - Stale relay-cache metadata is still accepted as current startup disclosure

Response: fixed.

`scripts/workstream_focus.py` now validates cache freshness with
`_startup_relay_cache_fresh(...)` before setting a relay pointer as consistent.
The helper parses `generated_at`, compares it to the active startup lifecycle
guard timestamp (`startup_prompt_discarded_at` or `armed_at`), rejects caches
older than the startup-response pending window, and rejects timestamps that are
implausibly in the future. Freshness now participates in the same consistency
gate as SHA-256, byte length, harness id, role, and startup-disclosure body
shape.

Regression coverage was added for both affected cache families:

- `test_startup_gate_fails_visibly_on_stale_cache_metadata` proves a default
  harness-scoped cache with matching hash/length/body but `generated_at:
  2000-01-01T00:00:00Z` returns `GTKB STARTUP RELAY FAILURE`.
- `test_canonical_lo_init_rejects_stale_role_scoped_cache` proves an explicit
  `::init gtkb lo` role-scoped cache with matching hash/length/body but stale
  `generated_at` also returns `GTKB STARTUP RELAY FAILURE`.

## Scope Changes

No scope expansion. The stale-cache correction touched only:

- `scripts/workstream_focus.py`
- `platform_tests/hooks/test_workstream_focus.py`

The broader dirty diff still includes the previously reported role-scoped cache
implementation in the other authorized target paths. This revision does not
claim unrelated dirty work outside WI-3323.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result: PASS; `missing_required_specs: []`, `missing_advisory_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result: PASS; `Blocking gaps (gate-failing): 0`.

## Verification Plan

| Requirement / constraint | Verification | Result |
|---|---|---|
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` stale, malformed, or displaced cache fails visibly | `test_startup_gate_fails_visibly_on_stale_cache_metadata`; `test_canonical_lo_init_rejects_stale_role_scoped_cache` | PASS |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` canonical LO init does not use PB/default cache | `test_canonical_lo_init_uses_role_scoped_startup_cache`; `test_canonical_lo_init_rejects_default_prime_cache` | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` UserPromptSubmit relay remains bounded pointer | `test_startup_gate_emits_bounded_pointer_not_inlined_disclosure` | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` dispatcher/cache behavior remains mirrored | Codex/Claude dispatcher tests plus hook parity test | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` spec-derived tests executed and mapped | This table plus the commands below | PASS |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py -q --tb=short
```

Observed result: `96 passed, 3 skipped, 2 xfailed`.

```text
python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_workstream_focus_hook_parity.py
```

Observed result: `All checks passed!`.

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result: PASS.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-truncation-fix-refile
```

Observed result: PASS.

## Risk And Rollback

Risk is low and localized to startup-disclosure relay acceptance. The freshness
window intentionally uses the same 30-minute interval as the existing
`startup_response_pending` expiry, with a small future-clock skew tolerance. If
the behavior is too strict, rollback is the targeted removal of
`_startup_relay_cache_fresh(...)` from the relay-pointer consistency predicate
and removal of the two stale-cache regression tests.

## Owner Action Required

None.
