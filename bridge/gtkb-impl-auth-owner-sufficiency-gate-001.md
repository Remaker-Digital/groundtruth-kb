NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5
author_model_version: 2026-06-02
author_model_configuration: default

# Implementation Proposal - Implementation-Start Owner Sufficiency Clarification Gate

bridge_kind: prime_proposal
Document: gtkb-impl-auth-owner-sufficiency-gate
Version: 001
Date: 2026-06-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-IMPL-AUTH-OWNER-SUFFICIENCY
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4241

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Fix the implementation-start authorization gate so a GOed bridge proposal that is otherwise valid, but whose `## Requirement Sufficiency` body is outside the bounded parser phrase set, can consume one explicit durable owner-decision deliberation as Requirement Sufficiency evidence. The fix keeps bridge GO, project authorization, target path extraction, specification linkage, and spec-derived verification checks fail-closed.

## Defect / Reproduction

The bridge reconciliation implementation threads for the audit CLI, index-chain deviation detector, and correction packets currently have live latest `GO` status. Each approved proposal has a `## Requirement Sufficiency` section, but the body uses natural explanatory prose rather than one of the gate's bounded sufficient-state phrases. The implementation-start gate therefore reports that the approved proposal is missing Requirement Sufficiency even though the section is structurally present.

The owner then provided durable clarification in `DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY`: "Existing requirements are sufficient. Please proceed with implementation." The current gate cannot consume that durable owner clarification. Rewriting the already-GOed proposals through a Prime Builder `REVISED` transition is invalid because Prime Builder may only file `REVISED` after `NO-GO`, not after latest `GO`.

## Requirement Sufficiency

Existing requirements sufficient. WI-4241, WI-3454, `DELIB-2026-06-02-IMPL-AUTH-OWNER-SUFFICIENCY-GATE`, and `DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY` are sufficient for this scoped gate correction. The work changes only how the implementation-start gate accepts explicit durable owner evidence for the Requirement Sufficiency field; it does not add new authority to bypass bridge review, project authorization, target paths, spec links, verification plans, or any formal artifact gate.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`, `platform_tests/scripts/test_implementation_start_gate.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The bridge remains the implementation authorization source; the fix requires a GOed bridge thread and does not create an alternate bridge queue.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - This proposal cites an active project authorization for WI-4241, and the gate must continue validating project authorization metadata.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - The project authorization bounds the mutation scope to the gate and tests; no broad status mutation or automatic remediation is allowed.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal includes concrete target paths, spec links, and a spec-derived verification plan.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation must include regression tests mapped to the governing specs and the observed blocked bridge threads.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item metadata are present for the implementation-start gate.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner clarification evidence must be an explicit owner-conversation deliberation with `outcome='owner_decision'`; non-owner or non-decision evidence is rejected.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The owner clarification is preserved as durable deliberation evidence instead of transient chat-only text.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The defect is a lifecycle gate friction point; remediation is tracked as WI-4241 rather than applied as an untracked bulk correction.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The fix uses explicit artifacts, packets, and tests to preserve governance provenance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation work remains within the GT-KB project root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The CLI behavior should be deterministic and usable by either harness, independent of hook-specific review surfaces.
- `GOV-STANDING-BACKLOG-001` - WI-4241 records the work in the MemBase backlog and is not a second backlog authority.
## Prior Deliberations

- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` - Owner directed the bridge reconciliation project and bounded proposal batch.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY` - Owner clarified that existing requirements are sufficient for the blocked bridge reconciliation implementation threads.
- `DELIB-2026-06-02-IMPL-AUTH-OWNER-SUFFICIENCY-GATE` - Owner directed the governed gate-fix path when valid bridge transitions could not return latest-GO threads to proposal revision state.
- `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` - Precedent for aligning the implementation-start gate with GO-time review semantics while keeping fail-closed checks.

## Owner Decisions / Input

- `DELIB-2026-06-02-IMPL-AUTH-OWNER-SUFFICIENCY-GATE` - Owner authorized a governed work item to let the implementation-start gate consume durable owner clarification evidence.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-REQ-SUFFICIENCY` - Owner supplied the concrete Requirement Sufficiency clarification for the blocked reconciliation threads.
- `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-IMPL-AUTH-OWNER-SUFFICIENCY` - Active project authorization for WI-4241; forbids bridge GO bypass, broad bulk status mutation, deployment, force push, credential lifecycle changes, spec deletion, and automatic remediation without review.

## Proposed Scope

- Add an explicit owner-sufficiency deliberation option to the begin command.
- Validate the supplied deliberation against MemBase before issuing a packet: it exists, is owner-conversation evidence, has owner-decision outcome, contains a bounded Requirement Sufficiency phrase, and names either the current bridge id or the proposal's cited work item.
- Apply the owner-deliberation fallback only when the approved proposal's Requirement Sufficiency state is `missing`; an explicit gap remains blocking.
- Preserve all other implementation-start failures exactly as failures, including missing target paths, missing spec links, missing verification plan, inactive project authorization, non-GO status, post-GO awaiting review, path escape, and packet drift.
- Record the fallback in the packet with machine-readable metadata, including the evidence mode, deliberation id, and matched bridge or work-item basis.
- Add regression tests for accepted owner clarification, rejected non-owner evidence, rejected non-decision evidence, rejected non-applicable evidence, and explicit gap precedence.

## Out Of Scope

- Editing the already-GOed reconciliation proposals in place.
- Creating a Prime Builder `REVISED` entry after latest `GO`.
- Broad bulk status mutation or automatic backlog remediation.
- Changing Loyal Opposition GO/NO-GO/VERIFIED transition authority.
- Treating owner clarification evidence as a replacement for target paths, spec links, project authorization, or verification plans.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Read only MemBase deliberation text and bridge metadata; no credentials or environment values. | Credential scan and fixture review. | |
| CQ-PATHS-001 | Yes | Mutate only listed in-root source and test files. | Implementation authorization packet plus git diff review. | |
| CQ-COMPLEXITY-001 | Yes | Add a small validation helper and keep existing gate flow intact. | Unit tests exercise helper behavior and begin integration. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing Requirement Sufficiency phrase constants and DB path helpers. | Tests cover phrase matching and validation failures. | |
| CQ-SECURITY-001 | Yes | Fail closed on missing, non-owner, non-decision, non-applicable, or gap evidence. | Negative tests for each rejected evidence class. | |
| CQ-DOCS-001 | Yes | CLI option help documents that evidence must be explicit durable owner clarification. | CLI help string review in source. | |
| CQ-TESTS-001 | Yes | Add regression tests for the blocked bridge class and the new validation helper. | Targeted pytest for the authorization and gate suites. | |
| CQ-LOGGING-001 | N/A | The gate emits JSON packets and errors, not runtime logs. | N/A. | No logging surface changes. |
| CQ-VERIFICATION-001 | Yes | Verify no-write packet generation and protected-edit gate behavior after implementation. | Targeted pytest plus live no-write checks for the blocked bridge ids. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: test that authorization still requires a GOed bridge and rejects non-GO or awaiting-review states.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: existing project authorization tests continue to pass; add integration coverage where owner evidence coexists with PAUTH metadata.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: regression verifies owner evidence does not bypass inactive or invalid project authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: regression verifies owner evidence does not bypass missing spec links or target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: regression verifies owner evidence does not bypass missing verification plan.
- `SPEC-AUQ-POLICY-ENGINE-001`: tests reject non-owner and non-`owner_decision` deliberations and accept captured owner clarification only when applicable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: packet metadata records the deliberation id so the owner clarification is durable and auditable.

## Acceptance Criteria

- The begin command succeeds for the blocked bridge reconciliation threads when supplied with the captured sufficiency deliberation.
- The same command without owner-sufficiency evidence continues to reject those threads until their proposals are revised through a valid future bridge lifecycle.
- Explicit requirement-gap text remains a hard block even if owner evidence is supplied.
- Non-owner, non-decision, missing, or non-applicable deliberation ids are rejected.
- The packet records the owner deliberation id and evidence basis.
- Targeted authorization and gate tests pass.

## Risks / Rollback

The risk is over-accepting owner evidence and weakening the bridge proposal standard. The mitigation is an explicit CLI argument, MemBase validation, bounded phrase matching, bridge/work-item applicability checks, and no fallback for explicit gap declarations or any other gate failure. Rollback is to remove the new option and helper; existing begin behavior remains intact when the option is absent.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Recommended Commit Type

`fix`
