NEW

# Defect-Fix Proposal - WI-5308 Codex Private-Desktop Proof Auto-Renewal

bridge_kind: prime_proposal
Document: gtkb-wi5308-codex-proof-auto-renewal
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; owner-resumed fleet stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5308-CODEX-PROOF-RENEWAL-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5308

target_paths: ["scripts/ensure_dispatcher_daemon.py", "scripts/codex_no_window_smoke_probe.py", "platform_tests/scripts/test_ensure_dispatcher_daemon.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py"]

## Claim

Codex A is again a real, PB-only headless dispatch target, but only because an interactive operator manually refreshed a four-hour WI-5135 proof. This proposal closes the already-tracked WI-5134 lifecycle gap through its GOV-12/GOV-13 successor WI-5308 and TEST-11451. The dispatcher supervisor will renew the proof before expiry through the already-VERIFIED dispatch-wrapper and Windows private-desktop probe, without changing routing, eligibility, worker limits, leases, roles, or live work.

## Defect / Reproduction

1. Before the bounded recovery, `scripts/verify_codex_dispatch.py --json` reported `live_headless_reason=codex_no_window_verification_expired`; dispatcher recipient `prime-builder:A` reported `codex_dispatch_not_ready` and had no live worker.
2. The committed proof generator already existed at `scripts/codex_no_window_smoke_probe.py`, but no supervisor, scheduled task, or governed lifecycle called it before the four-hour `expires_at` boundary.
3. Running the established probe through `--dispatch-wrapper` on 2026-07-15 produced two runs, three marker commands per run, `windows_private_desktop` containment, zero visible windows, and a current proof expiring at `2026-07-16T01:48:16Z`.
4. The live daemon then spawned substantive PB worker `2026-07-15T21-48-32Z-prime-builder-A-aff7b2` on demand for `gtkb-authority-foundations-project-authorization`. Runtime evidence records harness A, role `prime-builder`, a 4,200-second lifetime, and `windows_private_desktop` containment.
5. Nothing will repeat that refresh automatically. Without this repair, A returns to `codex_dispatch_not_ready` after the current proof expires.

The old pre-GOV-12 WI-5134 is retired in favor of WI-5308 / TEST-11451; its diagnosis remains historical evidence. WI-5250 remains a distinct ACL-probe truthfulness repair and is not absorbed here.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, and the VERIFIED WI-5135 containment contract already require unattended, truthful, private-desktop Codex dispatch readiness. WI-5308 implements the missing renewal lifecycle and does not introduce a new role, routing policy, eligibility policy, proof schema, or safety requirement.

## In-Root Placement Evidence

All four mutation targets are clean tracked files inside `E:\GT-KB\scripts\` or `E:\GT-KB\platform_tests\`. Runtime proof, refresh status, and lock outputs remain generated under the established in-root `.gtkb-state/bridge-poller/` state directory and are not versioned implementation targets.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - an eligible, healthy PB target must remain dispatchable without periodic manual recovery.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - A remains a functional governed harness with durable readiness and evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the existing scheduled supervisor is the owner of unattended daemon/readiness maintenance; no retired poller is restored.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - readiness remains based on observed Codex behavior rather than assumed hook or subprocess inheritance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation still requires independent GO, claim, implementation-start authorization, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal names the complete governing set and exact target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - TEST-11451 maps due timing, single-flight behavior, containment, failure handling, and non-mutation to executable tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and machine-readable targets are present.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - each source/test mutation remains operation-time gated by the active bounded PAUTH.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass GO, exact targets, claim, start, or independent verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the predecessor, successor, linked test, proposal, implementation, runtime evidence, and verdict remain durable and connected.
- `GOV-STANDING-BACKLOG-001` - the recurring outage remains visible until independently VERIFIED and committed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all code, tests, and generated evidence remain inside the GT-KB platform root.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded PAUTH carriers and full governed repair for defects discovered while proving A/B/C/D/F/H.
- `DELIB-202666064` authorizes the WI-5135 Codex headless Prime path and its private-desktop containment work.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` requires efficacy-gated no-window behavior.
- `DELIB-20266201` records dispatcher daemon process-lifecycle supervision requirements.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-010.md` independently VERIFIED the exact private-desktop and schema-v2 probe reused here.
- WI-5134 records the original auto-refresh gap; WI-5308 is its linked-test successor.

## Owner Decisions / Input

- Mike's 2026-07-15 directive is exact: "Codex must be restored to a fully dispatchable state in which headless PB workers are spawned on demand."
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` permits this bounded proposal and PAUTH carrier while preserving all later bridge and implementation gates.
- No eligibility, role, routing, allowance, credential, deployment, release, or direct runtime-state mutation is requested.

## Proposed Scope

1. Add a pure proof-state evaluator to `codex_no_window_smoke_probe.py`. A schema-v2 passing proof with an `expires_at` later than a bounded renewal lead remains a no-op; missing, expired, malformed, or near-expiry evidence becomes due.
2. Add an OS-released single-flight lock around the renewal operation so concurrent supervisor invocations cannot launch duplicate Codex probes. The lock must not depend on a permanently stale marker or terminate any process.
3. Make proof and bounded refresh-status writes atomic. Keep the existing verification schema and four-hour TTL authoritative.
4. On a passing refresh, atomically publish the new proof. On observed visible-window evidence, publish the failure immediately so dispatch fails closed. On a non-window operational failure while an existing proof is still current, preserve that still-valid proof, record a bounded failure/backoff status, and retry before expiry; once no current proof remains, readiness continues to fail closed.
5. Have `ensure_dispatcher_daemon.py` ensure the daemon first, then invoke the due-only renewer from its existing hidden scheduled-supervisor path. Renewal failure must not kill or restart the healthy daemon, but the command/status output must make the readiness failure diagnosable.
6. Preserve the existing `--dispatch-wrapper` and `windows_private_desktop` route. Do not add a direct `codex exec` path, change the worker command, or weaken the schema-v2 marker/window checks.
7. Preserve A as PB-only and keep current eligibility, max-items, leases, live workers, worker lifetimes, routing, proof TTL, and all other harnesses unchanged.

## Explicit Exclusions

- No edit to dispatcher runtime, rules, registry, eligibility, leases, locks, worker ledgers, roles, model selection, or allowance configuration.
- No worker termination, daemon disablement, retired poller restoration, watchdog kill loop, or duplicate daemon creation.
- No ACL mutation and no change to WI-5250's probe-classification scope.
- No credential lifecycle, external provider/account mutation, Git history rewrite, push, deployment, release, destructive cleanup, or unrelated worktree mutation.
- No staging or commit before independent verification; finalization must include only WI-5308 reviewed hunks and bridge evidence.

## Specification-Derived Verification Plan

| Requirement | Deterministic verification |
| --- | --- |
| Current proof is a no-op | Freeze time with a proof outside the lead window; assert zero probe calls and unchanged proof bytes. |
| Near-expiry/missing proof renews | Inject a near-expiry and missing proof; assert one dispatch-wrapper/private-desktop probe call and atomic passing proof publication. |
| Single-flight across supervisor invocations | Hold the renewal lock and invoke a second refresh; assert the second returns a stable held/no-op result and launches no probe. |
| Visible-window evidence fails closed | Inject a probe payload with `visible_window_detected=true`; assert failure publication and no ready result. |
| Transient non-window failure preserves current evidence | Inject an operational marker/provider failure while the old proof is unexpired; assert proof bytes remain unchanged, bounded status/backoff is written, and no success is claimed. |
| Supervisor integration | Assert daemon ensure happens before renewal, already-running daemon stays a no-op, and renewal failure never stops/restarts it. |
| Containment contract | Existing WI-5135 tests continue to require schema v2, marker chain, dispatch-wrapper path, and `windows_private_desktop` on Windows. |
| Role/config/worker non-mutation | Tests prove no dispatcher config, eligibility, lease, runtime ledger, role, or worker termination API is called. |
| Static quality | Ruff check/format and `git diff --check` pass on the exact four paths. |
| Live readiness | After VERIFIED landing, canonical dispatcher report shows A selected as PB-only and a fresh substantive PB item can spawn under private-desktop containment. |

Minimum focused commands:

- `python -m pytest platform_tests/scripts/test_ensure_dispatcher_daemon.py platform_tests/scripts/test_codex_no_window_smoke_probe.py -q --tb=short`
- selected WI-5135 readiness/containment tests from `platform_tests/scripts/test_dispatcher_runtime.py` and `platform_tests/scripts/test_verify_codex_dispatch.py` in read-only verification context
- `python -m ruff check scripts/ensure_dispatcher_daemon.py scripts/codex_no_window_smoke_probe.py platform_tests/scripts/test_ensure_dispatcher_daemon.py platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `python -m ruff format --check scripts/ensure_dispatcher_daemon.py scripts/codex_no_window_smoke_probe.py platform_tests/scripts/test_ensure_dispatcher_daemon.py platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `git diff --check -- scripts/ensure_dispatcher_daemon.py scripts/codex_no_window_smoke_probe.py platform_tests/scripts/test_ensure_dispatcher_daemon.py platform_tests/scripts/test_codex_no_window_smoke_probe.py`

## Acceptance Criteria

- A current proof remains byte-for-byte unchanged until the bounded lead window.
- At most one renewal probe is in flight across concurrent supervisor invocations.
- Every real renewal uses the established dispatch wrapper and Windows private desktop; no visible window may be observed.
- Passing evidence extends the four-hour proof automatically without operator action.
- Visible-window evidence revokes readiness immediately; transient non-window failure cannot erase still-current passing evidence or claim success.
- A remains PB-only, dispatchable when funded and functional, and able to spawn substantive headless PB work on demand.
- No live worker, dispatcher configuration, eligibility, role, lease, or runtime ledger is mutated by the renewal path.
- All implementation is confined to the exact four clean PAUTH-covered paths and passes TEST-11451 plus the carried WI-5135 containment checks.
- Independent Loyal Opposition verification and a focused commit complete the lifecycle.

## Risks / Rollback

The main risk is an unattended refresh loop consuming Codex budget or replacing valid evidence after a transient provider failure. Due-only timing, single-flight exclusion, bounded retry/backoff, and preservation of still-current proof contain that risk. A second risk is that supervisor maintenance could interfere with daemon liveness; ordering and tests therefore require daemon ensure first and prohibit restart/termination on renewal failure. Rollback is a focused revert of the four source/test paths; the last valid proof remains subject to its existing TTL and all bridge/metadata history remains append-only.

## Pre-Filing Preflight Subsection

Before filing, run applicability and mandatory clause preflights against this exact content. Filing is allowed only with `preflight_passed=true`, no missing required or advisory specifications, no blocking errors, and zero mandatory clause gaps.

## Files Expected To Change

- `scripts/ensure_dispatcher_daemon.py`
- `scripts/codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_ensure_dispatcher_daemon.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`

## Recommended Commit Type

`fix`
