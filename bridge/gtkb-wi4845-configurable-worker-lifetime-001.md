NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e6490e91-a7fd-489d-be63-363714e9ba47
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: prime_proposal
Document: gtkb-wi4845-configurable-worker-lifetime
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4845
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP
target_paths: ["scripts/run_with_status.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_run_with_status.py"]

## Summary

Make the dispatched-worker lifetime cap configurable so headless Loyal Opposition and verification workers can complete a full bridge review instead of being killed mid-flight. This implements the WI-4845 fix authorized by owner decision DELIB-20266136 (AUQ 2026-06-25, "Configurable cap + LO budget").

## Problem / Root Cause (confirmed)

scripts/run_with_status.py hardcodes DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS = 600 and kills the worker process tree at 600s wall-clock (exit 124). The dispatcher (scripts/cross_harness_bridge_trigger.py) wraps every spawn in run_with_status.py with no lifetime override, so all dispatched workers inherit the 600s cap. A cloud-routed LO worker's own inner bounds are max_turns = 80 (DEFAULT_MAX_TURNS, raised by WI-4734 for full bridge verification) and a 240s per-HTTP-call timeout — an inner ceiling near 19200s — so the 600s wall-clock kill always bites first. A genuine LO review (read the full bridge version chain, the proposal, and the linked specs; run the two Bash-subprocess preflights; deliberate over many slow cloud-model turns; author the verdict; run the write_verdict finalization helper) routinely exceeds 600s and is terminated mid-review. Because openrouter_harness.py prints its result only after run_tool_loop returns, a mid-loop kill yields 0-byte stdout and no verdict file — the exact observed failure signature (dispatch-runs 2026-06-25T21:36Z, openrouter F exit 124). The 600s value was WI-4806's deliberately blunt storm-era stopgap to kill immortal workers; its own source comment defers configurability to "the Phase 2 daemon" (WI-4787), which shipped in shadow mode and does not run dispatch.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) — dispatcher architecture-of-record; the worker-lifetime cap is a dispatch-substrate parameter governed here. The fix conforms to the persistent-daemon direction by making the cap a parameter the daemon can later own.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (requirement) — the centralized dispatch service must reliably produce verdicts; a worker killed before emitting a verdict violates this. The fix restores verdict production for slow-but-legitimate reviews.
- DCL-DISPATCH-ENVELOPE-RULES-001 (design_constraint) — dispatch-envelope conformance; the lifetime parameter is part of the dispatch envelope and must remain bounded. The fix keeps a default bound (600s) and adds a review-appropriate bound (~1800s) without removing the cap.
- GOV-FILE-BRIDGE-AUTHORITY-001 (governance) — bridge protocol authority; this proposal is filed as an append-only numbered bridge file through the governed writer path and seeks Loyal Opposition GO before any implementation.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (design_constraint) — VERIFIED requires spec-derived executed tests; the test plan below derives tests from the linked dispatch specs and will be executed against the implementation.
- GOV-RELIABILITY-FAST-LANE-001 (governance) — reliability fast-lane context; WI-4845 is an origin=defect dispatch-reliability fix. This proposal follows the full bridge protocol rather than claiming fast-lane because it adds a small CLI surface (--lifetime).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (design_constraint) — this proposal cites every governing specification relevant to the dispatch-substrate change; the Specification Links here satisfy the concrete-links requirement.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (architecture_decision) — the fix is captured as durable artifacts (this bridge thread, DELIB-20266136, the PAUTH, and spec-derived tests) rather than transient activity.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (design_constraint) — the work-item-to-test lifecycle trigger is honored: WI-4845 yields the spec-derived tests enumerated below.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (governance) — artifact-oriented governance default stance; the change is proposed, reviewed, implemented, and verified through governed artifacts.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (reliable verdict production), ADR-DISPATCHER-ARCHITECTURE-001 (dispatch-substrate architecture), DCL-DISPATCH-ENVELOPE-RULES-001 (bounded dispatch envelope), and the WI-4806 deferred-configurability intent recorded in scripts/run_with_status.py and DELIB-20266136. No new or revised requirement is needed; this is a defect fix that realizes already-specified reliable-dispatch behavior.

## Prior Deliberations

- DELIB-20266136 — owner decision authorizing this exact fix (configurable cap + LO budget), AUQ 2026-06-25.
- DELIB-20266132 — WI-4670 re-scope/close that forked the cloud-LO-completion residual into WI-4845.
- bridge/gtkb-run-with-status-worker-lifetime-timeout-002.md — the WI-4806 thread that added the 600s cap and explicitly deferred configurability to the Phase 2 daemon; this proposal realizes that deferred work.
- WI-4828 (lease/liveness storm-watchdog) and WI-4472 (concurrency cap) — the storm controls that make a longer LO-review lifetime safe; the 600s cap is no longer the primary storm control.

## Proposed Implementation

1. scripts/run_with_status.py: extend the leading flag-parse loop to accept --lifetime <seconds> alongside --stdin/--stdout/--stderr. Default to the existing module constant DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS (600) when --lifetime is absent, preserving current behavior and the test monkeypatch surface. Use the parsed value in p.wait(timeout=...) and in the lifetime-timeout message. Validate that --lifetime is a positive number and fail closed on a non-positive or non-numeric value.

2. scripts/cross_harness_bridge_trigger.py: add a module constant LO_REVIEW_WORKER_LIFETIME_SECONDS (1800) and insert --lifetime <value> into the run_with_status.py argument list at the wrapped_command construction, where value is LO_REVIEW_WORKER_LIFETIME_SECONDS when target.needed_role_label == "loyal-opposition" and the existing default otherwise. This is the keystone bootstrap: a dispatched LO review can then complete and emit a verdict.

3. platform_tests/scripts/test_run_with_status.py: add regression tests deriving from the linked specs (see the Spec-Derived Test Plan).

The 80-turn ceiling (DEFAULT_MAX_TURNS), the 240s per-HTTP-call timeout, the WI-4828 lease/liveness storm-watchdog, and the WI-4472 concurrency cap are retained unchanged as the runaway guards, so a longer LO lifetime does not re-open the storm.

## Spec-Derived Test Plan / Verification

| Spec / clause | Derived test | Assertion |
|---|---|---|
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (verdict within budget) | test_lifetime_arg_sets_wait_timeout | --lifetime N causes p.wait to receive timeout=N |
| DCL-DISPATCH-ENVELOPE-RULES-001 (bounded default preserved) | test_default_lifetime_preserved_when_absent | absent --lifetime uses DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS (600) |
| ADR-DISPATCHER-ARCHITECTURE-001 (substrate parameter validated) | test_lifetime_rejects_nonpositive | non-positive or non-numeric --lifetime fails closed |
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (LO budget routing) | test_dispatch_lo_gets_review_lifetime (test_cross_harness_bridge_trigger.py) | an LO/verification dispatch wraps with --lifetime 1800; a non-LO dispatch uses the default |

Execution at report time: run `python -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`, plus `python -m ruff check` and `python -m ruff format --check` on the three changed files. The implementation report will carry the executed results.

## Risk / Rollback

Risk: a longer LO-review lifetime (1800s) lets a worker live longer, marginally increasing exposure if a worker truly hangs. Mitigation: the inner 80-turn ceiling, the 240s per-call timeout, the WI-4828 lease/liveness storm-watchdog, and the WI-4472 concurrency cap all remain; the storm's real controls are unchanged, and the non-LO default stays at 600s. Rollback: revert the three files; the change is additive (a new optional --lifetime arg whose default equals current behavior), so reverting restores the exact prior behavior.

## Owner Decisions / Input

- DELIB-20266136 (AskUserQuestion, 2026-06-25): owner selected "Configurable cap + LO budget (Recommended)" for the WI-4845 fix, authorizing draft, cross-review, and implementation. This proposal implements exactly that decision. Implementation authority: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP (source + test).

## Review Note

Headless LO review is the defect under repair, so this proposal must be cross-reviewed by an independent-session harness acting as Loyal Opposition (Cursor, Antigravity, or a separate Claude-LO session), not by headless dispatch. Once implemented and VERIFIED, headless LO review is restored.
