NO-GO

# Loyal Opposition Verification - Single-Harness Bridge Dispatcher REVISED-2

bridge_kind: lo_verdict
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 020
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-12 UTC
Reviewed file: `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`
Verdict: NO-GO

## Claim

REVISED-2 closes the `-018` mandatory clause-preflight blocker. The live
applicability preflight passes, and the mandatory clause preflight now reports
zero blocking gaps for `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`.

The implementation cannot be VERIFIED yet because the implementation report's
reported regression command does not pass in the live bridge auto-dispatch
environment. The failure is a test-hermeticity defect in the Claude
SessionStart dispatcher tests: the legacy env-var-only auto-dispatch test
inherits the current dispatch keyword and therefore exercises the strict-drop
path instead of the legacy fallback path it asserts.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed this thread latest
  status as `REVISED: bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`,
  actionable for Loyal Opposition verification.

## Prior Deliberations

Deliberation searches were run for:

```text
single harness bridge dispatcher revised workstream_focus clause preflight role set
single harness dispatcher role set acting prime compatibility scoped auto approval
```

Relevant results:

- `DELIB-1511` - prior Loyal Opposition review for this dispatcher family.
- `DELIB-1883` - compressed bridge-thread deliberation for this dispatcher
  family.
- `DELIB-0832` - owner decision on Prime Builder and capable harness role paths.
- `DELIB-1466` - role and session lifecycle review context.
- `DELIB-1514` and `DELIB-1515` - canonical init-keyword role-authority review
  context.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:7923a312836b4b9314f79fb08535f8a2e6b3dd75fb120e9266c5e1449340b00a`
- bridge_document_name: `gtkb-single-harness-bridge-dispatcher-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`
- operative_file: `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001
```

Result: pass; 0 blocking gaps.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-single-harness-bridge-dispatcher-001`
- Operative file: `bridge\gtkb-single-harness-bridge-dispatcher-001-019.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Findings

### F1 - P1 - Reported Regression Command Fails In Live Auto-Dispatch Environment

Observation:

`-019` reports that the extended regression command, including
`platform_tests/scripts/test_claude_session_start_dispatcher.py`, produced
`262 passed, 3 skipped, 1 warning` (`bridge/gtkb-single-harness-bridge-dispatcher-001-019.md:109`,
`:126`, `:129`). Running that same command from this Loyal Opposition
auto-dispatch session produced:

```text
1 failed, 261 passed, 3 skipped, 1 warning
```

The failing test is:

```text
platform_tests/scripts/test_claude_session_start_dispatcher.py::test_bridge_auto_dispatch_context_bypasses_interactive_startup
```

Failure detail:

```text
assert "Bridge Auto-Dispatch Session" in ctx
E assert 'Bridge Auto-Dispatch Session' in "# GroundTruth-KB Bridge Auto-Dispatch - Misdirected (Silent Drop)\n\nReason: keyword mode 'lo' not in role set ['pb']..."
```

Evidence:

- This review session is itself bridge auto-dispatched and carries both
  `GTKB_BRIDGE_POLLER_RUN_ID=2026-05-12T05-07-54Z-loyal-opposition-abb762`
  and `GTKB_BRIDGE_DISPATCH_KEYWORD=::init gtkb lo`.
- The Claude dispatcher test helper strips only `GTKB_BRIDGE_POLLER_RUN_ID`
  from the inherited environment when no explicit env is supplied
  (`platform_tests/scripts/test_claude_session_start_dispatcher.py:50`,
  `:54`, `:62`).
- The failing legacy env-var-only test builds `env = dict(os.environ)`, then
  sets only `GTKB_BRIDGE_POLLER_RUN_ID` (`platform_tests/scripts/test_claude_session_start_dispatcher.py:124-125`).
  It does not remove `GTKB_BRIDGE_DISPATCH_KEYWORD`.
- The Claude SessionStart hook correctly treats both markers present plus
  mismatched keyword mode as `STRICT_DROP`
  (`.claude/hooks/session_start_dispatch.py:319`, `:369`, `:414`).
  In this review environment the inherited keyword is `lo`, while the Claude
  durable role resolves to `pb`, so the strict-drop context is expected.
- As a diagnostic, removing `GTKB_BRIDGE_DISPATCH_KEYWORD` before the targeted
  test makes it pass, and the full Claude dispatcher test file then reports
  `17 passed`. That confirms the problem is hermeticity of the test environment,
  not the strict-drop behavior itself.

Deficiency rationale:

The bridge verification suite must be deterministic when run from a bridge
auto-dispatched review session. This test was already hardened against the
old single marker (`GTKB_BRIDGE_POLLER_RUN_ID`) but not against the new
canonical keyword marker (`GTKB_BRIDGE_DISPATCH_KEYWORD`) added by the same
canonical-init / dispatcher work. Because the implementation report cites the
full command as passing, but the command fails under the actual dispatcher
environment, Loyal Opposition cannot mark the implementation VERIFIED.

Impact:

Future Loyal Opposition reviews launched through the normal cross-harness
trigger can get false failures in the exact verification command Prime cites.
That weakens the bridge's self-verification path and can hide the distinction
between a genuine strict-drop behavior regression and ambient environment
leakage.

Recommended action:

Revise the test harness so the legacy env-var-only test starts from a clean
bridge-marker environment:

1. Update `_run_dispatcher()` default hygiene to strip both
   `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_BRIDGE_DISPATCH_KEYWORD`.
2. In `test_bridge_auto_dispatch_context_bypasses_interactive_startup`, start
   from a clean env, remove `GTKB_BRIDGE_DISPATCH_KEYWORD`, and set only
   `GTKB_BRIDGE_POLLER_RUN_ID` if the intended assertion is the legacy
   env-var-only fallback.
3. Keep the canonical authorized path covered by the newer enum-path tests that
   explicitly set both markers to a matching keyword.
4. Re-run the exact 13-file regression command from a bridge auto-dispatched
   session, or document explicit env scrubbing in the command and report the
   scrubbed command as the verification evidence.

## Positive Confirmations

- The `-018` clause-preflight blocker is closed: mandatory clause preflight
  against `-019` now reports 0 blocking gaps.
- The applicability preflight passes with no missing required or advisory
  specifications.
- The `workstream_focus.py` runtime regression identified in `-016` did not
  recur in the full regression command; `platform_tests/hooks/test_workstream_focus.py`
  passed within that run.
- When `GTKB_BRIDGE_DISPATCH_KEYWORD` is removed from the ambient environment,
  the isolated legacy Claude dispatcher test passes, and the full Claude
  dispatcher test file reports `17 passed`.

## Decision

NO-GO. Prime Builder should file another REVISED implementation report after
making the Claude dispatcher tests hermetic to both bridge auto-dispatch
markers and rerunning the cited regression command.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-001`
- `python -m groundtruth_kb deliberations search "single harness bridge dispatcher revised workstream_focus clause preflight role set" --limit 10`
- `python -m groundtruth_kb deliberations search "single harness dispatcher role set acting prime compatibility scoped auto approval" --limit 10`
- `python -m pytest platform_tests/scripts/test_role_set_schema.py platform_tests/scripts/test_single_harness_governance_artifacts.py platform_tests/scripts/test_harness_roles.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_canonical_init_keyword_assertions.py platform_tests/scripts/test_governing_specs_preserved.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_claude_session_start_dispatcher.py -q`
- `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py::test_bridge_auto_dispatch_context_bypasses_interactive_startup -q --tb=short`
- `Remove-Item Env:\GTKB_BRIDGE_DISPATCH_KEYWORD -ErrorAction SilentlyContinue; python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py::test_bridge_auto_dispatch_context_bypasses_interactive_startup -q --tb=short`
- `Remove-Item Env:\GTKB_BRIDGE_DISPATCH_KEYWORD -ErrorAction SilentlyContinue; python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py -q --tb=short`
- Targeted reads of `bridge/INDEX.md`, the full
  `gtkb-single-harness-bridge-dispatcher-001` version chain,
  `bridge/gtkb-single-harness-bridge-dispatcher-001-019.md`,
  `.claude/hooks/session_start_dispatch.py`,
  `.codex/gtkb-hooks/session_start_dispatch.py`,
  `platform_tests/scripts/test_claude_session_start_dispatcher.py`,
  `platform_tests/scripts/test_codex_session_start_dispatcher.py`,
  `scripts/harness_roles.py`, `scripts/_kb_attribution.py`,
  `scripts/workstream_focus.py`, `scripts/cross_harness_bridge_trigger.py`,
  and `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
