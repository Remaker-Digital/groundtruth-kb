NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; resumed fleet goal

bridge_kind: governance_advisory
Document: gtkb-wi5232-wi5216-pauth-registered-vocabulary
Version: 001
Date: 2026-07-14 UTC

Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5232
target_paths: ["groundtruth.db"]

# Implementation Proposal - Reissue WI-5216 PAUTH with registered operation vocabulary

## Summary

WI-5216 has an independent `GO` at
`bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md`, but Prime
Builder cannot legally acquire the implementation claim. The live
`work_intent_acquire` gate fails closed before creating a claim because the
active PAUTH
`PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712`
contains unregistered `forbidden_operations` labels:

- `dispatcher_or_routing_change`
- `raw_guard_weakening`
- `turn_or_timeout_reduction`
- `direct_runtime_or_lease_edit`
- `unrelated_mutation`

This is the same non-executable-envelope shape corrected in the verified
WI-5138 PAUTH activation chain. This proposal appends a version-2 correction to
the same PAUTH ID using only registered operation IDs, preserving the PAUTH ID
already cited by the WI-5216 proposal so the existing `GO` can become
executable without revising WI-5216's approved implementation scope.

## Claim

Prime Builder proposes a bounded PAUTH vocabulary repair only. It does not
implement WI-5216 source changes, does not edit dispatcher/routing/runtime/lease
state, does not weaken raw guards, does not reduce runtime allowances, and does
not authorize unrelated work.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
requires operation names and mutation classes to come from a governed, versioned
taxonomy, and states that an unregistered operation denies. WI-5232 / TEST-11386
capture the observed failure and expected recovery.

## In-Root Placement Evidence

The only implementation target is `groundtruth.db` under `E:\GT-KB`. No source,
test, dispatcher configuration, runtime JSON, lease, credential, release,
deployment, Git remote, or external-system target is in scope for this PAUTH
repair.

## Exact Proposed PAUTH Version-2 Envelope

Append a new version for the existing authorization ID with the exact values
below. Arrays must be persisted in the displayed order.

```json
{
  "id": "PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712",
  "authorization_name": "WI-5216 provider verdict denial-loop recovery",
  "project_id": "PROJECT-GTKB-GOOSE-HARNESS-ADOPTION",
  "owner_decision_deliberation_id": "DELIB-202666173",
  "scope_summary": "Authorize the existing WI-5216 bridge cycle and, only after the existing independent GO plus matching work-intent claim and implementation-start packet, bounded source/test/bridge work in the approved five target paths to recover D/F provider verdict-publication loops through PublishBridgeVerdict. Preserve dispatcher/routing eligibility, raw Write/Edit/Bash guard strength, all 600/900/3600/29400/29700 allowances, runtime JSON and lease files, credentials, deployment, Git remote/history actions, and unrelated dirty worktree content.",
  "allowed_mutation_classes": [
    "source",
    "test",
    "bridge"
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
    "WI-5216"
  ],
  "excluded_work_item_ids": [],
  "included_spec_ids": [
    "GOV-HARNESS-ONBOARDING-CONTRACT-001",
    "ADR-CROSS-HARNESS-PARITY-001",
    "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001",
    "ADR-CLOUD-HARNESS-TEMPLATE-001",
    "DCL-OLLAMA-TOOL-PARITY-GATE-001",
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "GOV-DOCUMENT-AUTHOR-PROVENANCE-001",
    "DCL-DISPATCH-ENVELOPE-RULES-001",
    "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
    "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
    "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001"
  ],
  "excluded_spec_ids": [],
  "expires_at": null,
  "status": "active",
  "changed_by": "prime-builder/codex/A",
  "change_reason": "WI-5232: correct WI-5216 PAUTH forbidden_operations from free-form labels to registered operation IDs after work_intent_acquire failed closed with unknown_forbidden_operation.",
  "supersedes": null,
  "superseded_by": null
}
```

## Exact Mutation Command

After fresh independent `GO`, matching Prime Builder claim, and a successful
no-write implementation-start check for this thread, execute:

```powershell
groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-GOOSE-HARNESS-ADOPTION --id PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712 --owner-decision DELIB-202666173 --name "WI-5216 provider verdict denial-loop recovery" --scope "Authorize the existing WI-5216 bridge cycle and, only after the existing independent GO plus matching work-intent claim and implementation-start packet, bounded source/test/bridge work in the approved five target paths to recover D/F provider verdict-publication loops through PublishBridgeVerdict. Preserve dispatcher/routing eligibility, raw Write/Edit/Bash guard strength, all 600/900/3600/29400/29700 allowances, runtime JSON and lease files, credentials, deployment, Git remote/history actions, and unrelated dirty worktree content." --allowed-mutation source --allowed-mutation test --allowed-mutation bridge --forbid credential_lifecycle --forbid destructive_cleanup --forbid dispatcher_mutation --forbid external_system_mutation --forbid git_commit --forbid git_history_rewrite --forbid git_push --forbid production_deployment --forbid release --include-work-item WI-5216 --include-spec GOV-HARNESS-ONBOARDING-CONTRACT-001 --include-spec ADR-CROSS-HARNESS-PARITY-001 --include-spec DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 --include-spec ADR-CLOUD-HARNESS-TEMPLATE-001 --include-spec DCL-OLLAMA-TOOL-PARITY-GATE-001 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec GOV-DOCUMENT-AUTHOR-PROVENANCE-001 --include-spec DCL-DISPATCH-ENVELOPE-RULES-001 --include-spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 --include-spec DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 --include-spec PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 --include-spec DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 --include-spec DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 --changed-by prime-builder/codex/A --change-reason "WI-5232: correct WI-5216 PAUTH forbidden_operations from free-form labels to registered operation IDs after work_intent_acquire failed closed with unknown_forbidden_operation." --json
```

Do not add `--exclude-*`, `--expires-at`, or `--plan-incomplete` arguments.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - unregistered
  operation names deny at every operation gate; denied work-intent acquisition
  must create no claim.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - governs the PAUTH envelope fields
  being versioned.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - this PAUTH version does not
  bypass WI-5216's existing GO, claim, implementation-start, report, or
  independent verification gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this correction must flow through a numbered
  bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links
  the relevant governing specifications before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must execute the mapped PAUTH verification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - WI-5216 remains necessary for genuine
  governed D/F proof.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
  - the repair preserves D/F parity goals without changing routing or
  eligibility.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` and `DCL-OLLAMA-TOOL-PARITY-GATE-001` - the
  downstream WI-5216 implementation remains limited to the approved F/D harness
  surfaces.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - downstream publisher recovery must
  preserve dispatcher session and provider model provenance.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - the PAUTH correction preserves all runtime
  allowances.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, WI/test, PAUTH repair,
  implementation report, and verification remain linked as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the failed implementation gate
  triggers a governed correction rather than an informal bypass.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proof-blocking defect is
  preserved as a work item with a linked test and bridge lifecycle.

## Prior Deliberations

- `DELIB-202666173` authorizes correction of every defect discovered during the
  genuine A/B/C/D/F/H fleet proof.
- `DELIB-202665962` records the verified WI-5138 PAUTH activation chain and the
  specific precedent that free-form forbidden-operation labels make a PAUTH
  non-executable until replaced with registered operation IDs.
- `bridge/gtkb-wi5216-provider-verdict-denial-loop-recovery-002.md` is the
  existing independent GO that this PAUTH repair unblocks.
- `WI-5232` / `TEST-11386` capture the observed gate failure and expected
  recovery.

## Owner Decisions / Input

- `DELIB-202666173` is the owner directive for correcting proof-blocking
  defects found during the fleet goal.
- No new owner approval is requested in this proposal; the change narrows an
  already-active PAUTH into the registered operation vocabulary required by the
  current governance gate.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Registered vocabulary | Load `config/governance/project-authorization-operation-taxonomy.toml` and verify every proposed `allowed_mutation_classes` and `forbidden_operations` value normalizes to a registered ID. |
| Exact persisted PAUTH | Run `gt projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5216-VERDICT-LOOP-RECOVERY-20260712 --json` and compare ID, version, active status, included work item, ordered allowed classes, ordered forbidden operations, included specs, owner decision, scope, and change reason. |
| Work-intent unblock | Run `python scripts/bridge_claim_cli.py claim gtkb-wi5216-provider-verdict-denial-loop-recovery --session-id <current-session> --ttl-seconds 300` and require success with no `unknown_forbidden_operation`; release the claim immediately after this verification if WI-5216 implementation is not starting in the same transaction. |
| Side-effect boundary | Before/after snapshots show this implementation only appends the PAUTH version and creates the implementation report; no source, test, dispatcher runtime JSON, lease, credential, deployment, or unrelated Git state changes occur. |
| No bridge bypass | WI-5216 still requires its existing latest `GO`, matching claim, implementation-start packet, source/test changes, implementation report, and independent LO verification before completion. |

## Acceptance Criteria

- The active WI-5216 PAUTH no longer contains any unknown
  `forbidden_operations` value.
- The PAUTH ID cited by the WI-5216 GO-approved proposal remains the active ID,
  so no WI-5216 proposal revision is required solely for ID mismatch.
- A matching WI-5216 work-intent claim succeeds where it previously failed with
  `unknown_forbidden_operation`.
- The correction does not authorize dispatcher/routing edits, runtime JSON or
  lease edits, credential lifecycle, Git push/history, release/deployment, raw
  guard weakening, timeout reduction, or unrelated work.
- The correction is independently VERIFIED before WI-5216 protected source/test
  implementation resumes.

## Risk And Rollback

The main risk is encoding a broader PAUTH than the original intent. The proposal
limits that risk by retaining the same PAUTH ID, one included work item, the
same allowed mutation classes, exact registered forbidden operation IDs, and
scope text that preserves the original no-routing/no-guard-weakening/no-timeout
reduction/no-runtime-lease/no-unrelated-work boundaries. If the persisted
version differs from the normative envelope, stop WI-5216 implementation and use
a separately GO-approved append-only successor to supersede or correct the
authorization; do not delete historical rows.

## Recommended Commit Type

`fix`

## Pre-Filing Preflight

Applicability preflight against the draft content:

- packet_hash: `sha256:78256eb150e1715b26672da69c7456e4668f8504d044e481f31247def20cf50f`
- bridge_document_name: `gtkb-wi5232-wi5216-pauth-registered-vocabulary`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-propose-drafts/gtkb-wi5232-wi5216-pauth-registered-vocabulary-body.md`
- operative_file: `(none)`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Mandatory ADR/DCL clause preflight against the draft content:

- Bridge id: `gtkb-wi5232-wi5216-pauth-registered-vocabulary`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0
