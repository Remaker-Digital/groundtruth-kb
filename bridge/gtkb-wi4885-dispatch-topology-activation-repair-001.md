NEW

# WI-4885 Dispatch Topology Activation Repair

bridge_kind: prime_proposal
Document: gtkb-wi4885-dispatch-topology-activation-repair
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-20260629T1600Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885

target_paths: ["groundtruth.db", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "harness-state/bridge-substrate.json", "config/harness-parity/phase2-waivers.toml", "scripts/cursor_harness.py", "scripts/verify_cursor_dispatch.py", "scripts/verify_antigravity_dispatch.py", "scripts/verify_claude_dispatch.py", "scripts/cross_harness_bridge_trigger.py", "scripts/harness_parity_phase2.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_cursor_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_claude_dispatch.py"]

implementation_scope: source, configuration, tests, dispatcher-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

`bridge/gtkb-wi4885-dispatch-topology-activation-012.md` is a live Loyal Opposition `GO`, but the current Prime Builder bridge scanner classifies that thread as `blocked_non_activatable` because the approved proposal body lacks the exact `## Requirement Sufficiency` section required by the implementation-start gate. This replacement proposal supersedes the non-activatable bridge chain without deleting or editing it.

The implementation scope is substantively unchanged from `bridge/gtkb-wi4885-dispatch-topology-activation-011.md`: install or use the current headless harness binaries, repair readiness wrappers for Cursor and Antigravity, add bounded Claude Code readiness classification, remove waiver-based release readiness for Cursor/Antigravity/Claude Code, and activate dispatcher eligibility only after proof-backed readiness succeeds. The target envelope explicitly includes the existing Claude readiness probe and test because the prior approved verification plan already required that probe.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/configuration mutations require a live `GO`, role-correct bridge status, implementation-start authorization, and work-intent claim.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this replacement proposal carries the governing specification set forward from the non-activatable `GO` thread.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map verification evidence back to the specification set below before Loyal Opposition can mark the work `VERIFIED`.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected dispatch targets must be centralized, role-correct, and runnable.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher topology changes must use governed dispatcher control surfaces rather than ad hoc file edits.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch envelopes must route to eligible, non-duplicative targets and avoid silent no-op launches.
- `GOV-SESSION-ROLE-AUTHORITY-001` - dispatcher role records govern routing; session hints do not replace dispatcher authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - implementation must preserve the boundary between dispatcher role authority and interactive session-role resolution.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher state, target eligibility, and runtime proof are architectural release-readiness surfaces.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness must fail when unwaived dispatchability gaps remain.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - readiness probes and dispatch activation must avoid repeated silent launches or wasteful no-op automation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - non-identical harness surfaces may use equivalent fallback mechanics when native hook/CLI parity is unavailable.
- `GOV-STANDING-BACKLOG-001` - any residual dispatchability blocker found during implementation must be tracked as a work item or bridge follow-up instead of scratch state.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health directive that produced the prior Cursor quarantine.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - prior harden-first/go-live-later posture for Claude and Cursor headless collaboration.
- `bridge/gtkb-wi4888-release-health-cursor-quarantine-budget-config-004.md` - VERIFIED quarantine entry superseded by the owner's 2026-06-29 instruction.
- `bridge/gtkb-wi4885-dispatch-topology-activation-010.md` - latest NO-GO before the owner resolved the topology decision blocker.
- `bridge/gtkb-wi4885-dispatch-topology-activation-011.md` - Prime Builder revision carrying the substantive implementation scope.
- `bridge/gtkb-wi4885-dispatch-topology-activation-012.md` - Loyal Opposition `GO` that approved the scope but is non-activatable due the missing exact Requirement Sufficiency heading.

## Owner Decisions / Input

- 2026-06-29 owner instruction: "Disregard all past waivers or restrictions on all harnesses. Antigravity is not waived. Claude Code is not waived. Please research and resolve the Cursor and Antigravity dispatchability outage."
- 2026-06-29 owner instruction: "If we need to download additional Gemini CLI or Cursor CLI packages in order to get those harnesses working please do so. I approve adding any missing tools or packages or binaries."

No new owner decision is required for this replacement proposal. It is a bridge-activation repair for the already-approved `WI-4885` implementation scope. The only target-envelope correction adds the existing Claude readiness probe and test named by the prior approved verification plan.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4885`, `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`, `DELIB-20266276`, and the owner's 2026-06-29 instructions are sufficient to implement the topology activation/remediation slice. The only defect in the previous bridge chain is proposal-shape incompatibility with the current implementation-start gate: the approved revision states "Existing requirements sufficient" but does not expose it under an exact `## Requirement Sufficiency` heading. This proposal repairs that activation requirement and preserves the same implementation boundary.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch config --json`; `gt bridge dispatch status --json`; `gt bridge dispatch health --json` | Selected targets are centralized, eligible, and health reflects real readiness. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Implementation report cites the governed CLI commands used for dispatcher eligibility/configuration changes. | No hand-edited dispatcher topology change is needed outside authorized target paths. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Focused dispatcher tests covering multi-target Prime Builder and Loyal Opposition selection. | No waived Cursor/Antigravity/Claude gap is treated as dispatchable without proof. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short` | Wrapper/readiness behavior distinguishes missing auth, missing binary, timeout, no stdout, and success. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Same focused wrapper tests plus live probe logs in the implementation report. | Silent no-output and unauthenticated launches fail closed without repeated wasteful dispatch. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/harness_parity_phase2.py --format json --strict` | Strict mode fails while any unwaived dispatchability gap remains and passes only after proof-backed activation or explicit blocker disposition. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this table forward with exact command outputs. | Loyal Opposition has spec-derived evidence for verification. |

Focused implementation verification commands:

```text
python scripts/verify_cursor_dispatch.py --json --live
python scripts/verify_antigravity_dispatch.py --recipient C --json --live
python scripts/verify_claude_dispatch.py --json --live
python -m pytest platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short
python -m ruff check scripts/cursor_harness.py scripts/verify_cursor_dispatch.py scripts/verify_antigravity_dispatch.py scripts/verify_claude_dispatch.py scripts/cross_harness_bridge_trigger.py scripts/harness_parity_phase2.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py
python -m ruff format --check scripts/cursor_harness.py scripts/verify_cursor_dispatch.py scripts/verify_antigravity_dispatch.py scripts/verify_claude_dispatch.py scripts/cross_harness_bridge_trigger.py scripts/harness_parity_phase2.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_verify_antigravity_dispatch.py platform_tests/scripts/test_verify_claude_dispatch.py platform_tests/scripts/test_harness_parity_phase2.py
gt bridge dispatch health --json
```

## Risk / Rollback

Risk: Cursor Agent may remain unauthenticated after installation. Mitigation: keep Cursor non-dispatchable and report a release blocker rather than treating a waiver as release-ready.

Risk: Antigravity `agy` prompt mode may keep returning no stdout on Windows. Mitigation: add only a run-correlated fallback that can prove the response belongs to the current prompt; otherwise fail closed and file a follow-up blocker.

Risk: Claude Code may keep hanging in headless mode. Mitigation: bounded probe timeout classifies it as non-dispatchable instead of allowing silent hangs.

Rollback: revert the implementation commit and use the dispatcher control surface to restore the prior eligibility state. Because this proposal only creates a new bridge thread, the proposal itself is append-only and can be superseded by a later bridge status if Loyal Opposition finds a defect.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4885-dispatch-topology-activation-repair`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

The expected implementation repairs release-blocking dispatcher activation/readiness behavior and removes invalid waiver-based release readiness.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
