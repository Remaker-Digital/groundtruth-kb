NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; user goal continuation

# WI-5279 Project Authorization Bootstrap Lifecycle

Document: gtkb-wi5279-project-authorization-bootstrap-lifecycle
Version: 001
bridge_kind: prime_proposal

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5279
target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Summary

Prime Builder proposes a bounded implementation for `WI-5279`: add an explicit, non-bypass project-authorization bootstrap lifecycle so a first or replacement PAUTH transaction can be executed only through a durable, case-bound claim/start path. The implementation will not make ordinary `governance_advisory`, `operational_state_change`, or other terminal/non-implementation `GO` verdicts generally claimable.

The proposal exists to clear the Authority Foundations blocker called out by `bridge/gtkb-authority-foundations-project-authorization-004.md`, which requires an executable bootstrap claim/start submode before `WI-5277` can safely proceed.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-5279`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and the latest `NO-GO` at `bridge/gtkb-authority-foundations-project-authorization-004.md` are sufficient to define the implementation. No new formal requirement is requested by this proposal.

## Problem

The current bridge and PAUTH lifecycle has a bootstrap contradiction:

1. Ordinary implementation proposals require a current PAUTH metadata line before they can receive executable implementation authority.
2. A first or replacement PAUTH transaction may be exactly the work needed to create or replace that authority.
3. Treating an advisory or operational-state `GO` as an ordinary implementation `GO` makes terminal/non-implementation bridge kinds claimable, which violates `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.
4. Relying on prose owner intent does not bind a claim kind, start packet, target carrier, single-use semantics, or evaluator branch.

The result is a recurring deadlock: the work needed to correct project authorization cannot pass the same project-authorization gates unless a bypass is introduced, but bypasses are explicitly disallowed.

## Proposed Implementation

Add a special bootstrap path with three mechanical properties.

First, introduce a new explicit claim kind in `scripts/bridge_work_intent_registry.py`, tentatively `project_authorization_bootstrap`. The generic `claim` path must continue to deny ordinary `GO` claimability for non-implementation bridge kinds. A bootstrap claim must be acquired only through a dedicated CLI subcommand and only when all of the following hold:

- latest bridge status is `GO`;
- the approved proposal declares a bootstrap lifecycle marker for project authorization;
- the proposal cites the exact owner decision or project-scope PAUTH that authorizes the bootstrap;
- the proposal declares `groundtruth.db` or an equivalent MemBase carrier target for the future PAUTH transaction;
- the request binds one bridge slug, one project id, one work item id, one owner-decision id, one target authorization id or proposed authorization id, and one session id;
- no existing bootstrap claim for the same bridge is active or already consumed.

Second, extend `scripts/bridge_claim_cli.py` with a dedicated bootstrap command, tentatively:

```text
python scripts/bridge_claim_cli.py claim-bootstrap <slug> --owner-decision <DELIB-ID> --project <PROJECT-ID> --work-item <WI-ID> --authorization-id <PAUTH-ID> --carrier groundtruth.db
```

The exact command spelling may change during implementation if the codebase already has a better naming convention, but the final interface must expose a distinct bootstrap claim path and must not reuse generic `claim` as the sole control.

Third, extend `scripts/implementation_authorization.py` and `scripts/implementation_start_gate.py` so `begin` can create and validate a schema-v3 start packet for the bootstrap claim kind. The packet must include a `bootstrap_authority` object or equivalent stable field carrying:

- `claim_kind`;
- `owner_decision_id`;
- `project_id`;
- `work_item_id`;
- `bridge_id`;
- `authorization_id` or proposed authorization id;
- `carrier_targets`;
- `single_use` state;
- pre-start packet hash;
- work-intent claim row evidence.

The evaluator must fail closed if any field drifts between proposal, claim, start packet, and protected mutation. The start gate must authorize only the declared PAUTH carrier transaction targets; it must not authorize source/test/config mutation under a bootstrap packet unless those paths are separately in target scope under an ordinary implementation packet.

## Explicit Non-Goals

- Do not make all latest `GO` verdicts claimable.
- Do not make `governance_advisory`, `operational_state_change`, `ADVISORY`, `DEFERRED`, `WITHDRAWN`, or other non-implementation bridge kinds ordinary implementation work.
- Do not execute the pending Authority Foundations PAUTH create/revoke transaction in this work item.
- Do not mutate `groundtruth.db` as part of this implementation proposal except for normal work-intent/packet runtime evidence created by governed tooling during claim/start verification.
- Do not authorize WI-5178, WI-5184, WI-5249, WI-5255, WI-5277, or black-box WI-5268/WI-5269..WI-5276 implementation.
- Do not perform Git push, release, production deployment, credential lifecycle, destructive cleanup, external-system mutation, or git history rewrite.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5279; bridge/gtkb-authority-foundations-project-authorization-004.md; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
  "primary_route": "bridge_claim_cli explicit bootstrap claim plus implementation_authorization begin plus implementation_start_gate validation",
  "before_behavior": "A project-authorization bootstrap attempt is forced toward either a prose exception or an ordinary GO claim path that is not mechanically limited to a single PAUTH carrier transaction.",
  "after_behavior": "A project-authorization bootstrap attempt uses a named claim kind and packet authority object whose owner decision, project, work item, bridge, authorization id, carrier target, session, and single-use fields are checked before protected mutation.",
  "self_descriptive_naming": "The claim kind, CLI subcommand, packet field, and gate diagnostics use project_authorization_bootstrap terminology instead of generic implementation language.",
  "obsolete_guidance_disposition": "Existing prose-only bootstrap guidance remains historical evidence but stops being used as executable authority after the mechanical lifecycle is available.",
  "history_preservation": "The numbered bridge chain, work-item records, PAUTH records, and implementation-start packet evidence remain append-only; this proposal does not rewrite prior Authority Foundations bridge files.",
  "baseline": {
    "known_blocker": "WI-5277 latest NO-GO requires WI-5279 or a durable bound exception before another GO",
    "generic_go_claim_risk": "ordinary GO claimability cannot distinguish a bootstrap exception from ordinary implementation work",
    "pauth_transaction_state": "no PAUTH create or revoke transaction is executed by this proposal"
  },
  "expected_result": {
    "bootstrap_claim_kind": "project_authorization_bootstrap",
    "generic_nonimplementation_go_claimable": false,
    "packet_contains_bootstrap_authority": true,
    "drift_fails_closed": true,
    "unrelated_target_authorized": false
  },
  "rollback": {
    "instructions": "Revert only the target source and test hunks introduced for WI-5279; do not execute or roll back any PAUTH carrier transaction because none is in scope.",
    "test": "Re-run the focused work-intent, implementation-authorization, and implementation-start gate tests."
  },
  "hard_invariants": [
    "No ordinary non-implementation bridge GO becomes generically claimable.",
    "A bootstrap packet cannot authorize unrelated source, test, configuration, dispatcher, credential, release, or external-system mutation.",
    "The owner decision, project id, work item id, bridge id, authorization id, carrier target, session id, and single-use state are hash-bound or fail closed.",
    "The pending Authority Foundations PAUTH transaction remains separately bridge-governed."
  ],
  "fail_closed_conditions": [
    "Missing or mismatched owner decision id.",
    "Missing or mismatched project, work item, bridge, authorization id, or carrier target.",
    "Generic claim path used instead of the bootstrap command.",
    "Attempted reuse of a consumed bootstrap authority.",
    "Attempted mutation outside the declared carrier target."
  ],
  "essential_context_preservation": "This work preserves the Authority Foundations NO-GO chain, the WI-5279 backlog record, the project-scoped PAUTH evidence, and the no-bypass distinction between bootstrap authority and ordinary implementation authority."
}
```

## Target Paths

```json
[
  "scripts/bridge_work_intent_registry.py",
  "scripts/bridge_claim_cli.py",
  "scripts/implementation_authorization.py",
  "scripts/implementation_start_gate.py",
  "platform_tests/scripts/test_bridge_work_intent_registry.py",
  "platform_tests/scripts/test_implementation_authorization.py",
  "platform_tests/scripts/test_implementation_start_gate.py"
]
```

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-Derived Verification Plan

| Specification / requirement | Verification |
| --- | --- |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Add tests proving generic `claim` still denies non-implementation/terminal bridge-kind `GO` claimability and only the explicit bootstrap claim path can create the bootstrap claim kind. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Add tests proving bootstrap claim/start binds owner decision, project id, work item id, authorization id, carrier target, session id, and bridge slug; drift in any field fails closed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Add tests proving the bootstrap path produces an implementation-start packet with explicit bootstrap authority and does not authorize unrelated source/test/config paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Add proposal fixtures or tests showing bootstrap proposals still carry project/PAUTH/WI metadata or a specifically validated bootstrap equivalent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused tests listed below and include exact observed results in the implementation report. |

Expected focused commands:

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
```

## Acceptance Criteria

1. A distinct bootstrap claim kind exists and is persisted in the work-intent carrier.
2. A dedicated CLI path can acquire the bootstrap claim only for an eligible latest-`GO` bootstrap proposal.
3. Generic `claim` remains non-authoritative for terminal/non-implementation bridge kinds.
4. `implementation_authorization.py begin` emits a schema-v3 packet that binds the bootstrap authority fields and hashes them.
5. `implementation_start_gate.py` validates bootstrap packets and denies drift, unrelated targets, missing owner decision, missing carrier target, reused/consumed bootstrap state, or wrong session.
6. Focused regression tests cover positive bootstrap claim/start and negative generic-claim, drift, missing-field, wrong-target, and reuse paths.
7. No pending Authority Foundations or black-box PAUTH transaction is executed under this proposal; those remain separate bridge-governed work after this lifecycle is verified.

## Rollback

If the implementation fails review, revert only the source and test changes in the target list. Because this proposal does not execute any PAUTH carrier transaction, rollback does not require database repair beyond removing transient work-intent or implementation-start runtime state created during tests.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the active Authority Foundations project-scope PAUTH used by this proposal.
- `WI-5279` records the owner directive to provide an executable non-bypass project-authorization bootstrap lifecycle.
- No new owner decision is requested by this proposal.

## Prior Deliberations

- `DELIB-202666274` - active Authority Foundations project-scope authorization.
- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - project envelope and quarantine boundary that exposed the bootstrap gap.
- `bridge/gtkb-authority-foundations-project-authorization-002.md` - first NO-GO identifying the bootstrap contradiction.
- `bridge/gtkb-authority-foundations-project-authorization-004.md` - latest NO-GO requiring WI-5279's executable bootstrap lifecycle or a durable bound exception.
- `WI-5279` - backlog record for the missing executable bootstrap lifecycle.

## Pre-Filing Preflight

Draft content-file preflight before filing:

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-drafts/gtkb-wi5279-project-authorization-bootstrap-lifecycle-001.md --json`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
  - `blocking_errors: []`
  - packet hash from the initial draft run: `sha256:64b242aec49f04a0be3ffefd18e3c48fe9520d709e1d612cb8adac1f44be1640`
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-drafts/gtkb-wi5279-project-authorization-bootstrap-lifecycle-001.md`
  - exit code `0`
  - must-apply clauses: `2`
  - blocking gaps: `0`

The exact filed version must pass the same checks after helper metadata insertion and before Loyal Opposition `GO`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
