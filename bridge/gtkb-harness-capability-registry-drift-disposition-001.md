NEW
author_identity: prime-builder/Codex
author_harness_id: A
author_session_context_id: S20260616-CODEX-INTERACTIVE
author_model: GPT-5 Codex
author_model_version: 2026-06-16 runtime
author_model_configuration: Codex desktop interactive coding agent

# Defect-Fix Proposal - Harness Capability Registry Drift Disposition

bridge_kind: prime_proposal
Document: gtkb-harness-capability-registry-drift-disposition
Version: 001
Date: 2026-06-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4557

target_paths: ["config/agent-control/harness-capability-registry.toml", "bridge/gtkb-harness-capability-registry-drift-disposition-*.md"]

Defect-fix proposal focused on reproducing, correcting, and verifying protected configuration drift disclosed during S20260616 Codex closeout.

## Claim

`config/agent-control/harness-capability-registry.toml` has an out-of-scope dirty diff produced during Codex skill-adapter regeneration. Because that file is protected config and was not within the approved target paths for `gtkb-no-index-skill-template-doc-cleanout`, Prime Builder must not silently restore or accept the change. This bridge proposes a narrow governed disposition lane: inspect the current diff, decide whether the registry should be restored to HEAD or intentionally retained, make only that bounded config change, and verify that harness registry/capability surfaces remain consistent with WI-4557.

## Requirement Sufficiency

Existing requirements are sufficient for this bounded disposition. `WI-4557` specifically covers reconciliation of registry, routing, capability labels, bridge VERIFIED state, and MemBase status. `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557` authorizes bounded config mutation for WI-4557 while forbidding bridge bypass and unapproved formal artifact mutation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credentials or credential-shaped literals; inspect only registry metadata and bridge files. | Bridge helper credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep implementation inside the declared project root and target paths. | Implementation-start packet, target_paths metadata, and final diff name review. | |
| CQ-COMPLEXITY-001 | Yes | Prefer direct registry disposition over new abstraction, parser, or generator behavior. | Scope review confirms no source/test/tooling changes in this bridge. | |
| CQ-CONSTANTS-001 | Yes | Preserve existing registry key names and generated-source conventions. | Registry diff review and existing validation/generator checks. | |
| CQ-SECURITY-001 | Yes | Avoid cloud, credential, deployment, or hook mutation. | Changed-file review confirms config-only disposition plus bridge report. | |
| CQ-DOCS-001 | Yes | Carry rationale in the bridge proposal and implementation report; no narrative docs are edited. | LO review of this proposal and later implementation report. | |
| CQ-TESTS-001 | Yes | Use existing registry/capability validation checks; add no tests in this slice. | Implementation report records exact focused command output. | |
| CQ-LOGGING-001 | N/A | | | This registry disposition does not alter logging behavior. |
| CQ-VERIFICATION-001 | Yes | Verify the final registry state, no-index invariant, and target-path scope before report. | Registry validation and final diff/stat evidence. | |

## Defect / Reproduction

Fresh `git diff -- config/agent-control/harness-capability-registry.toml` during closeout shows the file remains modified outside the `gtkb-no-index-skill-template-doc-cleanout` approved target path set. The visible delta is primarily blank-line normalization plus a `source_sha256` value change for `.codex/skills/send-review/SKILL.md`. LO recorded the same issue as the first NO-GO finding in `bridge/gtkb-no-index-skill-template-doc-cleanout-006.md`.

Reproduction commands:

```powershell
git diff -- config/agent-control/harness-capability-registry.toml
git diff --stat -- config/agent-control/harness-capability-registry.toml
```

Observed closeout evidence:

- `git diff --stat -- config/agent-control/harness-capability-registry.toml` reports one insertion and thirty-five deletions.
- `bridge/gtkb-no-index-skill-template-doc-cleanout-006.md` identifies the drift as out-of-scope protected config.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/agent-control/harness-capability-registry.toml`, `bridge/gtkb-harness-capability-registry-drift-disposition-*.md`.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - Harness capability state must remain governed and reconcilable across runtime surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected config changes require the bridge authority path before mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The drift crossed from incidental observation into a durable work item because it affects protected governance/config surfaces.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal names the governing specs before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Any implementation report must include verification derived from the linked governance and registry requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The proposal is linked to `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`, `WI-4557`, and its active PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner-authority evidence must remain explicit for implementation authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - In-root placement evidence is required for changed GT-KB artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4557 is the governed backlog authority for this reconciliation work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must self-enforce bridge checks when native hook parity is incomplete.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The observed config drift is routed into an artifact-backed disposition instead of ad hoc cleanup.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The drift triggers lifecycle handling as a config-defect observation.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - The bridge file remains the review and approval mechanism; no `bridge/INDEX.md` dependency is introduced.
- `REQ-HARNESS-REGISTRY-001` - Harness capability registry contents must be intentionally generated, verified, and consistent with actual harness state.

## Prior Deliberations

- `DELIB-20263383` - Owner AUQ authorizing bounded WI-4557 implementation under `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557`.
- `DELIB-20263331` - GT-KB Bridge Implementation Report - WI-4516 OpenRouter/Ollama Bash Bridge Hardening - 005.
- `DELIB-20263077` - Loyal Opposition Verification - Ordered Fallback Routing Revision.
- `DELIB-20260680` - Loyal Opposition Verdict - Ollama Integration Phase 1 Umbrella.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557` - Active project authorization for bounded WI-4557 implementation; owner-decision deliberation `DELIB-20263383`.

## Proposed Scope

Implement only one of the following after GO and implementation-start authorization:

1. Restore `config/agent-control/harness-capability-registry.toml` to the correct governed content if the current diff is incidental adapter-regeneration drift.
2. Keep the current registry content only if inspection proves the `source_sha256` update reflects the correct current generated adapter surface, while explicitly preserving/restoring formatting expected by registry tooling.

The implementation may run existing registry, harness-dispatch, and skill-adapter checks needed to prove the chosen disposition. It must not modify source code, tests, hooks, cloud/deployment files, credentials, bridge index artifacts, or unrelated config.

## Specification-Derived Verification Plan

| Requirement / Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001` | Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-capability-registry-drift-disposition --no-write` before implementation, then acquire a work-intent claim before any live mutation. |
| `REQ-HARNESS-REGISTRY-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run the existing registry/capability validation command identified by local tooling; at minimum verify the final diff is limited to `config/agent-control/harness-capability-registry.toml` and semantically justified. |
| No-index bridge invariant | Run `Test-Path bridge\INDEX.md` and confirm `False`. |
| Scope control | Run `git diff --name-only -- config/agent-control/harness-capability-registry.toml` and `git diff --stat -- config/agent-control/harness-capability-registry.toml` after disposition; report exact output. |
| WI-4557 linkage | Include `WI-4557`, `PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4557`, and `DELIB-20263383` in the implementation report. |

## Acceptance Criteria

- The registry drift is no longer an ungoverned blocker for `gtkb-no-index-skill-template-doc-cleanout`.
- The final state of `config/agent-control/harness-capability-registry.toml` is either restored to HEAD or intentionally retained with evidence that the content is correct.
- The implementation report includes the exact before/after registry diff summary, verification command outputs, and no-index invariant evidence.
- No file outside the declared `target_paths` is modified by this bridge's implementation.

## Risks / Rollback

Risk: blindly reverting the file could discard a legitimate regenerated hash update. Mitigation: inspect the source adapter and registry generation inputs before selecting restore-vs-retain.

Risk: retaining the file could normalize an accidental formatting or hash change. Mitigation: verify with existing registry/generator tooling and report the final diff.

Rollback: restore only `config/agent-control/harness-capability-registry.toml` to the previous governed version if verification shows the change is incidental drift.

## Pre-Filing Preflight

Commands:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-capability-registry-drift-disposition --content-file .gtkb-state\bridge-propose-drafts\gtkb-harness-capability-registry-drift-disposition-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-capability-registry-drift-disposition --content-file .gtkb-state\bridge-propose-drafts\gtkb-harness-capability-registry-drift-disposition-001.md
```

Applicability preflight:

- bridge_document_name: `gtkb-harness-capability-registry-drift-disposition`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-propose-drafts/gtkb-harness-capability-registry-drift-disposition-001.md`
- operative_file: `(none)`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

Clause applicability preflight:

- Bridge id: `gtkb-harness-capability-registry-drift-disposition`
- Operative file: `.gtkb-state\bridge-propose-drafts\gtkb-harness-capability-registry-drift-disposition-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation; exit 5 would indicate a blocking gap, exit 0 passed.

## Files Expected To Change

- `config/agent-control/harness-capability-registry.toml`
- `bridge/gtkb-harness-capability-registry-drift-disposition-*.md`

## Recommended Commit Type

`fix`
