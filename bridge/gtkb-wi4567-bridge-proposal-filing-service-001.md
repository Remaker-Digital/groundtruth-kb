NEW

# Implementation Proposal - WI-4567 Bridge Proposal Filing Service

bridge_kind: prime_proposal
Document: gtkb-wi4567-bridge-proposal-filing-service
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-28 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4567

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py", "platform_tests/skills/test_bridge_propose_helper.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4567 by adding a source-native deterministic command, `gt bridge file-implementation-proposal`, that files a gate-passing NEW implementation proposal end-to-end from a work item, slug, target paths, and owner-decision evidence when new authorization state is needed.

The current flow spreads deterministic ceremony across deliberation capture, project membership, project authorization, proposal metadata, work-intent claim, helper write, author metadata, and preflight checks. This proposal keeps Prime Builder judgment in the proposal body while moving repeatable wiring into a service.

## Claim

Prime Builder proposes a bounded CLI/service implementation that reduces proposal-filing ceremony without bypassing the bridge, owner-decision, project-authorization, author-provenance, or preflight gates.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4567 explicitly defines the acceptance target: "One command files a gate-passing NEW implementation proposal end-to-end: DELIB+PAUTH+membership+header-triple+author-metadata+claim+write+green preflight, with always-applicable doc:* cross-cutting specs auto-seeded." The work item permits either a new `gt bridge file-implementation-proposal` command or extending `gt bridge propose --file`; this proposal selects the new command so the existing draft-only `gt bridge propose` behavior remains stable.

Implementation authority is sufficient for this proposal because `DELIB-20265586` authorized the snapshot-bound project scope and the active project authorization includes `WI-4567`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `platform_tests/skills/test_bridge_propose_helper.py`

No Agent Red or out-of-root artifact is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs PB authority to file NEW proposals and requires bridge status authority to remain role-correct.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The service preserves durable artifacts for owner decisions, project authorization, proposal metadata, and verification evidence rather than relying on chat memory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The filed proposal body must contain concrete specification links, and the command must auto-seed mandatory cross-cutting specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The proposal and implementation report must map linked specifications to verification commands before LO verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The command must inject the machine-readable `Project Authorization`, `Project`, and `Work Item` header lines.
- `GOV-STANDING-BACKLOG-001` - WI-4567 is backlog-governed work inside the deterministic-services project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Any PAUTH reuse or creation must be project-scoped, owner-evidenced, and bounded to the work item.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - If the command mints a PAUTH, it must create a bounded envelope rather than broad ambient authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The filing path must preserve Codex non-bypass compliance behavior when native Write/Edit hooks are unavailable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The implementation is a deterministic artifact service for recurring proposal-filing ceremony.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The command must preserve lifecycle-relevant owner decisions, PAUTHs, and bridge records as governed artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The work is platform bridge tooling only and must not mutate adopter application surfaces.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner-decision capture/reuse must respect the established owner-input policy when PAUTH creation is requested.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - Owner principle: repetitive AI work is a defect; deterministic plumbing belongs in services.
- `DELIB-20265586` - Owner authorized the snapshot-bound project implementation sweep that includes `WI-4567`; this authorization does not bypass bridge review or implementation-start gates.

## Owner Decisions / Input

- `DELIB-20265586` - Owner approved the bounded project authorization shape. The active PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-001-BOUNDED-IMPLEMENTATION-2026-06-23` includes `WI-4567`.
- No new owner decision is required before implementation because this proposal does not change the acceptance target; it chooses the allowed command-name option from WI-4567.

## Proposed Scope

1. Add `gt bridge file-implementation-proposal` under the existing bridge CLI group.
2. Create a source-native proposal filing service in `groundtruth_kb.bridge.proposal_filing` that composes a dispatchable `NEW` proposal body and keeps the current draft-only command separate.
3. Reuse or extend `proposal_autoload` to resolve the work item, active project membership, active PAUTH, owner-decision deliberation, linked specs, target paths, and prior-deliberation candidates.
4. If the work item already has active project membership and an active PAUTH covering it, reuse that state. If membership or PAUTH creation is requested, require explicit owner-decision evidence via a `DELIB-*` id or an owner-decision content file; fail closed when evidence is missing.
5. For PAUTH creation, mint a bounded work-item-scoped authorization with included work item id, included governing specs, and owner-decision deliberation id. Do not create broad project authority.
6. Inject `bridge_kind`, author metadata, project header triple, inline-JSON `target_paths`, specification links, prior deliberations, owner-decision evidence, claim, proposed scope, verification plan, risk/rollback, and recommended commit type into the filed proposal.
7. Acquire bridge work intent before writing and publish through the governed no-index bridge path, preserving the credential scan and Codex compliance audit behavior.
8. Run built-in applicability and ADR/DCL clause preflights against the candidate content before writing. If either preflight blocks, abort without writing a bridge file.
9. After writing, re-run the same preflights against the live bridge id and print the resulting pass/fail evidence.
10. Add focused tests for successful filing in a temp project root, missing-owner-evidence failures, author-metadata resolution, preflight-fail no-write behavior, and target-path/header injection.

## Out of Scope

- Retiring `gt bridge propose`; it remains a non-dispatchable draft generator.
- Bypassing Loyal Opposition review or implementation-start authorization.
- Creating owner decisions without owner-supplied content or an existing `DELIB-*` id.
- Mutating Agent Red or any adopter application.
- Production deployment, push, or release actions.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Add a temp-root CLI test proving `gt bridge file-implementation-proposal` writes exactly one `NEW` bridge file through the governed writer path and refuses an existing slug. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Assert the filed proposal contains `Project Authorization`, `Project`, `Work Item`, `bridge_kind`, and inline-JSON `target_paths` lines. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Assert auto-seeded mandatory specs are present and that explicit `--add-spec` entries are deduped. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Assert the generated filed proposal contains a `## Specification-Derived Verification Plan` section with user-supplied or deterministic verification entries. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Add temp-DB tests for reuse of an active PAUTH, failure when no PAUTH exists and no owner-decision evidence is supplied, and bounded PAUTH creation when evidence is supplied. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Assert the source service runs the same compliance audit before writing and leaves no bridge file when audit/preflight fails. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Assert owner-decision, PAUTH, membership, and bridge evidence are emitted as durable records or explicit citations rather than chat-only assumptions. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Assert target-path validation rejects out-of-root and `applications/Agent_Red` scope for this platform command unless a future adopter-specific proposal authorizes it. |

Expected implementation verification commands:

```text
python -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py platform_tests/skills/test_bridge_propose_helper.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4567-bridge-proposal-filing-service --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4567-bridge-proposal-filing-service
```

## Acceptance Criteria

- `gt bridge file-implementation-proposal --wi <WI> --slug <slug> --target-path <path>...` can file a dispatchable `NEW` proposal without manual bridge file editing when membership and PAUTH already exist.
- The command can create missing membership and a bounded PAUTH only when explicit owner-decision evidence is provided; otherwise it exits nonzero with no bridge write.
- The filed proposal body contains complete author metadata without relying on six manually-set author metadata environment variables in interactive sessions.
- The filed proposal body contains parseable inline-JSON `target_paths`, the machine-readable project header triple, concrete Specification Links, Prior Deliberations, Owner Decisions / Input, Requirement Sufficiency, and a Specification-Derived Verification Plan.
- Built-in applicability and ADR/DCL clause preflights run before write and block writes on failures.
- The command prints live post-write preflight evidence after a successful write.
- Focused tests cover the success path and the failure paths most likely to produce LO NO-GO findings.

## Risks / Rollback

Risk is moderate because the service touches bridge filing and project-authorization plumbing. The main failure mode is accidentally weakening governance by creating PAUTHs without sufficient owner evidence. The implementation must fail closed around owner-decision evidence, existing bridge slug collisions, out-of-root target paths, preflight failures, and author metadata gaps.

Rollback is a single revert of the CLI/service/test changes. Existing bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`
- `platform_tests/skills/test_bridge_propose_helper.py`

## Recommended Commit Type

`feat`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
