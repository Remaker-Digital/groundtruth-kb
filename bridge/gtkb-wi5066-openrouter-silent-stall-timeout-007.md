NEW

# GT-KB Bridge Implementation Report - gtkb-wi5066-openrouter-silent-stall-timeout - 007

bridge_kind: implementation_report
Document: gtkb-wi5066-openrouter-silent-stall-timeout
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5066-openrouter-silent-stall-timeout-006.md
Approved proposal: bridge/gtkb-wi5066-openrouter-silent-stall-timeout-005.md
Date: 2026-07-09 UTC

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: 1884030d-2dc8-498a-82fe-49dc4432d90f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066

Recommended commit type: fix

## Implementation Claim

WI-5066 scope A (bound + backstop + lease cleanup) is implemented. A silent,
unbounded OpenRouter/F worker stall is now a bounded, classified failure with no
stale lease residue. The implementation carries the -005 approved scope forward
but delivers it against the live committed baseline, which materially narrows the
source surface from the proposal's authoring-time assumption (see Scope
Reconciliation below): IP-1 was implemented in full; IP-2's dispatcher backstop
was found already committed and already regression-tested; IP-3 was scoped to the
one drain path that still lacked residue cleanup.

## Scope Reconciliation (verified against the live committed baseline)

The -005 proposal was authored in a prior session and assumed the dispatcher's
worker-lifetime backstop had been lost to worktree churn. Before implementing, I
verified each IP against the current HEAD (`fac6e892`) rather than the proposal's
authoring-time claims. Findings:

- **IP-1 (`scripts/cloud_harness_base.py`) - GENUINELY MISSING - implemented.**
  No wall-clock/DNS bound existed around the provider `urlopen`. Implemented in
  full.

- **IP-2 (`scripts/dispatcher_runtime.py`) - ALREADY COMMITTED - no source or
  test change.** The OpenRouter/F bounded worker-lifetime (`900s`) pass-through
  and the exit-`124` -> `worker_timeout` classification with configured-lifetime
  telemetry are already present in HEAD and were introduced by committed commit
  `afdda712` (not lost). `git status` reports `scripts/dispatcher_runtime.py`
  clean. The behavior is already regression-tested by
  `test_openrouter_lifetime_timeout_classified_as_worker_timeout`
  (`platform_tests/scripts/test_dispatcher_runtime.py`, explicitly WI-5066
  tagged) plus `test_spawn_harness_passes_target_lifetime_to_status_wrapper` and
  `test_worker_lifetime_profile_*`. Re-adding the same code or a duplicate test
  would be a redundant, no-value edit, so `dispatcher_runtime.py` and
  `test_dispatcher_runtime.py` are intentionally unchanged. The existing test is
  the spec-to-test evidence for the 124-classification clause.

- **IP-3 (`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`) - PARTLY
  PRESENT - scoped to `drain()`.** `soft_reset()` already cleaned both residue
  classes (`_prune_stale_dispatch_runs` for stale dispatch-runs and
  `_clear_lease_locks` for lease locks). The genuine gap was `drain()`, which
  terminated live workers and cleared drain markers but never pruned the
  no-live-worker lease / stale dispatch-run residue observed in the live stall.
  Implemented drain-side cleanup only.

`scripts/run_with_status.py` is deliberately untouched (its lifetime mechanism is
committed baseline and its current uncommitted worktree change belongs to the
separate `gtkb-wi5066-dispatch-wrapper-commandline-redaction` thread).

## Implementation Detail

### IP-1 - DNS/wall-clock bound (`scripts/cloud_harness_base.py`)

Root cause: `urllib.request.urlopen(request, timeout=...)` bounds socket
connect/read but not `getaddrinfo` (DNS), which runs before the socket exists. A
DNS-resolution stall therefore blocks the worker with no socket, no CPU, and no
output past the request timeout - the exact WI-5066 signature.

Fix: each provider POST attempt in `_post_json_with_bounded_retry` now runs on a
daemon worker thread joined for a hard wall-clock bound derived from the
per-attempt remaining deadline (`_call_with_wall_clock_bound`). Because the join
caps the whole call (DNS + connect + TLS + read), a `getaddrinfo` stall now
elapses the bound and raises `_ProviderCallTimeout` (a `TimeoutError` subclass),
which the existing transport-retry classifier
(`_is_retryable_provider_transport_error`) treats as retryable and the bounded
`CHAT_MAX_ATTEMPTS` loop absorbs. A persistent stall exhausts the deadline and
fails with a classified `CloudHarnessError` and nonzero exit rather than an
unbounded silent stall. The socket timeout is set a grace
(`PROVIDER_CALL_WALL_CLOCK_GRACE_SECONDS = 5.0`) shorter than the join so a
genuine socket stall still raises an accurately classified `URLError` first. A
fresh `Request` is built per attempt so an orphaned worker thread from a prior
attempt never shares mutable request state.

### IP-3 - drain residue cleanup (`bridge_dispatch_reset.py`)

Added `_prune_dead_lease_locks` (conservative: prunes a lease lock only when its
heartbeat is stale AND its recorded worker PID is not alive, so an in-flight or
hung-but-not-yet-reaped worker's lease is never dropped) and `_drain_residue_cleanup`
(sums dead-lease pruning plus the existing `_prune_stale_dispatch_runs` across
every dispatcher state dir). `drain()` now runs the cleanup at the dry-run report
and both non-dry-run completion paths, and reports the counts through two new
additive `DrainResult` telemetry fields (`dead_lease_locks_removed`,
`stale_dispatch_runs_pruned`). No recipient/quiesce state, bridge files,
PAUTH/project state, or quality surfaces are touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

## Owner Decisions / Input

Implementation authority is the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
reliability fast-lane (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`).
The -005 scope was owner-selected via AskUserQuestion in the predecessor session
(detected_via: ask_user_question): fix scope "A - Full" and "Draft the REVISE
now". No new owner decision is required by this report. No credential rotation,
provider-account change, deployment, force-push, sandbox weakening, or
visible-window fallback was requested or performed. The scope reconciliation
above (IP-2 already committed; IP-3 scoped to drain) is factual implementation
reporting, not a change to the approved scope.

## Prior Deliberations

- `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-005.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-006.md` - Loyal Opposition (Antigravity/C) GO verdict authorizing implementation.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing reliability fast-lane authorization.
- `DELIB-202665303` - owner decision: dispatch failure-timer = per-harness worker timers, generous first (governs the F=900s cap reused by IP-2).
- `DELIB-202665863` - LO verification of the watchdog/retry-reset pattern IP-1's bounded-timeout-then-retry design follows.

## Files Changed

- `scripts/cloud_harness_base.py` (IP-1 source: `_ProviderCallTimeout`, `_call_with_wall_clock_bound`, `PROVIDER_CALL_WALL_CLOCK_GRACE_SECONDS`, bounded attempt body)
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py` (IP-3 source: `_lease_record_worker_alive`, `_prune_dead_lease_locks`, `_drain_residue_cleanup`, `DrainResult` fields, `drain()` wiring)
- `platform_tests/scripts/test_cloud_harness_base.py` (IP-1 tests: 4 new)
- `groundtruth-kb/tests/test_bridge_dispatch_reset.py` (IP-3 tests: 3 new + `_write_lease` helper)

`dispatcher_runtime.py` and `test_dispatcher_runtime.py` are intentionally unchanged (IP-2 already committed + already tested; see Scope Reconciliation).

```text
 .../src/groundtruth_kb/bridge_dispatch_reset.py    | 65 +++++++++++++++
 groundtruth-kb/tests/test_bridge_dispatch_reset.py | 75 ++++++++++++++++-
 platform_tests/scripts/test_cloud_harness_base.py  | 57 +++++++++++++
 scripts/cloud_harness_base.py                      | 93 +++++++++++++++++++---
 4 files changed, 278 insertions(+), 12 deletions(-)
```

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (bounded/observable provider call) | `test_openai_chat_dns_stall_is_bounded_and_raises_classified_error` + `test_wall_clock_bound_times_out_on_stall_and_is_retryable` + `test_wall_clock_bound_returns_result_when_call_completes` + `test_wall_clock_bound_reraises_call_error` (test_cloud_harness_base.py) - a mocked never-returning `urlopen` is bounded, retried, and finally raises a classified `CloudHarnessError`; the synthetic timeout is a `TimeoutError` the retry classifier absorbs. PASS. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` (124 classification + drain/reset residue) | IP-2 classification: existing `test_openrouter_lifetime_timeout_classified_as_worker_timeout` (test_dispatcher_runtime.py, WI-5066-tagged) - PASS. IP-3 residue: `test_drain_prunes_dead_lease_and_preserves_hung_worker_lease`, `test_drain_prunes_stale_dispatch_run_residue`, `test_drain_dry_run_reports_dead_lease_residue_without_removing` (test_bridge_dispatch_reset.py) - PASS. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (no-window / headless safety) | No dispatcher launch kwargs changed; IP-3 helpers reuse existing `_dispatch_run_pid_alive` (which already uses `CREATE_NO_WINDOW`). Existing dispatcher no-window tests remain green (169 passed). |
| `GOV-ENV-LOCAL-AUTHORITY-001` (no credential disclosure) | IP-1 error text emits no API keys, headers, or provider payloads (message is a generic "wall-clock bound (DNS/connect/TLS stall)"); the fresh `Request` reuses the existing header dict without logging it. Credential scan on this report content passed (abort mode). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest across the three target test files run green (see Commands Run); `ruff check` and `ruff format --check` clean on all four changed files. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start authorization packet created after LO GO (`implementation_authorization.py begin --bridge-id gtkb-wi5066-openrouter-silent-stall-timeout`); `latest_status: GO`, PAUTH active. |

## Commands Run

Focused suite (per-file, in-root writable basetemp - see Environment Deviation):

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q --tb=short --basetemp .harness-tmp/pt-cloud`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp/pt-disp`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_dispatch_reset.py -q --tb=short --basetemp .harness-tmp/pt-reset`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check <4 changed files>`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <4 changed files>`

## Observed Results

- `test_cloud_harness_base.py`: 34 passed (30 existing + 4 new IP-1).
- `test_dispatcher_runtime.py`: 169 passed (includes the existing WI-5066 IP-2 classification test).
- `test_bridge_dispatch_reset.py`: 13 passed (10 existing + 3 new IP-3).
- `ruff check`: All checks passed.
- `ruff format --check`: 4 files already formatted.

## Environment Deviation (basetemp)

The -005 plan cited `--basetemp .gtkb-state/pytest-tmp/wi5066` as the
headless-stable temp base. In this session that directory is ACL-denied (even
`Get-ChildItem` on it fails with `Access is denied` - the same dotdir ACL class
that WI-5065 addresses), and the default pytest temp resolves under a
`C:\Users\...` path that the root-boundary directive blocks. Tests were therefore
run against an in-root, writable, gitignored `.harness-tmp/` basetemp instead.
The tests are environment-independent; only the temp-base path differs from the
plan. Running the three files together in one invocation only fails on the
cross-root basetemp/fixture collision, not on any test logic; per-file invocation
is green.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: repairs a reliability defect (an unbounded silent provider-call
  stall) with bounded, classified failure handling plus drain-side lease/dispatch-run
  residue cleanup. No new user-facing capability surface; net additive test coverage.

## Risk And Rollback

- Risk: an orphaned daemon worker thread lingers after a persistent DNS stall.
  Mitigation: it is a daemon (never blocks interpreter exit), builds a fresh
  `Request` per attempt (no shared mutable state), and IP-2's committed 900s
  worker-lifetime cap is the process-level backstop above it.
- Risk: over-aggressive lease pruning could drop a live worker's lease.
  Mitigation: `_prune_dead_lease_locks` prunes only when heartbeat is stale AND
  PID is not alive; live-heartbeat and live-PID leases are preserved
  (`test_drain_prunes_dead_lease_and_preserves_hung_worker_lease`).
- Risk: the 5s grace slightly overruns a per-attempt socket deadline.
  Mitigation: grace is subtracted from the socket timeout, keeping the whole
  attempt within the per-attempt remaining deadline.
- Rollback: single-commit revert of the four changed files restores prior
  timeout/cleanup behavior; no credential, provider-account, or KB rollback is in
  scope.

## Loyal Opposition Asks

1. Verify IP-1's DNS-bound design and its retryable classification against the linked specs and the four cloud-harness tests.
2. Confirm the IP-2 "already committed + already tested" finding by inspecting `dispatcher_runtime.py` at HEAD (`afdda712` introduced `OPENROUTER_WORKER_LIFETIME_SECONDS`) and the existing `test_openrouter_lifetime_timeout_classified_as_worker_timeout`; confirm no dispatcher edit is warranted.
3. Confirm IP-3's drain-side residue cleanup is conservative (no live-lease/live-worker drop) and that `soft_reset` already covered its surface.
4. Return VERIFIED if the report and implementation satisfy the approved -005 scope as reconciled to the live baseline, otherwise NO-GO with findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
