NO-GO

# Prime Advisory - Canonical Terminology System And Bounded Context Model

Status: NO-GO on leaving canonical terminology and startup context as implicit documentation concerns.
Author: Codex Loyal Opposition
Date: 2026-05-07
bridge_kind: governance_advisory
origin: owner_requested_codex_advisory
prime_action: prepare_implementation_proposal
index_shape_note: no_preceding_new_expected_for_lo_advisory_bootstrap
Source report:
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-07-16-12-CANONICAL-TERMINOLOGY-SYSTEM-AND-BOUNDED-CONTEXT-ADVISORY.md`

## Bridge Delivery Note

This is an owner-requested Loyal Opposition advisory sent to Prime Builder for an implementation proposal. It is not a response to a Prime implementation proposal, and it does not authorize direct implementation without the normal proposal/review cycle.

The `NO-GO` status is deliberate: the current posture should not remain a partially implicit glossary/startup convention. Prime should file a normal implementation proposal that converts the advisory into scoped, testable GT-KB work.

This file has no preceding `NEW` line because it bootstraps an owner-requested Loyal Opposition advisory to Prime Builder. It follows the prior advisory-bootstrap pattern used by `gtkb-ops-current-state-monitoring-advisory-2026-05-04` and `gtkb-auq-policy-gate-backlog-advisory-2026-05-04`; it is not a missing Prime proposal or a version-numbering anomaly.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory is delivered through the Prime Builder / Loyal Opposition bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Prime's eventual implementation proposal must cite the governing specifications and this advisory source.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any implementation must include spec-derived tests for terminology policy, doctor behavior, startup context, or documentation coverage it changes.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-approved terminology/context framing should become durable implementation work instead of remaining chat-only guidance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposed model should preserve durable artifacts, lifecycle states, and traceable review evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminology additions and context-model changes should have explicit lifecycle states and propagation rules.
- `.claude/rules/canonical-terminology.md` - current live glossary / canonical terminology surface.
- `.claude/rules/deliberation-protocol.md` - requires owner decisions and substantive advisory reports to be preserved in the Deliberation Archive.
- `bridge/gtkb-canonical-terminology-surface-001.md` and follow-on verified implementation thread - prior canonical terminology surface authority.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md` - adjacent startup-context refactor advisory.

## Owner Decisions / Input

- 2026-05-07 owner agreement: "Canonical Terminology System" is the preferred name for the terminology feature.
- 2026-05-07 owner framing: users may add their own terms, but core terminology is implicitly linked to the processes, data, and services GT-KB agents require.
- 2026-05-07 owner requirement: initialized agents must be aware of core canonical terminology, available services, essential artifacts, and how to access them.
- 2026-05-07 owner agreement: GT-KB has a practical complexity ceiling; memory and knowledge systems can consume excessive resources and increase errors if not bounded.

## Claim

Prime should prepare an implementation proposal for a GT-KB slice that promotes the terminology feature to a first-class **Canonical Terminology System** and pairs it with a bounded **Agent Operating Context** model.

## Recommended Prime Action

File a normal implementation proposal for:

```text
GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001
```

The proposal should cover:

1. Canonical Terminology System as a primary GT-KB functional component.
2. Protected platform-owned core terms versus user/project/adopter terms.
3. Accepted synonyms, discouraged synonyms, and examples where common usage differs from GT-KB usage.
4. Collision handling when project terminology tries to redefine a GT-KB core term.
5. Agent Operating Context as a compact startup/retrieval package.
6. The required startup awareness set: core terms, services, essential artifacts, access methods, source-of-truth precedence, active role, and active scope.
7. The Bounded Knowledge Principle: GT-KB should make context discoverable, ranked, scoped, cited, and bounded, not merely abundant.
8. Documentation written for junior developers and fresh agents, not only existing maintainers.

## Suggested Acceptance Criteria

- Public and internal component maps include Canonical Terminology System.
- The glossary/canonical terminology docs explain that GT-KB terms may have meanings distinct from common usage.
- The docs define or propose a term record shape containing canonical term, definition, accepted synonyms, discouraged synonyms, scope, authority level, linked artifacts, linked services, examples, and status.
- Core GT-KB terms are protected from silent project-level redefinition.
- User/project/adopter terminology has a supported extension path.
- Agent startup documentation identifies the compact operating context agents must load or retrieve.
- Complexity control is explicit: startup loads a small always-on core and retrieves task-specific specs, deliberations, tests, and docs on demand.
- Tests or docs checks cover any modified terminology policy, doctor behavior, startup context, and docs surface.

## Decision Needed From Owner

None before Prime drafts the implementation proposal. Future schema choices and collision severity can be brought back through the normal owner-decision channel if Prime finds more than one viable design.
