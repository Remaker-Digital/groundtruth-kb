NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5
author_model_version: codex-desktop-2026-07-15
author_model_configuration: Codex Desktop; Prime Builder; danger-full-access; approval-policy-never

# Implementation Report - WI-5235 reissue WI-5217 PAUTH with registered vocabulary

bridge_kind: implementation_report
Document: gtkb-wi5235-wi5217-pauth-registered-vocabulary
Version: 003
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5235-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5235

target_paths: ["groundtruth.db"]
implementation_scope: metadata
requires_verification: true
kb_mutation_in_scope: true
Recommended commit type: fix

## Implementation Claim

Prime Builder implemented the GO-approved WI-5235 governance repair by appending version 2 of `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712` through the canonical `gt projects authorize` writer.

The repair removes the unregistered WI-5217 `forbidden_operations` labels and replaces them with registered operation IDs while preserving the existing included spec set and the substantive no-registry/routing, no role/model change, no worker-lifetime reduction, no direct runtime JSON or lease-file edit, and no unrelated-mutation boundaries in scope text and target-class enforcement.

This report does not claim implementation of the downstream WI-5217 source/test change. It only proves that the WI-5217 bridge thread can now acquire a claim and create an implementation-start packet without the prior `unknown_forbidden_operation` failure.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - registered operation names and mutation classes must be enforced at operation time.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - PAUTH envelope fields must remain bounded and inspectable.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH repair does not bypass the original WI-5217 GO, claim, or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge chain remains the workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - report carries forward the linked governing surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report maps each linked requirement to executed verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item, PAUTH, and target path metadata are carried forward.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the defect remains preserved through WI, PAUTH, bridge, implementation report, and verification flow.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - downstream WI-5217 remains the actual C prompt-transport implementation; this repair only restores its legal start path.
- `SPEC-AUQ-POLICY-ENGINE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-STANDING-BACKLOG-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - proposal-linked governance surfaces preserved by in-root, single-WI, bridge-mediated execution.

## Owner Decisions / Input

- `DELIB-202666173` authorizes the resumed six-harness fleet proof and correction of discovered defects through work item, linked test, PAUTH, bridge GO, implementation, testing, independent verification, and focused commit.
- No new owner decision was required for this PAUTH repair because the implemented version preserves the prior WI-5217 included spec set and therefore did not require the formal approval-packet path that blocked the WI-5232 spec-link amendment.

## Prior Deliberations

- `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-001.md` - Prime Builder proposal.
- `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-002.md` - D-authored Loyal Opposition GO.
- `DELIB-202666173` - owner directive for the fleet proof and defect-correction lifecycle.

## Implementation Evidence

Preconditions before mutation:

- Latest bridge status for `gtkb-wi5235-wi5217-pauth-registered-vocabulary` was `GO` at `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-002.md`.
- Matching Prime Builder work-intent claim acquired for session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, rowid `31182`, acquired at `2026-07-15T01:45:30Z`.
- `python scripts\implementation_authorization.py --project-root . begin --bridge-id gtkb-wi5235-wi5217-pauth-registered-vocabulary --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --no-write` exited 0. Packet hash: `sha256:6a1982c3d10ca9dbd2f0afc2acc28be074f1739cd3c959fd912df0b5b3299fb9`. Target classification for `groundtruth.db`: `metadata`.

Mutation:

- Ran `groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-GOOSE-HARNESS-ADOPTION ... --id PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712 ... --json`.
- Command exited 0 and appended PAUTH rowid `683`, version `2`, status `active`.

Persisted PAUTH version 2:

- `allowed_mutation_classes`: `["source", "test", "bridge"]`
- `forbidden_operations`: `["credential_lifecycle", "destructive_cleanup", "dispatcher_mutation", "external_system_mutation", "git_history_rewrite", "git_push", "production_deployment", "release"]`
- `included_work_item_ids`: `["WI-5217"]`
- `included_spec_ids`: `["SPEC-CENTRALIZED-DISPATCH-SERVICE-001", "GOV-HARNESS-ONBOARDING-CONTRACT-001", "DCL-DISPATCH-ENVELOPE-RULES-001", "ADR-CROSS-HARNESS-PARITY-001"]`
- `change_reason`: `WI-5235: correct WI-5217 PAUTH forbidden_operations from free-form labels to registered operation IDs after work_intent_acquire failed closed with unknown_forbidden_operation; governed by bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-002.md.`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Loaded `config/governance/project-authorization-operation-taxonomy.toml` with Python `tomllib`; verified every active v2 `forbidden_operations` and `allowed_mutation_classes` value resolves to a registered ID. Result: `forbidden_registered: true`, `allowed_classes_registered: true`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `gt projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712 --json` read back version `2`, status `active`, WI `WI-5217`, preserved included spec set, registered forbidden operations, and bounded scope text. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Temporary WI-5217 claim acquired only after PAUTH repair, and `implementation_authorization.py begin --bridge-id gtkb-wi5217-antigravity-prompt-transport --no-write` exited 0 against the original WI-5217 GO without source/test mutation. Temporary WI-5217 claim was released. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This post-implementation report is filed as the next numbered bridge file through `.codex/skills/bridge/helpers/impl_report_bridge.py file`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal links and GO conditions carried forward; report includes explicit spec mapping and does not expand implementation scope. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Executed deterministic readback, taxonomy, claim, and implementation-start checks listed in `Commands Run`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report header carries project authorization, project, work item, target path, and implementation scope. |
| Artifact-oriented governance surfaces | Defect remains tracked as `WI-5235`; implementation did not silently bypass WI/bridge/PAUTH lifecycle. |
| Fleet and dispatcher specs | Downstream WI-5217 start path now reaches source/test target classification under PAUTH v2, proving this repair removes the governance blocker without reconfiguring dispatcher eligibility or runtime state. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-wi5235-wi5217-pauth-registered-vocabulary --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --ttl-seconds 900`
- `python scripts\implementation_authorization.py --project-root . begin --bridge-id gtkb-wi5235-wi5217-pauth-registered-vocabulary --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --no-write`
- `groundtruth-kb\.venv\Scripts\gt.exe projects authorize PROJECT-GTKB-GOOSE-HARNESS-ADOPTION --id PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712 ... --json`
- `groundtruth-kb\.venv\Scripts\gt.exe projects show-authorization PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712 --json`
- `python -c "<tomllib taxonomy/readback validation>"`
- `python scripts\bridge_claim_cli.py claim gtkb-wi5217-antigravity-prompt-transport --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --ttl-seconds 300`
- `python scripts\implementation_authorization.py --project-root . begin --bridge-id gtkb-wi5217-antigravity-prompt-transport --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --no-write`
- `python scripts\bridge_claim_cli.py release gtkb-wi5217-antigravity-prompt-transport --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5235-wi5217-pauth-registered-vocabulary`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5235-wi5217-pauth-registered-vocabulary`

## Observed Results

- WI-5235 implementation-start no-write: exit 0; packet hash `sha256:6a1982c3d10ca9dbd2f0afc2acc28be074f1739cd3c959fd912df0b5b3299fb9`.
- `gt projects authorize`: exit 0; active PAUTH version `2`, rowid `683`.
- Taxonomy validation: `forbidden_registered: true`; `allowed_classes_registered: true`.
- WI-5217 claim acquisition: exit 0; rowid `31183`; no `unknown_forbidden_operation`.
- WI-5217 implementation-start no-write: exit 0; packet hash `sha256:eb7b81cb5715ffb627175c91da6c473e3e6a270eca21870660aa8cd02121be29`; operation-time decision allowed PAUTH version `2`; target classifications were `scripts/dispatcher_runtime.py` as `source` and `platform_tests/scripts/test_dispatcher_runtime.py` as `test`.
- WI-5217 temporary claim release: exit 0.
- Bridge applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0`.

## Files Changed

- `groundtruth.db` - append-only PAUTH version 2 for `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5217-C-PROMPT-TRANSPORT-20260712`.
- `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-003.md` - this implementation report.

Scope note: the repository already has a large unrelated dirty worktree. This report claims only the PAUTH v2 append in `groundtruth.db` and this bridge report for WI-5235.

## Acceptance Criteria Status

- Active WI-5217 PAUTH forbidden operations all resolve against the registered taxonomy: PASS.
- `implementation_authorization.py begin --bridge-id gtkb-wi5217-antigravity-prompt-transport --no-write` no longer fails with `unknown_forbidden_operation` when a valid claim is held: PASS.
- Substantive no-registry/routing, no role/model, no worker-lifetime-reduction, no runtime/lease, and no unrelated-mutation boundaries are preserved in the v2 scope text and by allowed target classes: PASS.
- No WI-5217 source/test implementation was performed under this PAUTH repair: PASS.

## Risk And Rollback

Residual risk is that the registered operation taxonomy still lacks exact one-to-one names for `role_or_model_change`, `worker_lifetime_reduction`, and `direct_runtime_or_lease_edit`. The repair preserves those boundaries through scope text and target-class enforcement rather than inventing unregistered operation names. If Loyal Opposition finds the envelope too broad or too narrow, rollback is an append-only successor PAUTH version; do not delete historical PAUTH rows.

## Recommended Commit Type

- Recommended commit type: `fix`
- Diff-stat justification: this is a governance blocker repair that restores WI-5217 implementation eligibility without adding a new capability surface.

## Loyal Opposition Asks

1. Verify the PAUTH v2 envelope against the registered operation taxonomy and the GO conditions in `bridge/gtkb-wi5235-wi5217-pauth-registered-vocabulary-002.md`.
2. Confirm that WI-5217 claim acquisition and no-write implementation-start now pass without `unknown_forbidden_operation`.
3. Return `VERIFIED` only for the WI-5235 PAUTH repair if satisfied; the downstream WI-5217 source/test implementation remains separate GO work.
