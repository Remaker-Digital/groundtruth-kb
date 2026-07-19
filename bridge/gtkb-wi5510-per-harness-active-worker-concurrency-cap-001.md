NEW
::init gtkb lo
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: d067ca16-171b-4b2e-89f5-642340e605a6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code-interactive-prime-builder-via-init-gtkb-pb

# Implementation Proposal - Add per-harness active-worker concurrency cap to bridge dispatch

bridge_kind: prime_proposal
Document: gtkb-wi5510-per-harness-active-worker-concurrency-cap
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5510

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Owner directive: dispatch concurrency throttling must be based on active-worker count per harness, not per-role or per-dispatch-action, sized as high as the system will bear before workers start failing. Today only a global cap (8) and a per-ROLE cap shared across harnesses (loyal-opposition=3) exist; nothing partitions the role budget per harness, which let 2 concurrent Ollama workers run while OpenRouter got 1, observed live this session. Empirical capacity probing this session (concurrent trivial round-trips, isolating raw provider throughput) found OpenRouter clean through 40 concurrent requests with zero hard failures, and Ollama clean through 25 concurrent requests with genuine HTTP 429 rate-limiting appearing at 30. Add a genuine per-harness live-worker cap (default 6, env-overridable, mirroring the existing per-role pattern exactly) wired into the same gate chain, and raise the role and global caps so the new per-harness cap is the practical constraint. The default is set with a safety margin below the observed provider ceilings because the probe measured raw provider throughput, not the full claim-acquire/review/verdict-publish workflow's additional local SQLite and git contention; tightening or loosening the default is expected once real review-workload concurrency data accumulates. Fast-lane reliability/observability improvement; source plus test only.

Work item description: Owner-directed architecture requirement: "The dispatch throttle should be based on the number of active workers, not the number of dispatch actions. The cap for each harness should be as high as the system will bear before workers start failing." This followed a direct observation this session: 2 concurrent live Ollama (D) workers were running simultaneously despite D's rules.toml max_items being 1, because max_items governs how many bridge items get bundled into one dispatch call's prompt, not concurrent worker count. The only live concurrency enforcement today is a global hard cap (GTKB_MAX_LIVE_DISPATCHED_PROCESSES, default 8, WI-4472) and a per-ROLE cap shared across every harness in that role (GTKB_DISPATCH_CONCURRENCY_<ROLE>, default loyal-opposition=3 / prime-builder=2, CA9165), both correctly PID-liveness-based (active workers, not dispatch actions), but neither is scoped per harness. With only D and F dispatchable for loyal-opposition, nothing prevents the shared role budget of 3 from landing entirely on one harness, as observed.

Empirical capacity data gathered this session via a controlled concurrent-round-trip probe (trivial single-turn prompts, bypassing the bridge-verdict/claim code path, isolating raw provider throughput from local contention): OpenRouter (F, deepseek-v4-flash) stayed clean (zero hard failures) through 40 concurrent requests. Ollama (D, deepseek-v4-flash-cloud) stayed clean through 25 concurrent requests; at 30 concurrent, 9/30 failed with genuine HTTP 429 Too Many Requests errors from the provider. This measures raw provider throughput only, not the full claim-acquire/review/verdict-publish workflow's local SQLite and git contention, so proposed defaults carry a safety margin below the observed ceilings pending real-workload validation.

Fix: add a genuine per-harness live-worker concurrency cap to dispatcher_runtime.py, following the exact PID-sidecar liveness-counting pattern already used by _count_live_dispatched_processes_for_role (dispatch_id already encodes the harness id as the token immediately after the role label, e.g. loyal-opposition-D), gated into the same _spawn_harness check chain alongside the existing global and per-role gates (most restrictive wins). Per-harness cap is configurable via a new GTKB_DISPATCH_CONCURRENCY_HARNESS_<ID> environment-variable override, following the identical override pattern already used for the role cap, with a code default of 6 per harness pending further tuning. Correspondingly raise the loyal-opposition role-cap default and the global hard cap so the new per-harness cap becomes the practical, active-worker-based throttle rather than being smothered by the existing role-shared ceiling of 3.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5510` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263487` - Cost-Optimized Autodispatch Priority Handoff
- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - Dispatcher daemon Claude+Cursor headless collaboration: harden-first, go-live-later
- `DELIB-20262479` - Bridge thread: gtkb-cross-harness-dispatch-concurrency-cap (10 versions, VERIFIED)
- `DELIB-202665737` - WI-4994 Prime Builder Fan-Out Dispatcher — Post-Implementation Verification Verdict

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5510`.

## Proposed Scope

- Add _count_live_dispatched_processes_for_harness(runs_dir, harness_id, role_label) to dispatcher_runtime.py, mirroring the existing _count_live_dispatched_processes_for_role exactly (same PID-sidecar liveness/prune semantics) but matching the compound token '-{role_label}-{harness_id}-' that _new_dispatch_id already encodes, so the count is scoped to one specific harness rather than the whole role.
- Add _max_live_dispatched_per_harness(harness_id) reading a new GTKB_DISPATCH_CONCURRENCY_HARNESS_<ID> environment-variable override, following the identical override-then-default pattern already used by _max_live_dispatched_per_role, with a code default of 6.
- Wire a third gate into the _spawn_harness check chain, evaluated after the existing global and per-role gates (most restrictive of the three wins), returning reason=per_harness_concurrency_cap_reached when the new harness-scoped count is at or above the per-harness cap.
- Raise DEFAULT_ROLE_LIMITS['loyal-opposition'] in bridge_dispatch_concurrency.py from 3 to 12, and raise DEFAULT_MAX_LIVE_DISPATCHED_PROCESSES in dispatcher_runtime.py from 8 to 20, so the new per-harness cap becomes the practical, active-worker-count-based throttle instead of being smothered by the existing role-shared and global ceilings, per the owner's explicit requirement that the throttle be worker-count-based per harness.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py; report pass/fail counts in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-RELIABILITY-FAST-LANE-001` | New unit tests added to test_perrole_concurrency_cap_dispatch.py exercise the per-harness counting function, the env override, and gate precedence ordering. |

## Acceptance Criteria

- A unit test in test_perrole_concurrency_cap_dispatch.py creates fake live .pid sidecars for two different harnesses under the same role and asserts the new per-harness count function returns only the count for the targeted harness, mirroring test_per_role_count_is_role_scoped.
- A unit test asserts the per-harness gate suppresses a spawn once the harness-scoped live count reaches its cap, while a different harness in the same role is still permitted to spawn (mirroring test_per_role_cap_suppresses_at_limit and test_per_role_below_cap_allows_same_role_spawn).
- A unit test asserts the GTKB_DISPATCH_CONCURRENCY_HARNESS_<ID> env override wins over the code default, mirroring test_per_role_cap_per_role_env_override.
- A unit test confirms the global and per-role gates still take precedence over the new per-harness gate when they are the more restrictive constraint, mirroring test_global_cap_keeps_precedence_over_per_role.
- ruff check and ruff format --check pass on both changed files.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`

## Recommended Commit Type

`feat`
