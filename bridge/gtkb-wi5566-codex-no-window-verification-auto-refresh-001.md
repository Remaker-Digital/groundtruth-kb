NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Codex no-window verification expires with no periodic auto-refresh, silently idling A

bridge_kind: prime_proposal
Document: gtkb-wi5566-codex-no-window-verification-auto-refresh
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5566

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/codex_no_window_smoke_probe.py", "platform_tests/scripts/test_codex_no_window_refresh.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prevent Codex A from silently becoming non-dispatch-ready when its four-hour no-window proof expires by adding a daemon-owned, asynchronous, liveness-aware, single-flight refresh of the existing private-desktop schema-v3 probe before expiry. Preserve fail-closed readiness, zero visible windows, full A/D/F allowances, all live workers, and the exact current dispatcher topology; make no dispatcher configuration or TAFE mutation.

Work item description: A (Codex Prime Builder) was completely idle for the entire session (zero dispatch-run artifacts) because scripts/verify_codex_dispatch.py's live_headless_ready gate depends on a time-bounded smoke-test verification (.gtkb-state/bridge-poller/codex-no-window-verification.json, ~4-hour TTL per this session's observed expires_at) written by scripts/codex_no_window_smoke_probe.py, and nothing periodically re-runs that probe before it lapses. Once it expires, the dispatcher silently treats A as codex_no_window_verification_expired/not-ready and stops dispatching to it, with no owner-visible alert. Manually re-running codex_no_window_smoke_probe.py --dispatch-wrapper immediately restored A to dispatchable. Fix: either schedule the smoke probe to re-run on an interval safely inside the TTL (mirroring the git-lock health-check pattern just added), or have the dispatch-health surface (gt bridge dispatch health) surface an explicit WARN/FAIL finding when this specific verification is within some margin of expiry, so the gap is visible before it silently drains PB throughput to zero.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5566` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_dispatcher_daemon.py`, `scripts/codex_no_window_smoke_probe.py`, `platform_tests/scripts/test_codex_no_window_refresh.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
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
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-RELIABILITY-FAST-LANE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665633` - GT-KB Bridge Verdict — gtkb-wi4929-codex-sessionstart-timeout-alignment — 012
- `DELIB-20260715-CONSOLE-WINDOW-STORM-DIAGNOSIS-EVIDENCE` - Console-window storm diagnosis: supporting evidence
- `DELIB-202666106` - Loyal Opposition Verdict — VERIFIED — gtkb-wi5135-codex-shell-no-window-dispatch
- `DELIB-202665784` - Loyal Opposition Verdict — GO — gtkb-wi5007-prime-unchanged-pending-residue
- `DELIB-202666203` - Authorize WI-5250 Codex A dispatch readiness repair

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5566`.

## Proposed Scope

- Add a daemon-owned, single-flight Codex no-window evidence refresh coordinator around the existing schema-v3 private-desktop smoke probe; do not create or modify a scheduled task, dispatcher rule, eligibility flag, role, cap, routing weight, or TAFE state.
- On live daemon ticks only, classify current evidence as not-due, due within a bounded pre-expiry margin, expired/missing, refresh-in-progress, refresh-backoff, refreshed, or refresh-failed. Launch at most one hidden asynchronous refresh only when no live Codex A dispatch is present; never wait synchronously in the dispatch tick or disturb D/F work.
- Use an atomic single-flight record with PID plus create-time provenance, bounded stale-owner recovery, and a bounded retry interval. Persist only operational refresh status and schema-v3 evidence; never treat launch as success, and keep readiness fail closed unless the exact completed probe passes the canonical validator.
- Make verification evidence replacement atomic so readers observe either the complete prior payload or complete new payload. Preserve the last passing payload until the refresh completes, but never extend its expiry or report success from an incomplete or failed probe.
- Expose stable bounded refresh diagnostics through the daemon tick/status path while preserving existing readiness reasons. Shadow mode and dry-run must remain observational and must never launch a refresh.
- Dependency hold: scripts/gtkb_dispatcher_daemon.py currently contains foreign shared-worktree changes. Do not claim or implement until all exact target ownership is clear and a post-GO operation-time packet admits only the approved hunks.

## Cross-Harness Disposition

- **A**: Codex remains PB-only and receives ordinary work only after canonical readiness passes; refresh is liveness-aware and single-flight.
- **D**: Ollama remains dispatchable LO with unchanged provider, role, allowance, cap, and routing behavior.
- **F**: OpenRouter remains dispatchable LO with unchanged provider, role, allowance, cap, and routing behavior.
- **B/C/E/H**: No source, configuration, role, eligibility, routing, or runtime behavior change.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5566; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "A (Codex Prime Builder) was completely idle for the entire session (zero dispatch-run artifacts) because scripts/verify_codex_dispatch.py's live_headless_ready gate depends on a time-bounded smoke-test verification (.gtkb-state/bridge-poller/codex-no-window-verification.json, ~4-hour TTL per this session's observed expires_at) written by scripts/codex_no_window_smoke_probe.py, and nothing periodically re-runs that probe before it lapses. Once it expires, the dispatcher silently treats A as codex_no_window_verification_expired/not-ready and stops dispatching to it, with no owner-visible alert. Manually re-running codex_no_window_smoke_probe.py --dispatch-wrapper immediately restored A to dispatchable. Fix: either schedule the smoke probe to re-run on an interval safely inside the TTL (mirroring the git-lock health-check pattern just added), or have the dispatch-health surface (gt bridge dispatch health) surface an explicit WARN/FAIL finding when this specific verification is within some margin of expiry, so the gap is visible before it silently drains PB throughput to zero.",
  "after_behavior": "Prevent Codex A from silently becoming non-dispatch-ready when its four-hour no-window proof expires by adding a daemon-owned, asynchronous, liveness-aware, single-flight refresh of the existing private-desktop schema-v3 probe before expiry. Preserve fail-closed readiness, zero visible windows, full A/D/F allowances, all live workers, and the exact current dispatcher topology; make no dispatcher configuration or TAFE mutation.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5566",
    "project": "PROJECT-GTKB-RELIABILITY-FIXES",
    "target_paths": [
      "scripts/gtkb_dispatcher_daemon.py",
      "scripts/codex_no_window_smoke_probe.py",
      "platform_tests/scripts/test_codex_no_window_refresh.py"
    ],
    "linked_specifications": [
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001",
      "GOV-HARNESS-ONBOARDING-CONTRACT-001",
      "GOV-RELIABILITY-FAST-LANE-001",
      "ADR-DISPATCHER-ARCHITECTURE-001"
    ]
  },
  "expected_result": {
    "summary": "Prevent Codex A from silently becoming non-dispatch-ready when its four-hour no-window proof expires by adding a daemon-owned, asynchronous, liveness-aware, single-flight refresh of the existing private-desktop schema-v3 probe before expiry. Preserve fail-closed readiness, zero visible windows, full A/D/F allowances, all live workers, and the exact current dispatcher topology; make no dispatcher configuration or TAFE mutation.",
    "scope": [
      "Add a daemon-owned, single-flight Codex no-window evidence refresh coordinator around the existing schema-v3 private-desktop smoke probe; do not create or modify a scheduled task, dispatcher rule, eligibility flag, role, cap, routing weight, or TAFE state.",
      "On live daemon ticks only, classify current evidence as not-due, due within a bounded pre-expiry margin, expired/missing, refresh-in-progress, refresh-backoff, refreshed, or refresh-failed. Launch at most one hidden asynchronous refresh only when no live Codex A dispatch is present; never wait synchronously in the dispatch tick or disturb D/F work.",
      "Use an atomic single-flight record with PID plus create-time provenance, bounded stale-owner recovery, and a bounded retry interval. Persist only operational refresh status and schema-v3 evidence; never treat launch as success, and keep readiness fail closed unless the exact completed probe passes the canonical validator.",
      "Make verification evidence replacement atomic so readers observe either the complete prior payload or complete new payload. Preserve the last passing payload until the refresh completes, but never extend its expiry or report success from an incomplete or failed probe.",
      "Expose stable bounded refresh diagnostics through the daemon tick/status path while preserving existing readiness reasons. Shadow mode and dry-run must remain observational and must never launch a refresh.",
      "Dependency hold: scripts/gtkb_dispatcher_daemon.py currently contains foreign shared-worktree changes. Do not claim or implement until all exact target ownership is clear and a post-GO operation-time packet admits only the approved hunks."
    ],
    "acceptance_criteria": [
      "TEST-11656 passes: before expiry, one bounded private-desktop refresh renews valid evidence and one fresh governed dispatcher-produced A Prime Builder item exits zero and advances its assigned bridge document.",
      "Concurrent live A work suppresses refresh without changing A eligibility; live D/F workers continue unaffected. Repeated daemon ticks cannot create duplicate refreshes.",
      "Probe failure, timeout, malformed evidence, visible-window detection, model-cache diagnostic failure, or nonzero wrapper result remains fail closed with one stable diagnostic and bounded retry; no false readiness or expiry extension occurs.",
      "Shadow mode and dry-run perform no refresh spawn or evidence mutation. Dispatcher configuration, roles, routing, caps, allowances, TAFE, leases, and unrelated worktree bytes remain unchanged.",
      "Evidence writes are atomic, target files are hunk-isolated from foreign dirty work, focused tests pass, independent LO verifies the implementation, and the focused commit contains only approved paths."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run TEST-11656 plus focused daemon/probe tests proving due-state classification, asynchronous single-flight launch, A-live suppression, bounded backoff, atomic evidence replacement, fail-closed readiness, and a fresh governed A dispatcher completion. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` | Inject refresh success, in-progress, and failure outcomes and prove bounded stable diagnostics preserve overall PASS/WARN/FAIL semantics without treating eligible A as a topology/configuration failure. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run the real private-desktop workspace-write sentinel contract and prove zero visible windows, schema-v3 validity, exact effective profile, complete sentinel lifecycle, and no weakened consumer validation. |
| `GOV-RELIABILITY-FAST-LANE-001` | Inspect the final diff and commit: no new public CLI or configuration surface, at most the two existing source modules plus one focused test module, and no unrelated mutation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Prove the persistent daemon exclusively owns refresh initiation and ordinary A dispatch still follows daemon-observed bridge work; no hook, poller, or second scheduler is introduced. |

## Acceptance Criteria

- TEST-11656 passes: before expiry, one bounded private-desktop refresh renews valid evidence and one fresh governed dispatcher-produced A Prime Builder item exits zero and advances its assigned bridge document.
- Concurrent live A work suppresses refresh without changing A eligibility; live D/F workers continue unaffected. Repeated daemon ticks cannot create duplicate refreshes.
- Probe failure, timeout, malformed evidence, visible-window detection, model-cache diagnostic failure, or nonzero wrapper result remains fail closed with one stable diagnostic and bounded retry; no false readiness or expiry extension occurs.
- Shadow mode and dry-run perform no refresh spawn or evidence mutation. Dispatcher configuration, roles, routing, caps, allowances, TAFE, leases, and unrelated worktree bytes remain unchanged.
- Evidence writes are atomic, target files are hunk-isolated from foreign dirty work, focused tests pass, independent LO verifies the implementation, and the focused commit contains only approved paths.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_codex_no_window_refresh.py`

## Recommended Commit Type

`feat`
