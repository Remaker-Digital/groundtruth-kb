REVISED

# Bridge Revision - gtkb-wi5066-openrouter-silent-stall-timeout - 005 (re-scoped proposal to the post-WI-5078 codebase)

bridge_kind: prime_proposal
Document: gtkb-wi5066-openrouter-silent-stall-timeout
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC
responds_to: `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-004.md`

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: a7996a03-6874-411a-9c40-cee06222cedd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066

target_paths: ["scripts/cloud_harness_base.py", "scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_dispatcher_runtime.py", "groundtruth-kb/tests/test_bridge_dispatch_reset.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED entry re-scopes the WI-5066 silent-stall fix to the current
codebase and returns the thread to a proposal awaiting Loyal Opposition GO. Two
facts force a re-scope rather than a re-report of the -003 implementation:

1. The -003 implementation (dispatcher worker-lifetime `900s` plus exit-code
   `124` -> `worker_timeout` classification in `scripts/dispatcher_runtime.py`)
   is no longer present in the worktree — `git status` reports
   `scripts/dispatcher_runtime.py` clean, so the uncommitted -003 changes were
   lost to worktree churn after the -004 NO-GO.
2. The provider transport was relocated by `3b3eb475`
   (WI-5078 cloud-harness re-base, 2026-07-08): `scripts/openrouter_harness.py`
   is now a thin adopter over `scripts/cloud_harness_base.py`, so the original
   proposal's IP-1 (harness-level DNS/TLS/startup bounding in
   `openrouter_harness.py`) must land in `cloud_harness_base.py`.

The fix design is unchanged in intent and validated by two independent analyses
(the original Codex proposal and a fresh 2026-07-09 root-cause pass): a silent,
unbounded stall becomes a bounded, classified failure with no stale lease.

## Root Cause (confirmed by code analysis)

The harness `session_timeout` is cooperative deadline-propagation: `run_tool_loop`
computes `_remaining_timeout(session_deadline)` and passes it as
`urllib.request.urlopen(request, timeout=...)`. That timeout bounds the socket
connect/read but does NOT bound `getaddrinfo` (DNS resolution), which runs inside
`urlopen` before the socket exists. A DNS-resolution stall therefore blocks the
worker with no socket, no CPU, no output, and the session deadline is never
re-checked. This matches the WI-5066 observation exactly (no TCP socket, no CPU,
no output, alive past the request timeout).

## Proposed Scope (scope A: bound + backstop + lease cleanup)

IP-1 (`scripts/cloud_harness_base.py`): bound the provider chat call including
DNS resolution. Execute the chat call under a hard wall-clock bound derived from
the remaining session deadline (worker-thread join, so `getaddrinfo` is covered),
and on expiry raise a classified, credential-safe, retryable transport error so
the existing bounded chat retry loop (`RETRYABLE_PROVIDER_TRANSPORT_MARKERS`,
`CHAT_MAX_ATTEMPTS`) handles it; a persistent stall fails with a clear classified
`CloudHarnessError` and nonzero exit rather than an unbounded silent stall.

IP-2 (`scripts/dispatcher_runtime.py`): re-implement the lost wrapper-lifetime
backstop — pass a bounded worker lifetime to `run_with_status.py` for OpenRouter/F
launches (the wrapper's committed baseline `TIMEOUT_EXIT_CODE = 124` /
`DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS` mechanism is reused, not modified), and
classify wrapper exit code `124` with no post-launch Loyal Opposition verdict as
`worker_timeout` with configured-lifetime telemetry. This is the process-level
backstop that bounds any hang location (DNS, socket, subprocess) even if IP-1's
in-harness bound is bypassed.

IP-3 (`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`): ensure
`gt bridge dispatch drain` / `reset --soft` clean the no-exit-code /
no-live-worker document-lease and stale dispatch-run residue observed in the live
stall, without clearing canonical bridge files, PAUTH/project state, or quality
surfaces.

IP-4 (tests): focused tests for the DNS/getaddrinfo bound (mocked slow resolver;
no live provider call), the dispatcher lifetime pass-through and `124`
classification, and the drain/reset lease-cleanup behavior.

Out of scope: `scripts/run_with_status.py` (its lifetime-kill mechanism is
committed baseline and its current uncommitted changes belong to the separate
`gtkb-wi5066-dispatch-wrapper-commandline-redaction` thread — deliberately not
touched here to avoid re-entanglement); credential lifecycle; provider-account
settings; visible-window fallback; broad dispatcher policy rewrites.

## Findings Addressed (from -004 NO-GO)

### P1 - The changed path set overlaps other selected implementation reports
Resolved by de-entanglement. WI-5064's SSL fix is committed independently in
`scripts/cloud_harness_base.py` via `3b3eb475` (WI-5078), so WI-5064 no longer
claims `dispatcher_runtime.py`. The WI-5065 `gtkb-wi5065-codex-live-sandbox-readiness`
thread is retired (WITHDRAWN at -005), abandoning its `dispatcher_runtime.py`
changes. This REVISED proposal also excludes `run_with_status.py`, leaving the
`gtkb-wi5066-dispatch-wrapper-commandline-redaction` thread's file untouched.
WI-5066 can therefore implement and commit its `dispatcher_runtime.py` change as
an atomic, single-concern finalization.

### P1 - Test reproduction was blocked by headless temp setup
Resolved by pinning the pytest temp base. The implementation report will run the
focused suite with an explicit in-root writable base temp directory
(`--basetemp .gtkb-state/pytest-tmp/wi5066`) so pytest can create its temporary
directory under the headless sandbox, and will cite the exact headless-stable
command and pass results.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this source/test repair is bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires active project authorization under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the standing authorization does not replace LO GO or the implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - authorizes this single-concern reliability defect repair by active project membership.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected harnesses must process work headlessly or fail observably.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs status/health, drain/reset, stale-run classification, and failure evidence.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - dispatcher background work stays headless/no-window safe on Windows.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential disclosure or lifecycle change while bounding provider runtime behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the report will map focused tests and runtime evidence to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the PAUTH/project/work-item metadata above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are GT-KB platform files inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-5066 is the active backlog record for this recurrence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live stall and its fix are preserved as durable bridge/work-item evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5066 advances through the standard defect-fix lifecycle triggers.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - defect, proposal, verification, and report stay linked through governed artifacts.

## Prior Deliberations

- `DELIB-202665863` - Loyal Opposition Verification: Service-SoT watchdog retry reset (WI-5062, VERIFIED) - the watchdog/retry-reset pattern this proposal's bounded-timeout-then-retry design follows.
- `DELIB-202665303` - Owner decision: WI-4987 dispatch failure-timer fix = per-harness worker timers, generous first, dial in with experience - governs the bounded worker-lifetime choice in IP-2.
- `DELIB-202665849` - Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060) - the retry-classification lineage IP-1 extends to DNS.
- `DELIB-202665847` - Loyal Opposition Verdict: OpenRouter connection reset retry - adjacent transport-retry precedent.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing reliability fast-lane authorization this work runs under.

## Owner Decisions / Input

Implementation authority is the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
(reliability fast-lane). The re-scope approach was chosen by the owner via
`AskUserQuestion` in this interactive session (2026-07-09), detected_via:
ask_user_question:

- Fix scope: owner selected **"A - Full"** (bound network incl DNS + process wall-clock backstop + lease cleanup on timeout/drain).
- WI-5066 handling: owner selected **"Draft the REVISE now"**, directing a REVISED of the existing `-openrouter-silent-stall-timeout` thread re-scoped to the post-WI-5078 codebase.
- Carried forward: the 2026-07-07 owner goal that OpenRouter must be LO-default and both Codex and OpenRouter must work headlessly (recorded on -001).

No credential rotation, provider-account change, deployment, force-push, sandbox weakening, or visible-window fallback is requested or authorized.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`,
WI-5066's acceptance summary, and `GOV-RELIABILITY-FAST-LANE-001` govern this
bounded defect repair. No new or revised requirement is required before
implementation begins after LO GO.

## Scope Changes

- Added `scripts/cloud_harness_base.py` as the IP-1 target (replaces the lost pre-WI-5078 `openrouter_harness.py` location for DNS/transport bounding).
- Retained `scripts/dispatcher_runtime.py` for IP-2 (re-implement the lost lifetime pass-through + `124` classification), now committable atomically after de-entanglement.
- Retained `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py` for IP-3 lease cleanup.
- Removed `scripts/openrouter_harness.py`, `scripts/run_with_status.py`, and `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` from the original -001 target set: transport moved to `cloud_harness_base.py`; `run_with_status.py` is left to the redaction thread; stale-run classification is achievable within the `dispatcher_runtime.py` exit-code path.

## Pre-Filing Preflight Subsection

Applicability and ADR/DCL clause preflights are run against this REVISED body via
`--content-file` before filing; expected `preflight_passed: true`,
`missing_required_specs: []`, and clause preflight `Blocking gaps: 0`.

## Spec-Derived Verification Plan

Focused tests land in `platform_tests/scripts/test_cloud_harness_base.py`,
`platform_tests/scripts/test_dispatcher_runtime.py`, and
`groundtruth-kb/tests/test_bridge_dispatch_reset.py`.

| Spec / governing surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Test that a mocked slow `getaddrinfo` in the chat path raises a classified retryable transport error within the bounded deadline rather than blocking indefinitely; a persistent stall exits nonzero with a classified `CloudHarnessError`. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Test that dispatcher exit-code processing classifies wrapper exit `124` with no LO verdict as `worker_timeout` with configured-lifetime telemetry; test drain/reset clears no-exit-code/no-live-worker lease residue. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Inspect/confirm dispatcher launch kwargs preserve Windows no-window behavior. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Assert failure messages and tests emit no API keys, headers, or raw provider payloads. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused pytest with `--basetemp .gtkb-state/pytest-tmp/wi5066`, plus `ruff check` and `ruff format --check` on the changed files, and cite exact pass results in the report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5066-openrouter-silent-stall-timeout` after LO GO and cite the packet. |

Expected focused commands:

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_dispatcher_runtime.py groundtruth-kb/tests/test_bridge_dispatch_reset.py -q --tb=short --basetemp .gtkb-state/pytest-tmp/wi5066

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py scripts/dispatcher_runtime.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py scripts/dispatcher_runtime.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py

## Verification Plan

The post-implementation report will carry forward the Specification Links above,
provide the spec-to-test mapping in the table, cite the exact executed commands
and results (including the headless-stable `--basetemp` pytest invocation), and
confirm no credential leakage and preserved no-window behavior.

## Risk And Rollback

- Risk: an overly aggressive DNS/session bound could abort a slow but healthy provider review. Mitigation: derive the bound from the existing session deadline (already `--session-timeout`-configured), classify as retryable so the bounded retry loop absorbs transients, and only fail hard after retries exhaust.
- Risk: re-touching `dispatcher_runtime.py` could regress no-window behavior or dispatch classification. Mitigation: reuse the committed `run_with_status.py` lifetime mechanism unchanged, lock no-window kwargs with tests, and keep the change to lifetime pass-through + `124` classification.
- Risk: lease-cleanup changes could over-prune canonical state. Mitigation: scope cleanup to no-exit-code/no-live-worker residue only; assert canonical bridge files, PAUTH/project state, and quality surfaces are untouched.
- Rollback: single-commit revert of the changed source/test lines restores prior timeout/classification/cleanup behavior; no credential, provider-account, or KB rollback is in scope.

## Recommended Commit Type

`fix:` - repairs a reliability defect (silent unbounded worker stall) with bounded, classified failure handling and lease cleanup; no new user-facing capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
