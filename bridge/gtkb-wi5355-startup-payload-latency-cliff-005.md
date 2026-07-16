REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Revised Implementation Proposal - WI-5355 Startup Payload Latency Cliff Dependency Cleared

bridge_kind: prime_proposal
Document: gtkb-wi5355-startup-payload-latency-cliff
Version: 005
Responds to: bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md
Date: 2026-07-16T22:26:15Z

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5355-STARTUP-PAYLOAD-LATENCY-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5355

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_startup_payload_latency.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat

## Revision Claim

This revision preserves the exact version-001 implementation scope and the
version-002 Loyal Opposition approval rationale. Version 004 issued NO-GO only
because WI-5355 was explicitly sequenced behind terminal WI-5328 verification,
and at that time WI-5328 was still non-terminal.

That dependency has now cleared. Current canonical reads show:

- `gt bridge threads --wi WI-5328 --json --compact` reports
  `gtkb-wi5328-session-envelope-role-writeback` latest `VERIFIED` at
  `bridge/gtkb-wi5328-session-envelope-role-writeback-010.md`.
- `gt backlog show WI-5328 --json` reports `stage: resolved`,
  `resolution_status: resolved`, and completion evidence from the bridge
  VERIFIED backlog reconciler.

Prime Builder therefore requests a fresh independent GO for the already-reviewed
WI-5355 proposal. No source, test, configuration, runtime, dispatcher, TAFE,
credential, Git, release, deployment, or external-system mutation has occurred
under this revision.

## Findings Addressed

### Version 004 dependency blocker - WI-5328 was not terminal

Resolved. WI-5328 is now terminal VERIFIED in bridge state and resolved in the
MemBase backlog. The dependency condition named by versions 002 through 004 is
satisfied.

No implementation scope or target path changes are introduced.

## Specification Links

- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - governing startup payload budget and latency concern.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge chain and role-authorized statuses remain canonical.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - dependency ordering is the sole correction in this revision.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bound to the active project authorization.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - later implementation still requires matching claim and start packet.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass independent GO, implementation report, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised implementation-targeting proposal carries concrete specification links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the later report must provide executed spec-derived latency, JSON-shape, and regression evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the cleared dependency and bridge state are preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the revision keeps work, tests, reports, decisions, and verification as a traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the dependency moved from non-terminal to verified/resolved state and is cited explicitly.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision governance remains intact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - work remains in the GT-KB platform root, not an adopter application.
- `GOV-STANDING-BACKLOG-001` - WI-5355 and WI-5328 status derive from MemBase backlog state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - startup/session hook behavior must retain Codex parity constraints while being repaired.

## Owner Decisions / Input

- `PAUTH-DISPATCHER-BLACK-BOX-WI5355-STARTUP-PAYLOAD-LATENCY-20260716` remains the active bounded authorization for WI-5355.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` remains the owner-decision evidence for bounded fleet defect repair.

No new owner decision is required. The prior blocker was a deterministic bridge
dependency state, and that dependency is now terminal.

## Prior Deliberations

- `bridge/gtkb-wi5355-startup-payload-latency-cliff-001.md` - original implementation proposal.
- `bridge/gtkb-wi5355-startup-payload-latency-cliff-002.md` - independent GO, explicitly sequenced after WI-5328 terminal verification.
- `bridge/gtkb-wi5355-startup-payload-latency-cliff-003.md` - Prime Builder NO-ACTION because WI-5328 was then non-terminal.
- `bridge/gtkb-wi5355-startup-payload-latency-cliff-004.md` - Loyal Opposition dependency-only NO-GO.
- `bridge/gtkb-wi5328-session-envelope-role-writeback-010.md` - current WI-5328 VERIFIED dependency closure.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - bounded owner authorization for discovered fleet defects.

## Requirement Sufficiency

Existing requirements remain sufficient. The work item, active PAUTH, prior GO,
and now-terminal WI-5328 dependency define the implementation boundary. This
revision does not request new requirements, target expansion, or owner waiver.

## Proposed Scope

Same as version 001:

1. Diagnose and repair the direct
   `scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook`
   latency cliff.
2. Preserve real direct-script execution, SessionStart JSON-shape coverage,
   startup intelligence, and fail-soft behavior.
3. Add focused regression coverage in
   `platform_tests/scripts/test_session_startup_payload_latency.py`.
4. Do not merely raise the timeout, terminate unrelated workers, disable
   startup intelligence, or mutate dispatcher/TAFE/runtime eligibility.

## Specification-Derived Verification Plan

| Spec / requirement | Verification | Expected result |
| --- | --- | --- |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | `gt bridge threads --wi WI-5328 --json --compact` and `gt backlog show WI-5328 --json` | WI-5328 latest bridge status is `VERIFIED`; backlog stage/resolution are `resolved`. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Repeated real direct startup-payload executions using the repaired fast-hook path, with phase/end-to-end timing captured. | Material headroom below the production allowance under ordinary concurrent fleet load. |
| Startup JSON contract / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Existing direct execution test for `scripts/session_self_initialization.py` plus focused JSON-shape checks. | Output remains parseable SessionStart JSON and retains required startup intelligence. |
| Slow-phase diagnostics | Focused injected-delay tests in `platform_tests/scripts/test_session_startup_payload_latency.py`. | Delayed internal phase terminates within its own bound and reports a named sanitized phase diagnostic. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the new focused module, the existing direct-execution regression, relevant session-self-initialization tests, Ruff check, Ruff format check, and `git diff --check` on the exact target paths. | All executed evidence is reported in the implementation report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge applicability and clause preflights on this revision and later implementation report. | No missing required specs and zero blocking clause gaps. |

## Acceptance Criteria

- WI-5328 dependency is terminal VERIFIED before WI-5355 implementation starts.
- Repeated direct fast-hook payload executions complete with material documented
  headroom below the production allowance.
- A delayed internal phase reports a bounded sanitized diagnostic rather than a
  generic subprocess timeout.
- Valid output remains parseable SessionStart JSON.
- Existing startup/session-envelope suites do not regress.
- No source or test path outside `target_paths` is mutated by WI-5355.

## Risk and Rollback

Risk is moderate because startup payload generation is broad and historically
slow under concurrent load. The implementation must keep the direct execution
coverage real and avoid hiding the defect by raising test timeouts or disabling
startup intelligence. Rollback is a focused revert of the two target paths plus
the append-only bridge audit chain.

## Fresh Evidence

Commands executed before filing this revision:

```text
gt bridge threads --wi WI-5328 --json --compact
gt backlog show WI-5328 --json
python .codex/skills/bridge/helpers/revise_bridge.py plan gtkb-wi5355-startup-payload-latency-cliff
python scripts/bridge_claim_cli.py claim gtkb-wi5355-startup-payload-latency-cliff --session-id 019f6668-9974-7d72-a456-826f9a67e627 --ttl-seconds 7200
```

Observed:

- WI-5328 bridge latest: `VERIFIED` at
  `bridge/gtkb-wi5328-session-envelope-role-writeback-010.md`.
- WI-5328 backlog: `stage: resolved`, `resolution_status: resolved`, with
  bridge VERIFIED reconciler completion evidence.
- WI-5355 revision plan: next version `005`, latest status before revision
  `NO-GO`.
- WI-5355 draft claim acquired by this Prime Builder session.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
