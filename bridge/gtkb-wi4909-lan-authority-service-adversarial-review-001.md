NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive-default
author_metadata_source: interactive-codex-explicit

bridge_kind: governance_advisory
Project Authorization: PAUTH-PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-ADR-DRAFTING
Project: PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY
Work Item: WI-4909
target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-15-37-lan-authority-service-architecture-decision-packet.md"]
implementation_scope: none
requires_verification: false

# WI-4909 Loyal Opposition Review Request - LAN Authority Service Architecture Decision Packet

Document: gtkb-wi4909-lan-authority-service-adversarial-review
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-04 UTC

## Bridge-Kind Disclosure

This is a non-implementation governance review request. It asks Loyal Opposition to review a candidate, non-authoritative Architecture Decision Packet. It does not request protected source mutation, protected test mutation, project substrate migration, bridge implementation dispatch, or protected-file authorization.

A `GO` response means Loyal Opposition found no material formalization blocker and may still include risks, required owner questions, or recommended edits. A `NO-GO` response means Loyal Opposition found defects, contradictions, missing decisions, or formalization blockers that must be resolved before `WI-4910` owner grilling and `WI-4911` formal artifact candidate drafting proceed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status-bearing files remain the role handoff and review mechanism.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this request carries project, PAUTH, and work-item linkage for a non-implementation advisory review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cited to satisfy mechanical bridge applicability checks; this file is not an implementation proposal and requests no implementation mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cited to satisfy mechanical bridge applicability checks; requested LO output is an adversarial review verdict, not post-implementation verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the candidate packet preserves a discovery artifact before any formal ADR/DCL/GOV mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner decisions, risks, formalization candidates, and follow-on WIs must be captured as governed artifacts when they become load-bearing.
- `GOV-20` - formal governance artifacts remain a follow-on step under the active PAUTH.

## Bridge Chain Evidence

This request is filed as the append-only numbered bridge file `bridge/gtkb-wi4909-lan-authority-service-adversarial-review-001.md`. The prior bridge file chain is not edited or deleted. Loyal Opposition should respond by adding the next numbered bridge file in this same thread.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `WI-4909` acceptance criterion | Loyal Opposition review of the packet and follow-on bridge `GO` or `NO-GO` verdict | no | pending LO review |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No implementation tests are requested; the requested evidence is the LO review verdict with packet, deliberation, and project/PAUTH citations | no | pending LO review |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Status-bearing numbered bridge files for this thread | yes | this request is filed through the bridge-propose helper |

## Prior Deliberations

- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-FIRST-RELEASE` - owner chose discovery-first release planning before implementation umbrellas.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-LAN-AUTHORITY-SERVICE` - owner chose a central LAN GT-KB authority/control-plane service with registered workers and authenticated tablet UI access.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-FIRST-DELIVERABLE-ARCHITECTURE-DECISION-PACKET` - owner chose an Architecture Decision Packet as the first concrete deliverable.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-ADP-INSIGHTS-DROPBOX-LOCATION` - owner chose `CODEX-INSIGHT-DROPBOX` and `INSIGHTS-...` classification for the non-authoritative packet.
- `DELIB-20266595` - owner approved the runtime-orchestration discovery PAUTH used here.

## Review Target

Review this packet:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-15-37-lan-authority-service-architecture-decision-packet.md`

The packet is explicitly non-authoritative and candidate-only. Treat it as the evidence base for later `WI-4910` owner grilling and `WI-4911` formal artifact candidate drafting, not as an implementation proposal.

## Requested Loyal Opposition Review

Please review for the `WI-4909` acceptance criterion: PASS when an LO review report identifies defects, risks, missing decisions, and formalization blockers, or records no material blockers with evidence.

Focus areas:

- source-of-truth boundaries among MemBase, bridge artifacts, dispatcher state, TAFE/lifecycle events, service records, and dashboard projections
- dispatch safety, including bridge latest status, work-intent claims, target-path authorization, implementation-start evidence, and NO-ACTION/circuit-breaker behavior
- service ownership ambiguity, especially whether the service can own live state without becoming a second backlog authority
- security model gaps for worker/tablet authentication, credential storage, token rotation, and auditability
- tablet launch constraints and whether the proposed first-release actions overreach
- SQLite-first versus PostgreSQL-first posture, including corruption and migration risks
- implementation-slice sequencing and rollback risk
- consistency with the July 2 OPS lifecycle/dispatcher consolidation report, which is also non-authoritative

## Expected Output

Please file the next bridge version as `GO` or `NO-GO` with:

- findings ordered by severity
- evidence citations to packet sections, owner deliberations, project/PAUTH state, current bridge/dispatcher rules, or live code/settings where relevant
- required corrections or owner decisions before `WI-4910` and `WI-4911`
- a clear statement whether the packet is sufficient to proceed to owner grilling, formalization candidate drafting, both, or neither

## Out Of Scope

- source implementation
- protected tests mutation
- runtime service scaffolding
- dispatcher migration
- project authorization broadening
- final ADR/DCL/GOV insertion

## Architecture Alignment Ledger

- OPS consolidation: review should ensure the packet keeps OPS work artifact-centric and does not replace bridge proposal/verdict/report/verification semantics.
- Dispatcher daemon architecture: review should check that the live dispatcher remains authoritative until a verified migration slice changes a bounded responsibility.
- Lifecycle-first/scoring-last: review should verify that actionability and authorization gates precede lane scoring and model routing.
- Portfolio reconciliation: review should confirm the packet does not reopen terminal dispatcher modernization WIs or create duplicate project-family authority.
