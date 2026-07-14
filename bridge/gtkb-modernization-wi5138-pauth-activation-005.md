REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5474-c61c-71a2-be00-85d5c04faa5a
author_model: GPT-5 Codex
author_model_version: 2026-07-13 runtime
author_model_configuration: Codex desktop interactive Prime Builder session

bridge_kind: governance_advisory
Document: gtkb-modernization-wi5138-pauth-activation
Version: 005
Addresses: bridge/gtkb-modernization-wi5138-pauth-activation-004.md
target_paths: ["groundtruth.db"]
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION
Work Item: WI-5138

# WI-5138 Corrected Bounded PAUTH Activation

## Summary

Activate one exact project authorization required to re-enter the six-file
modernization trust-enforcement slice through the strict bridge lifecycle.
This revision replaces every free-form `forbidden_operations` label with a
registered operation ID and makes every CLI-persisted field explicit. It
authorizes only the single PAUTH row append described below; it does not
authorize source, test, configuration, Git, release, deployment, credential,
cleanup, dispatcher, external-system, or unrelated effects by itself.

## Finding Response

Version 004 corrected the prior non-executable `GO` and required a revision
using only registered operation IDs. The corrected envelope uses exactly:

- `credential_lifecycle`
- `destructive_cleanup`
- `dispatcher_mutation`
- `external_system_mutation`
- `git_commit`
- `git_history_rewrite`
- `git_push`
- `production_deployment`
- `release`

A read-only evaluation against
`config/governance/project-authorization-operation-taxonomy.toml` returns no
unknown operation or mutation class. It permits `implementation_packet_create`,
`implementation_start`, and `protected_mutation` for the PAUTH's allowed target
classes, and returns `forbidden_operation` for each listed excluded operation.

## Requirement Sufficiency

Existing requirements sufficient

The frozen modernization scope, governing specifications, version 004
corrected `NO-GO`, and owner decisions cited below are sufficient for this
bounded activation. No requirement or scope change is proposed.

## Exact Proposed PAUTH Envelope

The following JSON is the complete normative value set for the row. Arrays
must be persisted in the displayed order. `null` and empty arrays must not be
silently replaced with broader values.

```json
{
  "id": "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713",
  "authorization_name": "WI-5138 bounded modernization trust-enforcement authorization",
  "project_id": "PROJECT-GTKB-PLATFORM-MODERNIZATION",
  "owner_decision_deliberation_id": "DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY",
  "scope_summary": "Bounded release-candidate evidence and strict bridge trust closure for WI-5138; source, test, and configuration effects remain limited to exact target paths of separately independently GO-approved proposals, matching claims, and successful implementation-start packets.",
  "allowed_mutation_classes": [
    "bridge",
    "metadata",
    "source",
    "test",
    "configuration",
    "runtime_state",
    "governance_evidence"
  ],
  "forbidden_operations": [
    "credential_lifecycle",
    "destructive_cleanup",
    "dispatcher_mutation",
    "external_system_mutation",
    "git_commit",
    "git_history_rewrite",
    "git_push",
    "production_deployment",
    "release"
  ],
  "included_work_item_ids": [
    "WI-5138"
  ],
  "excluded_work_item_ids": [],
  "included_spec_ids": [
    "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
    "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
    "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
    "GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001",
    "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
    "DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
    "DCL-PROJECT-DEPENDENCY-ORDERING-001",
    "DCL-GIT-BRANCH-BINDING-PROMOTION-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
    "DCL-NO-ACTION-STATUS-SEMANTICS-001"
  ],
  "excluded_spec_ids": [],
  "expires_at": null,
  "status": "active",
  "changed_by": "prime-builder/codex",
  "change_reason": "Corrected WI-5138 bounded modernization PAUTH activation under this thread's fresh independent GO.",
  "supersedes": null,
  "superseded_by": null
}
```

The generated initial row version must be `1`. No `--plan-incomplete` guard is
created by this operation.

## Exact Mutation Command

After a fresh independent `GO`, matching Prime Builder claim, and successful
no-write implementation-start check, execute `gt projects authorize` with the
exact values above. The repeatable `--allowed-mutation`, `--forbid`,
`--include-work-item`, and `--include-spec` arguments must preserve the arrays'
displayed order. Do not add any `--exclude-*`, `--expires-at`, or
`--plan-incomplete` argument.

## Authority Boundaries

The PAUTH is a necessary bound, never sufficient implementation authority.
Every later effect still requires an exact independently `GO`-approved bridge
proposal, matching work-intent claim, successful implementation-start packet,
exact target coverage, post-implementation report, and independent
`VERIFIED` verdict.

Non-taxonomy concepts remain bounded as follows:

- Secret disclosure and credential effects remain outside the owner decision
  and are covered by the forbidden `credential_lifecycle` and
  `external_system_mutation` operations plus credential-safety controls.
- Ref, branch, worktree, and repository-history effects remain outside the
  allowed mutation classes and later exact target paths; the registered Git
  operations are also forbidden.
- Bulk backlog changes, formal-specification mutation, unrelated work, and
  scope expansion remain outside the one included work item, exact scope,
  later target paths, and owner decision.
- Release and production deployment are explicitly forbidden.

The mandatory bridge version, work-intent claim/release, implementation packet,
and post-implementation report are expected control-plane evidence. Within the
PAUTH activation transaction itself, only one new
`project_authorizations` row may be inserted; no pre-existing DoT row may be
updated or deleted.

## Owner Decisions / Input

- `DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL` requires a fresh `GO`
  before the metadata mutation and independent LO verification before closure.
- `DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY` authorizes
  bounded WI-5138 modernization work while excluding the operations listed in
  this corrected envelope.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires a current bounded
  PAUTH before the dependent protected implementation.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the
  closed-vocabulary envelope to be reevaluated at packet, claim, start, and
  protected-effect boundaries.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - defines the persisted envelope
  fields and bounded semantics.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - requires approved linked
  specifications before active authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prevents PAUTH from
  replacing proposal, GO, target, report, or verification controls.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the numbered role-correct chain.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - governs the corrected 002-004
  disposition and this revision.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete
  applicable specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed,
  mapped evidence before activation is `VERIFIED`.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - forbids weakening existing
  controls while enabling the slice.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic
  envelope and evidence evaluation.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - orders this verified PAUTH before the
  dependent six-file proposal.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - keeps Git lifecycle effects outside
  this activation and its dependent source slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the decision, proposal,
  PAUTH, report, and verdict graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit active and verified
  states rather than ambient authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable authority evidence.

## Specification-Derived Verification Plan

| Requirement | Objective verification |
|---|---|
| Registered operation vocabulary | Load the canonical taxonomy and require every allowed class and forbidden operation in the JSON block to normalize exactly, with no unknown result. |
| Intended allow/deny behavior | Evaluate the candidate envelope for `implementation_packet_create`, `implementation_start`, and `protected_mutation` on `groundtruth.db`; require `allowed`. Evaluate every forbidden operation; require `forbidden_operation`. |
| Exact persisted envelope | Run `gt projects show-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713 --json` and compare every persisted field and ordered array to the normative JSON. |
| One-row transaction | Capture read-only before/after snapshots of the PAUTH table and related project, work-item, specification, and deliberation records; require exactly one new version-1 PAUTH row and no update/deletion of a pre-existing DoT row. |
| Bridge and start ordering | Require the fresh `GO`, matching claim, and `python scripts/implementation_authorization.py begin --bridge-id gtkb-modernization-wi5138-pauth-activation --no-write` to succeed before the CLI mutation. |
| Dependent consumability | After this activation reaches `VERIFIED`, require the later trust-enforcement proposal's no-write start to evaluate the PAUTH successfully before any of its six targets change. |
| Independent completion | File a post-implementation report containing exact observed output and obtain independent LO `VERIFIED`; `GO` alone is not completion. |

## Acceptance Criteria

1. The exact PAUTH ID exists once at version 1, is active, and includes only
   `WI-5138`.
2. Every persisted field and ordered array exactly matches the normative JSON.
3. All allowed classes and forbidden operations are registered, and the
   candidate evaluator produces the intended allow/deny outcomes.
4. The activation transaction inserts one PAUTH row and does not update or
   delete a pre-existing DoT row.
5. The PAUTH cannot authorize any later effect without the narrower bridge,
   claim, start, exact-target, report, and independent-verification chain.
6. This activation is not complete until its report receives independent LO
   `VERIFIED`.

## Risk And Rollback

The principal risk is treating project authorization as blanket source or Git
authority. The closed operation vocabulary, omitted repository-metadata class,
one included work item, exact later target paths, and bridge lifecycle bound
that risk. If any persisted field differs, stop dependent work and use a
separately `GO`-approved append-only successor to revoke or supersede the
authorization; do not delete or rewrite history.

## Prior Deliberations

- Versions 001-002 contain the rejected free-form operation vocabulary.
- Version 003 rejected that `GO`; version 004 independently corrected it to
  `NO-GO` and prescribed the nine registered operation IDs used here.
- `DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL`
- `DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY`

## Pre-Filing Preflight

- Applicability preflight must pass against these exact bytes with no missing
  required or advisory specifications.
- Mandatory ADR/DCL clause preflight must exit zero with no blocking gap.
