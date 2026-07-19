REVISED

bridge_kind: governance_advisory
Document: gtkb-authority-foundations-project-authorization
Version: 009
Responds to: bridge/gtkb-authority-foundations-project-authorization-008.md
Supersedes stale executable baseline: bridge/gtkb-authority-foundations-project-authorization-005.md
Date: 2026-07-17 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5277
target_paths: ["groundtruth.db"]

# Revised Authority Foundations Project Authorization - Current Baseline Rebind

## Revision Claim

Prime Builder accepts the version 008 NO-GO. The previous Prime `NO-ACTION`
body at version 007 did not include a detector-recognized
`## Specification-Derived Verification` section, so the mandatory clause gate
could not treat its readback checks as spec-derived evidence.

This revision supplies that section, rebases the proposed single-use
bootstrap transaction onto the current canonical authorization row, and
preserves the hard boundary that no `groundtruth.db` metadata transaction may
occur until a fresh independent GO, matching bootstrap claim, and
implementation-start packet all succeed.

No source, test, configuration, database, dispatcher, TAFE, harness, Git,
credential, deployment, release, or external-system mutation occurred while
filing this revision. This is a bridge-only correction.

## Current Baseline Rebind

The stale version 005 before-state was bound to
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`
version 1. The live canonical row is now version 2. This revision therefore
uses version 2 as the required before-state.

Current canonical before-state:

- ID: `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`
- Status: `active`
- Version: `2`
- Changed at: `2026-07-15T22:22:29+00:00`
- Changed by: `prime-builder/codex/A`
- Owner decision: `DELIB-202666274`
- Project: `PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS`
- Allowed mutation classes: `bridge`, `metadata`, `governance_evidence`,
  `source`, `test`, `configuration`, `documentation`, `runtime_state`
- Registered forbidden operations: `credential_lifecycle`,
  `destructive_cleanup`, `dispatcher_mutation`, `external_system_mutation`,
  `git_commit`, `git_history_rewrite`, `git_push`,
  `production_deployment`, `release`

The replacement target
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715`
is still absent. The successor transaction remains a bounded metadata
transaction: create the exact replacement row, confirm readback, then revoke
the project-scope row only after the replacement readback succeeds.

## Corrected Transaction Scope

After a fresh independent GO, matching bootstrap claim, and successful
implementation-start packet, Prime Builder may perform only these canonical
metadata operations:

1. Create
   `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715`
   using the registered operation and mutation-class vocabulary below.
2. Confirm canonical readback exactly matches the replacement envelope.
3. Revoke
   `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`
   version 2 only after replacement readback succeeds.

The replacement PAUTH must use registered operation vocabulary only. Owner
restrictions outside the registered operation taxonomy remain binding as prose
scope restrictions and implementation-start conditions; they are not encoded as
unregistered `forbidden_operations` tokens.

## Exact Replacement Envelope

```toml
id = "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715"
authorization_name = "Authority Foundations project implementation authorization"
project_id = "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS"
owner_decision_deliberation_id = "DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION"
scope_summary = "Authorize governed Authority Foundations project work under the approved charter. Each protected slice still requires exact project membership, an independent bridge GO, exact target paths, a matching claim, successful implementation-start authorization, executed tests, independent verification, and separately governed finalization. Existing pre-authorization dirty work remains quarantined candidate evidence. Direct harness contact, dispatcher or runtime mutation, credentials, destructive cleanup, unrelated mutation, push, deployment, and release are excluded."
allowed_mutation_classes = ["bridge", "metadata", "governance_evidence", "source", "test", "configuration", "documentation", "runtime_state"]
forbidden_operations = ["credential_lifecycle", "destructive_cleanup", "dispatcher_mutation", "external_system_mutation", "git_commit", "git_history_rewrite", "git_push", "production_deployment", "release"]
included_work_item_ids = []
excluded_work_item_ids = []
included_spec_ids = [
  "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
  "DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001",
  "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
  "GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001",
  "SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001",
  "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "GOV-FILE-BRIDGE-AUTHORITY-001",
  "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
  "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
  "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
  "DCL-PROJECT-DEPENDENCY-ORDERING-001",
  "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
  "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
  "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"
]
excluded_spec_ids = []
expires_at = null
```

## Exact Canonical Commands

The implementation worker must execute the create command only after fresh GO,
bootstrap claim, and implementation-start authorization:

```text
python -m groundtruth_kb.cli projects authorize PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS --id PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715 --owner-decision DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION --name "Authority Foundations project implementation authorization" --scope "Authorize governed Authority Foundations project work under the approved charter. Each protected slice still requires exact project membership, an independent bridge GO, exact target paths, a matching claim, successful implementation-start authorization, executed tests, independent verification, and separately governed finalization. Existing pre-authorization dirty work remains quarantined candidate evidence. Direct harness contact, dispatcher or runtime mutation, credentials, destructive cleanup, unrelated mutation, push, deployment, and release are excluded." --allowed-mutation bridge --allowed-mutation metadata --allowed-mutation governance_evidence --allowed-mutation source --allowed-mutation test --allowed-mutation configuration --allowed-mutation documentation --allowed-mutation runtime_state --forbid credential_lifecycle --forbid destructive_cleanup --forbid dispatcher_mutation --forbid external_system_mutation --forbid git_commit --forbid git_history_rewrite --forbid git_push --forbid production_deployment --forbid release --include-spec DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 --include-spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 --include-spec DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001 --include-spec GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 --include-spec GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 --include-spec SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001 --include-spec GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 --include-spec DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 --include-spec DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 --include-spec DCL-PROJECT-DEPENDENCY-ORDERING-001 --include-spec ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 --include-spec DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 --include-spec GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 --changed-by prime-builder/codex/A --change-reason "Single-use bootstrap remediation authorized by Mike; current-baseline rebind filed at gtkb-authority-foundations-project-authorization-009." --json
```

Only after exact replacement readback passes:

```text
python -m groundtruth_kb.cli projects revoke-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE --changed-by prime-builder/codex/A --change-reason "Revoke the version-2 project-scope Authority Foundations PAUTH only after the owner-authorized replacement was created and read back under the single-use bootstrap remediation." --json
```

## Specification Links

- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - owner
  authorization for the Authority Foundations project envelope and
  quarantine boundary.
- The owner granted a single-use bootstrap remediation exception for this
  exact bridge thread, limited to canonical `groundtruth.db` metadata
  transactions after independent GO, exact claim, and implementation-start
  authorization.
- No new owner decision is required by this revision. It narrows the stored
  envelope to registered vocabulary and rebases the before-state evidence to
  the current canonical row.

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - owner
  project authorization and quarantine boundary.
- `DELIB-202666274` - current normalized project-scope authorization readback
  provenance.
- `bridge/gtkb-authority-foundations-project-authorization-005.md` - previous
  executable proposal, now stale on before-state and vocabulary.
- `bridge/gtkb-authority-foundations-project-authorization-007.md` - Prime
  stop on baseline drift.
- `bridge/gtkb-authority-foundations-project-authorization-008.md` - LO
  NO-GO identifying the missing detector-recognized verification section.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` -
  verified bootstrap lifecycle dependency.

## Specification-Derived Verification

| Specification / requirement | Command evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; numbered bridge chain is authoritative | `python -m groundtruth_kb.cli bridge show gtkb-authority-foundations-project-authorization --json` | PASS - latest status is `NO-GO` at `bridge/gtkb-authority-foundations-project-authorization-008.md`; next Prime response is a `REVISED` version 009. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; current before-state must be exact | `python -m groundtruth_kb.cli projects show-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE --json` | PASS - current row is `active`, version `2`, changed at `2026-07-15T22:22:29+00:00`, with registered allowed mutation classes and forbidden operations. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; replacement must not already exist | `python -m groundtruth_kb.cli projects show-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715 --json` | PASS - command exited nonzero with `Project authorization ... not found.`, so the replacement remains absent. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; bootstrap lifecycle predecessor must be terminal | `python -m groundtruth_kb.cli bridge show gtkb-wi5279-project-authorization-bootstrap-lifecycle --json` | PASS - latest status is `VERIFIED` at `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; this revision must expose detector-recognized spec-derived verification | This `## Specification-Derived Verification` section maps each governing requirement to command evidence and observed result. | PASS - the section is present in the corrected revision and is the direct response to version 008. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; implementation-targeting metadata transaction must cite governing specs | The `## Specification Links` section lists project authorization, operation-time, bridge authority, dependency-ordering, lifecycle, and artifact-governance carriers. | PASS - cited specs include all required project-linkage, authorization, and verification carriers used by this transaction. |

## Pre-Filing Preflight Subsection

This completed revision is filed through the Codex bridge revision helper. The
helper runs credential scanning plus candidate-content applicability and
mandatory clause preflights against the completed body before publishing the
live numbered bridge file. Publication must fail closed if either preflight
returns a blocking result.

After filing, the live verification commands are:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-authority-foundations-project-authorization --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-authority-foundations-project-authorization
```

## Acceptance Criteria

1. Candidate and live applicability preflights pass with no missing required
   specifications.
2. Candidate and live clause preflights exit 0.
3. Loyal Opposition can review this version as the current operative
   `REVISED` response to version 008.
4. No `groundtruth.db` transaction occurs until a later independent GO,
   matching bootstrap claim, and implementation-start packet all succeed.
5. The later implementation report must carry exact before/after readback,
   database integrity, and quarantine-preservation evidence before any
   terminal `VERIFIED` claim.

## Risk And Rollback

Risk is limited to proposal clarity and future metadata-transaction execution.
The live correction is append-only bridge state. If Loyal Opposition finds the
registered vocabulary, owner-decision binding, or before-state evidence still
insufficient, the rollback path is another `NO-GO` with exact findings; no
source, database, dispatcher, TAFE, harness, Git, credential, release, or
deployment state has changed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
